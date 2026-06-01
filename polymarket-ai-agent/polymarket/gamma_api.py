"""Polymarket Gamma API Client - Fetches real market data"""

import logging
from typing import List, Dict, Any, Optional
import httpx
import json

import config


class GammaAPIClient:
    """Client for Polymarket Gamma API - fetches market data, prices, volumes"""

    def __init__(self):
        self.base_url = config.POLYMARKET_GAMMA_URL
        self.timeout = config.POLYMARKET_TIMEOUT
        self.logger = logging.getLogger('polymarket.gamma')

    async def get_active_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        sort: str = 'volume24hr',
    ) -> List[Dict[str, Any]]:
        """
        Fetch active markets from Gamma API
        
        Args:
            limit: Number of markets to fetch (max 100)
            offset: Pagination offset
            sort: Sort by volume24hr, createdAt, or liquidity
            
        Returns:
            List of market dicts with fields:
              - id: Market ID
              - question: Question text
              - category: Market category
              - outcomePrices: [YES_price, NO_price] as JSON string
              - volumeNum or volume24hr: Trading volume
              - closed: Is market closed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f'{self.base_url}/markets',
                    params={
                        'limit': min(limit, 100),
                        'offset': offset,
                        'status': 'active',
                        'sort': sort,
                    },
                )
            
            if response.status_code != 200:
                self.logger.error(f'Gamma API error: {response.status_code} - {response.text}')
                return []
            
            markets = response.json()
            self.logger.debug(f'Fetched {len(markets)} active markets')
            return markets
        
        except Exception as e:
            self.logger.error(f'Error fetching markets: {e}')
            return []

    async def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch single market details
        
        Args:
            market_id: Market ID
            
        Returns:
            Market dict or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f'{self.base_url}/markets/{market_id}'
                )
            
            if response.status_code != 200:
                self.logger.error(f'Error fetching market {market_id}: {response.status_code}')
                return None
            
            return response.json()
        
        except Exception as e:
            self.logger.error(f'Error fetching market {market_id}: {e}')
            return None

    async def get_market_prices(self, market_id: str) -> Optional[Dict[str, float]]:
        """
        Get current market prices (YES/NO)
        
        Args:
            market_id: Market ID
            
        Returns:
            Dict with 'yes' and 'no' prices, or None
        """
        try:
            market = await self.get_market(market_id)
            if not market:
                return None
            
            outcome_prices = market.get('outcomePrices', '["0.5", "0.5"]')
            
            # Parse JSON if string
            if isinstance(outcome_prices, str):
                prices = json.loads(outcome_prices)
            else:
                prices = outcome_prices
            
            return {
                'yes': float(prices[0]) if len(prices) > 0 else 0.5,
                'no': float(prices[1]) if len(prices) > 1 else 0.5,
            }
        
        except Exception as e:
            self.logger.error(f'Error parsing prices for {market_id}: {e}')
            return None

    async def get_market_volume(self, market_id: str) -> Optional[float]:
        """
        Get 24h trading volume
        
        Args:
            market_id: Market ID
            
        Returns:
            Volume in USD or None
        """
        try:
            market = await self.get_market(market_id)
            if not market:
                return None
            
            # Try different volume fields
            volume = market.get('volumeNum')
            if volume:
                return float(volume)
            
            volume = market.get('volume')
            if volume:
                return float(volume)
            
            volume = market.get('volume24hr')
            if volume:
                return float(volume)
            
            return 0.0
        
        except Exception as e:
            self.logger.error(f'Error getting volume for {market_id}: {e}')
            return None

    async def search_markets(self, query: str) -> List[Dict[str, Any]]:
        """
        Search markets by keyword
        
        Args:
            query: Search query
            
        Returns:
            List of matching markets
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f'{self.base_url}/markets',
                    params={
                        'query': query,
                        'limit': 50,
                    },
                )
            
            if response.status_code != 200:
                return []
            
            return response.json()
        
        except Exception as e:
            self.logger.error(f'Error searching markets: {e}')
            return []

    async def get_markets_by_category(
        self,
        category: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Fetch markets by category
        
        Args:
            category: Category name (e.g., 'US Politics', 'Sports')
            limit: Number of markets
            
        Returns:
            List of markets in category
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f'{self.base_url}/markets',
                    params={
                        'category': category,
                        'limit': limit,
                        'status': 'active',
                    },
                )
            
            if response.status_code != 200:
                return []
            
            markets = response.json()
            self.logger.debug(f'Fetched {len(markets)} markets in category {category}')
            return markets
        
        except Exception as e:
            self.logger.error(f'Error fetching category {category}: {e}')
            return []
