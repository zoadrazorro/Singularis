"""
GWM Client - Client library for calling GWM service

Usage in action arbiter:
    client = GWMClient("http://localhost:8002")
    await client.send_snapshot(snapshot_dict)
    features = await client.get_features()
    
    # Use features
    if features['threat_level'] > 0.7:
        prefer_defensive_actions()
"""

import asyncio
from typing import Optional, Dict, Any, List
import aiohttp
from loguru import logger


class GWMClient:
    """
    Async client for GWM service.
    
    Example:
        ```python
        client = GWMClient("http://localhost:8002")
        
        # Send snapshot from engine
        snapshot = {
            "timestamp": time.time(),
            "player": {...},
            "npcs": [...]
        }
        await client.send_snapshot(snapshot)
        
        # Get tactical features
        features = await client.get_features()
        threat_level = features['threat_level']
        nearest_enemy = features['nearest_enemy']
        
        # Use in ActionArbiter
        if threat_level > 0.7 and player_health < 0.3:
            suggest_escape_action()
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8002",
        timeout: float = 10.0
    ):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of GWM service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Stats
        self.total_requests = 0
        self.total_errors = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def close(self):
        """Close client session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def health(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health") as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            logger.error(f"[GWM-CLIENT] Health check failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def send_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send engine snapshot to GWM.
        
        Args:
            snapshot: Snapshot dict with player, npcs, objects, etc.
        
        Returns:
            Update response
        """
        try:
            session = await self._get_session()
            async with session.post(f"{self.base_url}/snapshot", json=snapshot) as resp:
                resp.raise_for_status()
                result = await resp.json()
            
            self.total_requests += 1
            return result
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[GWM-CLIENT] Send snapshot error: {e}")
            raise
    
    async def get_features(self) -> Dict[str, Any]:
        """
        Get current tactical features.
        
        Returns:
            GameWorldFeatures dict
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/features") as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            return data['features']
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[GWM-CLIENT] Get features error: {e}")
            raise
    
    async def get_entities(self) -> Dict[str, Any]:
        """
        Get current entity states.
        
        Returns:
            Dict with player, npcs, objects, cover_spots
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/entities") as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            return data
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[GWM-CLIENT] Get entities error: {e}")
            raise
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._session and not self._session.closed:
            try:
                asyncio.get_event_loop().create_task(self.close())
            except:
                pass
