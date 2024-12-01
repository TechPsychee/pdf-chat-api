# app/api/routes/__init__.py
from fastapi import APIRouter
from .pdf import router as pdf_router
from .chat import router as chat_router

router = APIRouter()

# Include routers without api_v1 prefix (that's added in main.py)
router.include_router(pdf_router)
router.include_router(chat_router)
