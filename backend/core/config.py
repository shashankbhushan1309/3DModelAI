import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # API / Server
    API_PORT: int = Field(default=8000, description="Port for the FastAPI backend")
    API_HOST: str = Field(default="127.0.0.1", description="Host for the FastAPI backend")

    # LLM & Ollama
    OLLAMA_BASE_URL: str = Field(default="http://127.0.0.1:11434", description="Base URL for local Ollama")
    LLM_MODEL: str = Field(default="mistral", description="Ollama model to use for generation")
    LLM_TIMEOUT: int = Field(default=180, description="Timeout in seconds for LLM requests")
    LLM_RETRIES: int = Field(default=2, description="Number of retries for transient LLM errors")

    # OpenAI Fallback (used when local Ollama fails)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key for GPT-4o fallback")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model to use as fallback")

    # FreeCAD
    FREECAD_PATH: Optional[str] = Field(default=None, description="Path to FreeCADCmd executable")
    FREECAD_TIMEOUT: int = Field(default=30, description="Timeout in seconds for FreeCAD execution")
    OUTPUT_DIR: str = Field(default="outputs", description="Directory to store generated scripts and STLs")
    MAX_SCRIPT_LENGTH: int = Field(default=2000, description="Maximum allowed lines for generated Python script")

    # RAG
    ENABLE_RAG: bool = Field(default=True, description="Enable RAG context injection")
    CHROMA_DB_DIR: str = Field(default="./chroma_db", description="Directory for ChromaDB persistence")
    RAG_DOCS_DIR: str = Field(default="./rag_docs", description="Directory containing source markdown docs for RAG")

    # Security / Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure output directory exists (resolve relative to backend/ directory)
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
settings.OUTPUT_DIR = os.path.join(_backend_dir, settings.OUTPUT_DIR)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
