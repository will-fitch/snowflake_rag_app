from typing import List
import streamlit as st
from snowflake.snowpark.types import StructType, StructField, StringType, BinaryType

def get_session():
    session = st.connection("snowflake").session()
    return session

def save_uploaded_file(file_name: str, file_content: bytes) -> str:
    session = get_session()
    # Delete if exists
    session.sql(f"DELETE FROM BASIC_RAG_DB.PUBLIC.UPLOADED_FILES WHERE filename = '{file_name}'").collect()
    # Explicitly define schema
    schema = StructType([
        StructField("FILENAME", StringType()),
        StructField("FILE_CONTENT", BinaryType())
    ])
    df = session.create_dataframe([[file_name, bytes(file_content)]], schema=["FILENAME", "FILE_CONTENT"])
    df.write.insert_into("BASIC_RAG_DB.PUBLIC.UPLOADED_FILES")

def load_file_content(filename: str) -> bytes:
    """Load the content of a file from the Snowflake uploaded_files table."""
    session = get_session()
    result = session.table("BASIC_RAG_DB.PUBLIC.UPLOADED_FILES").filter(f"filename = '{filename}'").select("file_content").collect()
    if not result:
        raise FileNotFoundError(f"{filename} not found in database")
    return bytes(result[0]["FILE_CONTENT"])

def list_uploaded_files() -> List[str]:
    """List all uploaded filenames in the Snowflake uploaded_files table."""
    session = get_session()
    results = session.table("BASIC_RAG_DB.PUBLIC.UPLOADED_FILES").select("filename").collect()
    return [row["FILENAME"] for row in results]

def load_all_uploaded_files() -> List[str]:
    """Return a list of all file contents for all uploaded files."""
    files = list_uploaded_files()
    return [load_file_content(f) for f in files]

def delete_uploaded_file(filename: str) -> None:
    """Delete a file from the Snowflake uploaded_files table."""
    session = get_session()
    # Delete if exists
    session.sql(f"DELETE FROM BASIC_RAG_DB.PUBLIC.UPLOADED_FILES WHERE filename = '{filename}'").collect()

def filename_exists(filename: str) -> bool:
    """Check if a file exists in the Snowflake uploaded_files table."""
    session = get_session()
    result = session.table("BASIC_RAG_DB.PUBLIC.UPLOADED_FILES").filter(f"filename = '{filename}'").select("filename").collect()
    return len(result) > 0

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file given as bytes."""
    return "pdf reading not implemented"
