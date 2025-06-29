# from dotenv import load_dotenv
import streamlit as st
import os
# import getpass

os.environ["OPENAI_API_KEY"] = "temp"

# session = st.connection("snowflake").session()
# api_key = session.sql("SHOW SECRETS IN ").collect()
# os.environ["OPENAI_API_KEY"] = api_key

# load_dotenv()
# if not os.environ.get("OPENAI_API_KEY"):
#   os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from vector_store import SnowflakeVectorStore

# from langchain.chat_models import init_chat_model
# from langchain_core.messages import HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
# from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

@dataclass
class RAGResponse:
    """Response from RAG model with content and source citations."""
    content: str
    sources: List[Dict[str, Any]]
    query: str

@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any]

class RAGModel:
    """
    A Retrieval-Augmented Generation (RAG) model that combines vector search with LLM responses.
    
    This class provides functionality to:
    - Store and search document chunks in a vector database
    - Generate responses using retrieved context and an LLM
    - Add new content with automatic chunking
    - Provide source citations for responses
    """

    def __init__(self) -> None:
        self.content = [("default_content", "default_filename")]
        
        self.vector_db = SnowflakeVectorStore()

    def query(self, query: str) -> RAGResponse:

        relevant_documents = self.vector_db.similarity_search(query)

        if(len(relevant_documents) == 0):
            return RAGResponse(
                content="No relevant information found. Please try again with different query.",
                sources=[],
                query=query
            )
        
        return RAGResponse(
            content="\n".join([document.page_content for document in relevant_documents]),
            sources=[],
            query=query
        )

    def _add_chunks(self, document_strings, filename):
        documents = []
        for content in document_strings:
            metadata = {"filename": filename}
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
        return self.vector_db.add_documents(documents)

    def add_content(self, file_content: str, filename: str = "unknown file", chunk_size: int = 500, chunk_overlap: int = 10) -> int:
        try:
            # Split the text into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            chunks = splitter.split_text(file_content)
            
            # Add chunks with source metadata
            return self._add_chunks(chunks, filename)
            
            # return len(chunks)  # Return number of chunks added
            
        except Exception as e:
            raise Exception(f"Error processing file content: {str(e)}")

    def delete_by_filename(self, filename: str) -> None:
        self.vector_db.delete_by_filename(filename)
