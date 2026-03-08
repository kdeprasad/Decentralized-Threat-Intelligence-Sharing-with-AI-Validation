"""
Threat Intelligence Platform — FastAPI Application Entry Point.

Registers routers, configures CORS, and creates database tables on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database.db import engine, async_session
from app.database.schema import Base
from app.api.routes_threats import router as threats_router
from app.api.routes_validation import router as validation_router
from app.services import background_worker
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── Lifespan: runs on startup / shutdown ────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables, then start the background polling worker."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready.")

    # Start background Google Sheets polling worker
    background_worker.start()
    logger.info("Background worker started (interval=%ds).", settings.POLL_INTERVAL_SECONDS)

    yield

    # Shutdown
    background_worker.stop()
    logger.info("Shutting down %s", settings.APP_NAME)
    await engine.dispose()


# ── FastAPI app ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Collects threat intelligence from Google Forms, validates with AI, and exposes a REST API.",
    lifespan=lifespan,
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ───────────────────────────────────
app.include_router(threats_router, prefix="/threats", tags=["Threats"])
app.include_router(validation_router, prefix="/validate", tags=["Validation"])


# ── Health / info endpoints ─────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Lightweight info endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Full health check — verifies database connectivity.

    Used by Docker HEALTHCHECK and monitoring systems.
    Returns HTTP 200 if healthy, HTTP 503 if the database is unreachable.
    """
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.APP_VERSION,
        }
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc),
            },
        )
