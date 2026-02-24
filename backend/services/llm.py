import httpx
import re
from core.config import settings
from core.logger import setup_logger
from core.errors import LLMError

logger = setup_logger("cad_copilot.llm")


def _extract_python_code(response_text: str) -> str:
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


class OllamaService:
    """Primary LLM service using local Ollama."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.retries = settings.LLM_RETRIES

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
                "temperature": 0.1
            }
        }

        for attempt in range(self.retries + 1):
            try:
                logger.info(f"Contacting local LLM '{self.model}' (Attempt {attempt + 1}/{self.retries + 1})")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                     response = await client.post(f"{self.base_url}/api/generate", json=payload)
                     response.raise_for_status()
                     data = response.json()
                     raw_response = data.get("response", "")
                     return _extract_python_code(raw_response)
            
            except httpx.ReadTimeout:
                logger.warning(f"Local LLM request timed out (Attempt {attempt + 1})")
                if attempt == self.retries:
                    raise LLMError(f"Local LLM request timed out after {self.retries + 1} attempts.")
            except httpx.HTTPError as e:
                logger.warning(f"Local LLM HTTP error: {e} (Attempt {attempt + 1})")
                if attempt == self.retries:
                    raise LLMError(f"Failed to communicate with local LLM.", details=str(e))
            except Exception as e:
                logger.error(f"Unexpected local LLM error: {e}", exc_info=True)
                raise LLMError("Unexpected error during local LLM generation.", details=str(e))


class OpenAIFallbackService:
    """Fallback LLM service using OpenAI GPT-4o API."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.available = bool(self.api_key)

    async def generate_code(self, prompt: str, system_prompt: str) -> str:
        if not self.available:
            raise LLMError("OpenAI fallback is not configured. Set OPENAI_API_KEY in .env")

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise LLMError("openai package is not installed. Run: pip install openai")

        logger.info(f"Falling back to OpenAI '{self.model}'...")

        try:
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{prompt}\n\nPlease output ONLY valid FreeCAD Python code."}
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            raw_response = response.choices[0].message.content or ""
            logger.info(f"OpenAI response received ({len(raw_response)} chars)")
            return _extract_python_code(raw_response)

        except Exception as e:
            logger.error(f"OpenAI fallback also failed: {e}", exc_info=True)
            raise LLMError(f"OpenAI fallback failed: {str(e)}", details=str(e))


class LLMServiceWithFallback:
    """
    Orchestrates LLM calls: tries local Ollama first, then falls back to OpenAI GPT-4o
    if the local model fails. If OpenAI is not configured, the local error is re-raised.
    """

    def __init__(self):
        self.primary = OllamaService()
        self.fallback = OpenAIFallbackService()

    async def check_health(self) -> bool:
        return await self.primary.check_health()

    async def generate_code(self, prompt: str, system_prompt: str) -> str:
        try:
            # Try local Ollama first
            return await self.primary.generate_code(prompt, system_prompt)
        except LLMError as local_err:
            # If OpenAI fallback is configured, try it
            if self.fallback.available:
                logger.warning(f"Local LLM failed ({local_err.message}). Attempting OpenAI fallback...")
                return await self.fallback.generate_code(prompt, system_prompt)
            else:
                # No fallback configured — re-raise the original error
                logger.error("Local LLM failed and no OpenAI fallback is configured.")
                raise


# Single service instance used by routes.py
llm_service = LLMServiceWithFallback()
