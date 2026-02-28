import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    """Shared HTTP client to be used for connection pooling"""
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        """Get or create the shared httpx client"""
        if cls._client is None or cls._client.is_closed:
            # We use a large connection pool for high concurrency
            cls._client = httpx.AsyncClient(
                verify=False,
                timeout=httpx.Timeout(10.0, connect=5.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
            )
            logger.info("Initialized shared httpx.AsyncClient for connection pooling")
        return cls._client

    @classmethod
    async def close_client(cls):
        """Close the shared client if it exists"""
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info("Closed shared httpx.AsyncClient")
            cls._client = None
