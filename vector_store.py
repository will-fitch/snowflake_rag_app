import streamlit as st
import os

tiktoken_cache_dir = "tiktoken_cache"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

# validate
assert os.path.exists(os.path.join(tiktoken_cache_dir,"9b5ad71b2ce5302211f9c61530b329a4922fc6a4"))


from snowflake.snowpark.types import StructType, StructField, StringType, VectorType, ArrayType, IntegerType

from langchain_openai import OpenAIEmbeddings
from typing import List

import uuid

class SnowflakeVectorStore:

    def __init__(self, table_name: str = "BASIC_RAG_DB.PUBLIC.DOCUMENT_CHUNKS"):
        self.table_name = table_name
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vector_dimensions = 3072 # OpenAI text-embedding-3-large dimension is 3072

        self.schema = StructType([
            StructField("CHUNK_ID", StringType()),
            StructField("FILENAME", StringType()),
            StructField("CHUNK_TEXT", StringType()),
            StructField("CHUNK_INDEX", IntegerType()),
            StructField("EMBEDDING", ArrayType())
        ])

    def _get_session(self):
        return st.connection("snowflake").session()

    def add_documents(self, documents):
        if not documents:
            return 0

        try:
            session = self._get_session()

            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]

            embeddings = self.embeddings.embed_documents(texts)

            # data = []
            # for i, (doc, metadata, embedding) in enumerate(zip(documents, metadatas, embeddings)):
            #     doc_id = str(uuid.uuid4())

            #     metadata_json = str(metadata) if metadata else "{}"

            #     data.append((
            #         doc_id,
            #         metadata.get('filename', 'unknown'),
            #         doc.page_content,
            #         metadata.get('chunk_index', i),
            #         embedding,
            #         # metadata_json
            #     ))

            # df.session.create_dataframe(data, schema=self.schema)
            # df.write.insert_into(self.table_name)

            # return len(documents)
            return 0

        except Exception as e:
            raise e

    def similarity_search(self, query, k: int = 4):
        try:
            session = self._get_session()

            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Convert embedding to Snowflake vector format
            embedding_str = ','.join(map(str, query_embedding))

            # Build query
            query_sql = f"""
            SELECT 
                CHUNK_TEXT,
                FILENAME,
                CHUNK_INDEX,
                METADATA,
                VECTOR_COSINE_SIMILARITY(EMBEDDING, TO_VECTOR('[{embedding_str}]')) as similarity_score
            FROM {self.table_name}
            ORDER BY similarity_score DESC
            LIMIT {k}
            """
            
            results = session.sql(query_sql).collect()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "content": row["CHUNK_TEXT"],
                    "metadata": {
                        "filename": row["FILENAME"],
                        "chunk_index": row["CHUNK_INDEX"],
                        "raw_metadata": row["METADATA"]
                    },
                    "score": row["SIMILARITY_SCORE"]
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error in similarity search: {str(e)}")
            return []

    def delete_by_filename(self, filename: str):
        try:
            session = self._get_session()
            
            # Get count before deletion
            count_sql = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE FILENAME = '{filename}'"
            count_result = session.sql(count_sql).collect()
            count_before = count_result[0]["COUNT"]
            
            # Delete chunks
            delete_sql = f"DELETE FROM {self.table_name} WHERE FILENAME = '{filename}'"
            session.sql(delete_sql).collect()
            
            print(f"✅ Deleted {count_before} chunks for filename: {filename}")
            return count_before
            
        except Exception as e:
            print(f"❌ Error deleting by filename: {str(e)}")
            return 0

    def reset_collection(self):
        try:
            session = self._get_session()
            
            # Get count before deletion
            count_result = session.sql(f"SELECT COUNT(*) as count FROM {self.table_name}").collect()
            count_before = count_result[0]["COUNT"]
            
            # Delete all data
            session.sql(f"DELETE FROM {self.table_name}").collect()
            
            print(f"✅ Reset collection: deleted {count_before} chunks")
            return count_before
            
        except Exception as e:
            print(f"❌ Error resetting collection: {str(e)}")
            return 0