"""
Zerodha Trade Copier — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router
from app.services.order_poller import order_poller

# ─── Logging ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)-30s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize DB tables
    Shutdown: Stop all polling tasks
    """
    # ── Startup ──
    logger.info("=" * 60)
    logger.info(f"  {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"  Polling interval: {settings.POLL_INTERVAL_SECONDS}s")
    logger.info(f"  Test mode (copy all statuses): {settings.COPY_ALL_STATUSES}")
    logger.info(f"  Database: {settings.DATABASE_URL}")
    logger.info("=" * 60)

    await init_db()
    logger.info("Database tables initialized (copier.db)")

    yield

    # ── Shutdown ──
    logger.info("Shutting down — stopping all pollers...")
    await order_poller.stop_all()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Zerodha Master → Child Trade Copier.\n\n"
        "Monitors a master Zerodha account's orders and replicates completed trades "
        "on a child Zerodha account in real-time via polling."
    ),
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
