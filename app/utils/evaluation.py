from typing import List, Dict
import time
from ..services.llm_service import LLMService
from ..services.embedding_service import EmbeddingService
from ..core.logging import setup_logging

logger = setup_logging()


class PerformanceEvaluator:
    def __init__(self):
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()

    async def compare_approaches(self, pdf_id: str, queries: List[str]) -> Dict:
        """Compare direct LLM vs chunked approach"""
        results = {
            "direct": await self._evaluate_direct(pdf_id, queries),
            "chunked": await self._evaluate_chunked(pdf_id, queries),
        }

        logger.info(f"Performance comparison completed for PDF {pdf_id}")
        return results

    async def _evaluate_direct(self, pdf_id: str, queries: List[str]) -> Dict:
        """Evaluate direct LLM processing"""
        start_time = time.time()
        responses = []
        token_counts = []

        for query in queries:
            try:
                response = await self.llm_service.generate_response(pdf_id, query)
                responses.append(response)
                token_counts.append(len(response.split()))
            except Exception as e:
                logger.error(f"Error in direct evaluation: {str(e)}")

        return {
            "processing_time": time.time() - start_time,
            "average_tokens": (
                sum(token_counts) / len(token_counts) if token_counts else 0
            ),
            "responses": responses,
        }

    async def _evaluate_chunked(self, pdf_id: str, queries: List[str]) -> Dict:
        """Evaluate chunked processing with embeddings"""
        start_time = time.time()
        responses = []
        token_counts = []

        for query in queries:
            try:
                relevant_chunks = self.embedding_service.query_document(pdf_id, query)
                combined_response = (
                    await self.llm_service.generate_response_from_chunks(
                        relevant_chunks, query
                    )
                )
                responses.append(combined_response)
                token_counts.append(len(combined_response.split()))
            except Exception as e:
                logger.error(f"Error in chunked evaluation: {str(e)}")

        return {
            "processing_time": time.time() - start_time,
            "average_tokens": (
                sum(token_counts) / len(token_counts) if token_counts else 0
            ),
            "responses": responses,
            "chunks_used": self.embedding_service.get_cache_stats(),
        }
