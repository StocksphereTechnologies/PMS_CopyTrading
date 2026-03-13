"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import accounts, positions, trades, summary
from app.api.endpoints import auth
from app.core.database import engine, Base
from contextlib import asynccontextmanager
import asyncio
from app.services.account_service import AccountService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize broker sessions for all enabled accounts
    from app.core.http import HttpClient
    asyncio.create_task(AccountService.initialize_all_sessions())
    yield
    # Shutdown: Close shared HTTP client
    await HttpClient.close_client()

app = FastAPI(
    title="StockSphere Trading Backend",
    description="Multi-account trading backend with Zerodha and 5paisa support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(positions.router, prefix=settings.API_V1_PREFIX)
app.include_router(trades.router, prefix=settings.API_V1_PREFIX)
app.include_router(summary.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StockSphere Trading Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
