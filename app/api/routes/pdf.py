from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ..models.schemas import PDFResponse
from ...services.pdf_service import PDFService
from ...core.security import verify_api_key, check_rate_limit
from ...core.logging import setup_logging

router = APIRouter()
logger = setup_logging()


@router.post(
    "/pdf",
    response_model=PDFResponse,
    dependencies=[Depends(verify_api_key), Depends(check_rate_limit)],
)
async def upload_pdf(
    file: UploadFile = File(...),
    pdf_service: PDFService = Depends(lambda: PDFService()),
):
    """Upload a PDF file"""
    try:
        pdf_info = await pdf_service.save_pdf(file)
        return PDFResponse(**pdf_info)
    except HTTPException as e:
        logger.error(f"HTTP error during PDF upload: {e.status_code}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during PDF upload: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
