from fastapi import APIRouter, Depends, HTTPException
from ..models.schemas import ChatRequest, ChatResponse
from ...services.llm_service import LLMService
from ...core.logging import setup_logging

router = APIRouter()
logger = setup_logging()


@router.post("/chat/{pdf_id}", response_model=ChatResponse)
async def chat_with_pdf(
    pdf_id: str,
    request: ChatRequest,
    llm_service: LLMService = Depends(lambda: LLMService()),
):
    """
    Chat with a specific PDF document
    """
    try:
        response = await llm_service.generate_response(pdf_id, request.message)
        return ChatResponse(response=response)
    except HTTPException as e:
        logger.error(f"HTTP error in chat endpoint: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
