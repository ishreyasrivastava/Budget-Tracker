"""
Budget Tracker API - Main Application Entry Point

A production-ready FastAPI backend for personal budget management.
Features real authentication via Supabase, expense tracking, budget management,
and analytics dashboard.

Author: Shreya Srivastava
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .config import get_settings
from .routes import auth, expenses, budgets, dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Budget Tracker API starting up...")
    if not settings.validate():
        logger.warning("⚠️ Missing required environment variables!")
    yield
    # Shutdown
    logger.info("👋 Budget Tracker API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    ## Budget Tracker API
    
    A comprehensive personal finance management API that helps you:
    
    - 📊 Track daily expenses by category
    - 💰 Set and monitor monthly budgets
    - 🚨 Get alerts when approaching budget limits
    - 📈 View spending analytics and trends
    
    ### Authentication
    All endpoints (except `/health`) require authentication via Supabase JWT.
    Include the token in the `Authorization: Bearer <token>` header.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
    "https://budget-tracker-shreya.vercel.app",
    "https://*.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


# Health check endpoint (public)
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns API status and version.
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "service": "budget-tracker-api"
    }


@app.get("/", tags=["Root"])
async def root():
    """API root - redirects to documentation."""
    return {
        "message": "Welcome to Budget Tracker API",
        "docs": "/docs",
        "health": "/health",
        "version": settings.API_VERSION
    }
