"""
Polymarket API client
"""
from typing import Dict, List, Optional, Any
import httpx
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class PolymarketAPIClient:
    """
    Client for interacting with Polymarket APIs
    """

    def __init__(self):
        self.base_url = settings.polymarket.api_url
        self.clob_url = settings.polymarket.clob_api_url
        self.api_key = settings.polymarket.api_key
        self.client = httpx.Client(timeout=30.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _make_request(
        self, method: str, endpoint: str, base_url: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Polymarket API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            base_url: Base URL to use (defaults to gamma API)
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{base_url or self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API request failed", error=str(e), endpoint=endpoint)
            raise

    # Markets endpoints

    def get_markets(
        self, limit: int = 100, offset: int = 0, active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of markets

        Args:
            limit: Number of markets to return
            offset: Offset for pagination
            active: Filter by active status

        Returns:
            List of market data
        """
        params = {"limit": limit, "offset": offset}
        if active is not None:
            params["active"] = str(active).lower()

        logger.info(f"Fetching markets", limit=limit, offset=offset, active=active)
        return self._make_request("GET", "/markets", params=params)

    def get_market(self, market_id: str) -> Dict[str, Any]:
        """
        Get specific market details

        Args:
            market_id: Market ID

        Returns:
            Market data
        """
        logger.info(f"Fetching market", market_id=market_id)
        return self._make_request("GET", f"/markets/{market_id}")

    def get_market_trades(
        self, market_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trades for a specific market

        Args:
            market_id: Market ID
            limit: Number of trades to return

        Returns:
            List of trade data
        """
        params = {"limit": limit}
        logger.info(f"Fetching market trades", market_id=market_id, limit=limit)
        return self._make_request("GET", f"/markets/{market_id}/trades", params=params)

    # Trader/Position endpoints

    def get_positions(self, address: str) -> List[Dict[str, Any]]:
        """
        Get positions for a specific trader address

        Args:
            address: Ethereum address

        Returns:
            List of position data
        """
        logger.info(f"Fetching positions", address=address)
        return self._make_request("GET", f"/positions", params={"user": address})

    def get_user_trades(
        self, address: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get trades for a specific user

        Args:
            address: Ethereum address
            limit: Number of trades to return
            offset: Offset for pagination

        Returns:
            List of trade data
        """
        params = {"user": address, "limit": limit, "offset": offset}
        logger.info(f"Fetching user trades", address=address, limit=limit)
        return self._make_request("GET", "/trades", params=params)

    # CLOB API endpoints

    def get_order_book(self, token_id: str) -> Dict[str, Any]:
        """
        Get order book for a specific token

        Args:
            token_id: Token ID

        Returns:
            Order book data
        """
        logger.info(f"Fetching order book", token_id=token_id)
        return self._make_request(
            "GET", f"/book?token_id={token_id}", base_url=self.clob_url
        )

    def get_ticker(self, token_id: str) -> Dict[str, Any]:
        """
        Get ticker data for a specific token

        Args:
            token_id: Token ID

        Returns:
            Ticker data
        """
        logger.info(f"Fetching ticker", token_id=token_id)
        return self._make_request(
            "GET", f"/ticker?token_id={token_id}", base_url=self.clob_url
        )

    def close(self):
        """Close the HTTP client"""
        self.client.close()


class AsyncPolymarketAPIClient:
    """
    Async client for interacting with Polymarket APIs
    """

    def __init__(self):
        self.base_url = settings.polymarket.api_url
        self.clob_url = settings.polymarket.clob_api_url
        self.api_key = settings.polymarket.api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _make_request(
        self, method: str, endpoint: str, base_url: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make async HTTP request to Polymarket API"""
        url = f"{base_url or self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            logger.debug(f"Making async {method} request to {url}")
            response = await self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Async API request failed", error=str(e), endpoint=endpoint)
            raise

    async def get_markets(
        self, limit: int = 100, offset: int = 0, active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get list of markets (async)"""
        params = {"limit": limit, "offset": offset}
        if active is not None:
            params["active"] = str(active).lower()

        return await self._make_request("GET", "/markets", params=params)

    async def get_positions(self, address: str) -> List[Dict[str, Any]]:
        """Get positions for a specific trader address (async)"""
        return await self._make_request("GET", f"/positions", params={"user": address})

    async def close(self):
        """Close the async HTTP client"""
        await self.client.aclose()
