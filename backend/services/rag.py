import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Optional
from core.config import settings
from core.logger import setup_logger

logger = setup_logger("cad_copilot.rag")

class RAGService:
    def __init__(self):
        self.enabled = settings.ENABLE_RAG
        self.collection_name = "freecad_docs"
        self._client = None
        self._collection = None
        # We use a lightweight local embedding model
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.initialized = False

    def initialize(self):
        """Lazy load the ChromaDB index to avoid blocking startup."""
        if not self.enabled:
            logger.info("RAG is disabled in configuration.")
            return

        try:
            db_path = os.path.abspath(settings.CHROMA_DB_DIR)
            os.makedirs(db_path, exist_ok=True)
            
            logger.info(f"Connecting to ChromaDB at {db_path}")
            self._client = chromadb.PersistentClient(path=db_path)
            
            # Create or get collection. Distance l2 is fine for standard embeddings.
            self._collection = self._client.get_or_create_collection(
                 name=self.collection_name, 
                 embedding_function=self.embedding_fn
            )
            
            count = self._collection.count()
            logger.info(f"RAG initialized successfully. Loaded {count} documents.")
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize RAG index: {e}", exc_info=True)
            self.enabled = False # Disable gracefully if DB is corrupt or missing
            self.initialized = False

    def check_health(self) -> dict:
        status = {
            "enabled": self.enabled,
            "initialized": self.initialized,
            "document_count": 0,
            "error": None
        }
        if self.initialized and self._collection:
            try:
                status["document_count"] = self._collection.count()
            except Exception as e:
                status["error"] = str(e)
                status["initialized"] = False
        return status

    def retrieve_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieves relevant FreeCAD examples or API snippets.
        Fails gracefully by returning an empty string.
        """
        if not self.enabled or not self.initialized or not self._collection:
             return ""
             
        try:
            count = self._collection.count()
            if count == 0:
                 return ""

            actual_n = min(n_results, count)
            results = self._collection.query(
                query_texts=[query],
                n_results=actual_n
            )

            if results and results['documents'] and results['documents'][0]:
                 docs = results['documents'][0]
                 formatted_context = "\n\n---\nRELEVANT FREECAD DOCUMENTATION/EXAMPLES:\n"
                 formatted_context += "\n\n".join(docs)
                 formatted_context += "\n---\n"
                 return formatted_context
            return ""
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}. Continuing without context.")
            return ""

# Singleton instance
rag_service = RAGService()
