from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str = Field(..., max_length=1000, description="The natural language CAD instruction.")

class RefineRequest(BaseModel):
    original_code: str = Field(..., description="The previous Python code.")
    instruction: str = Field(..., max_length=1000, description="The natural language refinement instruction.")

class GenerationResponse(BaseModel):
    status: str = Field(default="success")
    stl_url: str = Field(description="URL to download the generated STL file")
    code: str = Field(description="The validated Python script used to generate the shape")

class SystemStatusResponse(BaseModel):
    status: str = Field(description="Overall system status (ok/error/warning)")
    ollama_reachable: bool
    freecad_available: bool
    freecad_executable: Optional[str]
    rag_status: dict
    output_dir_writable: bool
