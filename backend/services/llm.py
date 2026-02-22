import httpx
import re
from core.config import settings
from core.logger import setup_logger
from core.errors import LLMError

logger = setup_logger("cad_copilot.llm")

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.retries = settings.LLM_RETRIES

    def _extract_python_code(self, response_text: str) -> str:
        """Extracts python code from LLM response. Handles markdown fences and raw code."""
        # Try to find all code blocks (with or without language tag)
        blocks = re.findall(r"```(?:python|py)?\s*\n?(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
        
        if blocks:
            # Pick the longest block — most likely the actual code
            code = max(blocks, key=len).strip()
        else:
            # No markdown fences — treat entire response as code
            code = response_text.strip()
        
        # Remove any stray markdown fences that survived
        code = code.replace("```python", "").replace("```py", "").replace("```", "").strip()
        
        # Validate that `final_shape` assignment exists
        if "final_shape" not in code:
            logger.warning("LLM output missing 'final_shape' — appending fallback")
            # Try to find the last variable assignment and alias it
            lines = code.strip().split("\n")
            last_line = lines[-1].strip()
            if "=" in last_line and not last_line.startswith("#"):
                var_name = last_line.split("=")[0].strip()
                code += f"\nfinal_shape = {var_name}"
            else:
                code += "\n# WARNING: No final_shape found in LLM output"
        
        return code

    async def check_health(self) -> bool:
        try:
             async with httpx.AsyncClient(timeout=5) as client:
                 res = await client.get(f"{self.base_url}")
                 return res.status_code == 200
        except Exception:
             return False

    async def generate_code(self, prompt: str, system_prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\nUser Request: {prompt}\n\nPlease output ONLY valid FreeCAD Python code.",
            "stream": False,
            "options": {
                "temperature": 0.1 # Keep it deterministic for code
            }
        }

        for attempt in range(self.retries + 1):
            try:
                logger.info(f"Contacting LLM '{self.model}' (Attempt {attempt + 1}/{self.retries + 1})")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                     response = await client.post(f"{self.base_url}/api/generate", json=payload)
                     response.raise_for_status()
                     data = response.json()
                     raw_response = data.get("response", "")
                     return self._extract_python_code(raw_response)
            
            except httpx.ReadTimeout:
                logger.warning(f"LLM request timed out (Attempt {attempt + 1})")
                if attempt == self.retries:
                    raise LLMError(f"LLM request timed out after {self.retries + 1} attempts.")
            except httpx.HTTPError as e:
                logger.warning(f"LLM HTTP error: {e} (Attempt {attempt + 1})")
                if attempt == self.retries:
                    raise LLMError(f"Failed to communicate with local LLM.", details=str(e))
            except Exception as e:
                logger.error(f"Unexpected LLM error: {e}", exc_info=True)
                raise LLMError("Unexpected error during LLM generation.", details=str(e))

llm_service = OllamaService()
