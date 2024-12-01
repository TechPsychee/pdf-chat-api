from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings, create_necessary_directories
from .core.logging import setup_logging
from .api.routes import router

# Initialize settings and logger
settings = get_settings()
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.API_V1_STR)


# Create necessary directories on startup
@app.on_event("startup")
async def startup_event():
    create_necessary_directories()
    logger.info("Application startup completed")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to PDF Chat API"}
