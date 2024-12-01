import typing
from typing import List, Dict
from pathlib import Path
from ..core.config import get_settings
from ..core.logging import setup_logging

settings = get_settings()
logger = setup_logging()


class EmbeddingService:
    def __init__(self):
        self.chunk_size = settings.EMBEDDING_CHUNK_SIZE
        self.embeddings_cache = {}

    def process_document(
        self, pdf_id: str, text_content: str, chunk_size: int = 500
    ) -> int:
        """Process document text into chunks and cache"""
        try:
            # Split text into chunks
            chunks = self._split_text(text_content, chunk_size)
            chunk_count = len(chunks)

            # Store in cache
            self.embeddings_cache[pdf_id] = {
                "chunks": chunks,
                "total_chunks": chunk_count,
            }

            logger.info(f"Processed document {pdf_id} into {chunk_count} chunks")
            return chunk_count
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return 0

    def query_document(self, pdf_id: str, query: str, n_results: int = 3) -> List[str]:
        """Get most relevant chunks for a query"""
        try:
            if pdf_id not in self.embeddings_cache:
                logger.error(f"Document {pdf_id} not found in cache")
                return []

            doc_data = self.embeddings_cache[pdf_id]
            chunks = doc_data["chunks"]

            # Simple keyword matching for now
            relevant_chunks = []
            query_terms = query.lower().split()

            for chunk in chunks:
                if any(term in chunk.lower() for term in query_terms):
                    relevant_chunks.append(chunk)

            # Return top N chunks or all if less than N
            return relevant_chunks[:n_results]

        except Exception as e:
            logger.error(f"Error querying document: {str(e)}")
            return []

    def handle_long_text(self, text: str, max_tokens: int = 8196) -> List[str]:
        """Handle text exceeding token limit"""
        chunks = self._split_text(text, self.chunk_size)
        processed_chunks = []
        current_chunk = ""
        current_tokens = 0

        for chunk in chunks:
            chunk_tokens = len(chunk.split())
            if current_tokens + chunk_tokens > max_tokens:
                processed_chunks.append(current_chunk)
                current_chunk = chunk
                current_tokens = chunk_tokens
            else:
                current_chunk += "\n" + chunk if current_chunk else chunk
                current_tokens += chunk_tokens

        if current_chunk:
            processed_chunks.append(current_chunk)

        return processed_chunks

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of approximately equal size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            current_size += len(word) + 1  # +1 for space
            if current_size > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def get_cache_stats(self) -> Dict:
        """Get statistics about cached embeddings"""
        return {
            "total_documents": len(self.embeddings_cache),
            "documents": {
                pdf_id: {"total_chunks": data["total_chunks"]}
                for pdf_id, data in self.embeddings_cache.items()
            },
        }
