import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict  # Add this import
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from ..core.config import get_settings
from ..core.logging import setup_logging
from .embedding_service import EmbeddingService
import json

settings = get_settings()
logger = setup_logging()


class PDFService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_service = EmbeddingService()

    async def save_pdf(self, file: UploadFile) -> dict:
        """Save uploaded PDF file and extract basic information"""
        try:
            # Validate file type
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400, detail="Only PDF files are allowed"
                )

            # Generate unique identifier
            pdf_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{pdf_id}_{timestamp}.pdf"
            file_path = self.upload_dir / safe_filename

            # Read and save file content
            content = await file.read()
            file_size = len(content)

            logger.debug(f"Received PDF file size: {file_size} bytes")

            if file_size > settings.MAX_PDF_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of {settings.MAX_PDF_SIZE // (1024 * 1024)}MB",
                )

            # Save file
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(content)

            logger.debug(f"Saved PDF to: {file_path}")

            # Extract PDF information and text content
            pdf_info = self._extract_pdf_info(file_path, file_size)
            pdf_info["pdf_id"] = pdf_id
            pdf_info["filename"] = file.filename
            pdf_info["uploaded_at"] = datetime.utcnow()

            # Store the extracted text
            self._store_pdf_content(pdf_id, pdf_info)

            # Process embeddings for the document
            try:
                chunk_count = self.embedding_service.process_document(
                    pdf_id, pdf_info["text_content"]
                )
                pdf_info["chunk_count"] = chunk_count
                logger.info(f"Created {chunk_count} embeddings for PDF {pdf_id}")
            except Exception as e:
                logger.error(f"Error creating embeddings: {str(e)}")
                # Continue even if embeddings fail, as basic functionality should still work

            logger.info(f"PDF saved successfully: {pdf_info}")
            return pdf_info

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error processing PDF file: {str(e)}"
            )

    def _extract_pdf_info(self, file_path: Path, file_size: int) -> dict:
        """Extract basic information and text content from PDF file"""
        try:
            with open(file_path, "rb") as file:
                pdf = PdfReader(file)
                text_content = ""

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text.strip() + "\n\n"

                logger.debug(
                    f"Extracted text content length: {len(text_content)} characters"
                )
                logger.debug(f"First 200 characters of content: {text_content[:200]}")

                return {
                    "size": file_size,
                    "pages": len(pdf.pages),
                    "text_content": text_content.strip(),
                }

        except Exception as e:
            logger.error(f"Error extracting PDF info: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Invalid or corrupted PDF file: {str(e)}"
            )

    def _store_pdf_content(self, pdf_id: str, pdf_info: dict):
        """Store PDF content and metadata"""
        try:
            content_file = self.data_dir / f"{pdf_id}.json"
            with open(content_file, "w", encoding="utf-8") as f:
                json.dump(pdf_info, f, default=str, ensure_ascii=False, indent=2)

            logger.debug(f"Stored PDF content to: {content_file}")

        except Exception as e:
            logger.error(f"Error storing PDF content: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error storing PDF content: {str(e)}"
            )

    def get_pdf_content(self, pdf_id: str) -> str:
        """Retrieve PDF content by ID"""
        try:
            content_file = self.data_dir / f"{pdf_id}.json"
            if not content_file.exists():
                logger.error(f"PDF content file not found: {content_file}")
                raise HTTPException(status_code=404, detail="PDF not found")

            with open(content_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                text_content = content.get("text_content", "")
                logger.debug(
                    f"Retrieved content length: {len(text_content)} characters"
                )
                logger.debug(
                    f"First 200 characters of retrieved content: {text_content[:200]}"
                )
                return text_content

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving PDF content: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error retrieving PDF content: {str(e)}"
            )

    async def process_large_pdf(self, file_path: Path) -> dict:
        """Process large PDF files efficiently"""
        try:
            with open(file_path, "rb") as file:
                pdf = PdfReader(file)
                total_pages = len(pdf.pages)

                # Process pages in chunks
                chunks = []
                for i in range(0, total_pages, settings.MAX_CHUNKS_PER_REQUEST):
                    page_range = range(
                        i, min(i + settings.MAX_CHUNKS_PER_REQUEST, total_pages)
                    )
                    chunk = ""
                    for page_num in page_range:
                        chunk += pdf.pages[page_num].extract_text() + "\n"
                    chunks.append(chunk)

                # Process embeddings for chunks
                for i, chunk in enumerate(chunks):
                    try:
                        self.embedding_service.process_document(
                            f"{file_path.stem}_chunk_{i}", chunk
                        )
                    except Exception as e:
                        logger.error(
                            f"Error creating embeddings for chunk {i}: {str(e)}"
                        )

                return {
                    "total_pages": total_pages,
                    "chunks": chunks,
                    "chunk_count": len(chunks),
                }
        except Exception as e:
            logger.error(f"Error processing large PDF: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error processing large PDF file"
            )

    async def get_relevant_chunks(
        self, pdf_id: str, query: str, n_results: int = 3
    ) -> List[str]:
        """Get relevant chunks of text based on query"""
        try:
            return self.embedding_service.query_document(pdf_id, query, n_results)
        except Exception as e:
            logger.error(f"Error getting relevant chunks: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error retrieving relevant content"
            )
