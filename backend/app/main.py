"""
Threat Intelligence Platform — FastAPI Application Entry Point.

Registers routers, configures CORS, and creates database tables on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import engine
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


@app.get("/", tags=["Health"])
async def root():
    """Health-check / info endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }
