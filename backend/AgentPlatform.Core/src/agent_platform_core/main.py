"""
FastAPI application entry point for Agent Platform Core.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .api.endpoints import agents, chat
from .models.schemas import ErrorResponse
from .database.connection import initialize_database, close_database

# Load environment variables
load_dotenv()


def setup_logging():
    """
    Configure centralized logging for the entire application.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create custom formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    
    return logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    """
    logger = logging.getLogger(__name__)
    
    # Startup
    logger.info("Starting Agent Platform Core...")
    
    try:
        # Initialize database connection
        initialize_database()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("Agent Platform Core started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Platform Core...")
    
    try:
        # Close database connections
        close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    logger.info("Agent Platform Core shut down successfully")


# Setup logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "Agent Platform Core"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="A flexible and scalable core AI service platform",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
            code="INTERNAL_ERROR"
        ).dict()
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "Agent Platform Core"}


# Database health check endpoint
@app.get("/health/db")
async def database_health_check():
    """
    Database health check endpoint.
    """
    from .database.connection import test_connection
    
    if test_connection():
        return {"status": "healthy", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")


# Include API routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with basic information.
    """
    return {
        "service": "Agent Platform Core",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "database": "SQL Server"
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    ) 