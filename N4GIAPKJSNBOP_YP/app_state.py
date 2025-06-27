from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import file_storage

from rag_model import RAGModel, RAGResponse

class AppState:
    """
    Manages the application state and business logic for the RAG chatbot.
    Separates business logic from UI concerns.
    """
    
    def __init__(self):
        self.rag_model: RAGModel = RAGModel()
        
    def query_model(self, query: str) -> RAGResponse:
        """Query the RAG model and return response with sources."""
        return self.rag_model.query(query)

    # File storage logic
    def load_file_content(self, filename: str) -> bytes:
        return file_storage.load_file_content(filename)

    def list_uploaded_files(self):
        return file_storage.list_uploaded_files()

    def delete_file(self, filename: str) -> None:
        file_storage.delete_uploaded_file(filename)
        self.rag_model.delete_by_filename(filename)

    def upload_file(self, file_name: str, file_content: bytes, chunk_size: int = 500, chunk_overlap: int = 50) -> int:
        """Save a file and add its content to the RAG model."""

        file_storage.save_uploaded_file(file_name, file_content)

        file_bytes = file_content.tobytes()
        
        return self.rag_model.add_content(file_bytes.decode("utf-8"), file_name, chunk_size, chunk_overlap)