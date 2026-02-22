from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import contextlib
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from core.config import settings
from core.logger import setup_logger
from core.errors import CopilotException, copilot_exception_handler, generic_exception_handler
from api.routes import router
from services.rag import rag_service

logger = setup_logger("cad_copilot.main")

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CAD Copilot Backend...")
    rag_service.initialize()
    yield
    logger.info("Shutting down CAD Copilot Backend...")

app = FastAPI(title="AI CAD Copilot API", version="1.0.0", lifespan=lifespan)

# Strict CORS for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(CopilotException, copilot_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(router, prefix="/api")

# Serve output files securely
# Ensure the directory exists before mounting
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        reload_excludes=["outputs/*", "chroma_db/*", "*.stl", "*.pyc"],
    )
