from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import (
    AUTO_CREATE_TABLES,
    CORS_ALLOW_CREDENTIALS,
    CORS_ORIGIN_REGEX,
    CORS_ORIGINS,
    settings,
)
from app.core.logging import logger
from app.database import async_engine, Base
import app.models  # Ensure all ORM models are registered with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager: handles startup and shutdown tasks.

    Tables are created automatically only for local/SQLite runs. On a serverless
    platform such as Vercel the database survives the process, so the schema is
    managed by Alembic migrations instead of an implicit create_all per cold start.
    """
    if AUTO_CREATE_TABLES:
        logger.info("Initializing database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Application startup complete.")
    else:
        logger.info("Automatic table creation disabled; expecting managed schema.")

    yield

    logger.info("Shutting down application...")
    await async_engine.dispose()
    logger.info("Database engine disposed cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-Ready URL Shortener API featuring unique short code generation, "
        "instant 307 redirects, detailed click tracking, and advanced time-series analytics."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend clients (e.g. Vercel, Next.js, React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Root Endpoint",
    description="Welcome endpoint providing API status and documentation link."
)
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health Check",
    description="Health check endpoint for Docker & Render deployment monitoring."
)
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


# Import and include routers AFTER root/health routes
from app.routers.analytics import router as analytics_router
from app.routers.url import router as url_router

app.include_router(analytics_router)
app.include_router(url_router)
