import google.generativeai as genai
from typing import List, Dict
from pathlib import Path
from fastapi import HTTPException
from ..core.config import get_settings
from ..core.logging import setup_logging
from .pdf_service import PDFService

settings = get_settings()
logger = setup_logging()


class LLMService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-pro")
            self.pdf_service = PDFService()
            logger.info("LLM Service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM Service: {str(e)}")
            raise

    async def generate_response(self, pdf_id: str, query: str) -> str:
        """Generate a response based on the PDF content and user query"""
        try:
            # Get PDF content
            text_content = self.pdf_service.get_pdf_content(pdf_id)
            if not text_content:
                raise HTTPException(status_code=404, detail="PDF content not found")

            # Create prompt with context
            prompt = self._create_prompt(text_content, query)

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
            )

            logger.debug(f"Generated response for query: {query[:50]}...")
            return response.text

        except HTTPException as http_err:
            logger.error(f"HTTP error in generate_response: {str(http_err)}")
            raise
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error generating response: {str(e)}"
            )

    def _create_prompt(self, context: str, query: str) -> str:
        """Create a detailed prompt for the LLM"""
        return f"""
        You are an AI assistant analyzing a document about philosophical films. 
        
        Document Content:
        {context}

        User Question: {query}

        Please provide a detailed response based on the document content above. Consider:
        1. The main themes and categories present in the document
        2. The films mentioned and their philosophical relevance
        3. Any specific philosophical concepts or ideas discussed
        4. The organization and structure of the content

        If answering about specific films or categories, please cite examples from the document.
        If the question cannot be answered based on the document content, explain why.

        Provide your response in a clear, structured format.
        """
