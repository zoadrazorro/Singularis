"""
IWM Client - Client library for calling IWM service

Usage in perception/action modules:
    client = IWMClient("http://localhost:8001")
    latent = await client.encode_image(frame)
    pred = await client.predict_next(latent.z_cls, action_params)
"""

import asyncio
import base64
import io
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import numpy as np
from PIL import Image
import aiohttp
from loguru import logger


@dataclass
class IWMLatentResult:
    """Result from encode."""
    z_cls: np.ndarray  # [D]
    z_patches: Optional[np.ndarray] = None  # [N, D]
    timestamp: float = 0.0
    latent_dim: int = 768
    model_variant: str = "core"


@dataclass
class IWMPredictionResult:
    """Result from predict."""
    z_cls_pred: np.ndarray  # [D]
    z_patches_pred: Optional[np.ndarray] = None  # [N, D]
    mrr: float = 0.0
    uncertainty: float = 0.0
    timestamp: float = 0.0


@dataclass
class IWMRolloutResult:
    """Result from rollout."""
    z_cls_seq: List[np.ndarray]  # List of [D]
    z_patches_seq: Optional[List[np.ndarray]] = None  # List of [N, D]
    mrr_seq: List[float] = None
    uncertainty_seq: List[float] = None
    timestamp: float = 0.0


class IWMClient:
    """
    Async client for IWM service.
    
    Example:
        ```python
        client = IWMClient("http://localhost:8001")
        
        # Encode frame
        result = await client.encode_image(frame)
        being_state.vision_core_latent = result.z_cls
        
        # Predict next
        pred = await client.predict_next(
            result.z_cls,
            aug_params=[0.5, 0.3, 0.0]
        )
        surprise = np.linalg.norm(pred.z_cls_pred - next_latent)
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: float = 30.0
    ):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of IWM service
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
            logger.error(f"[IWM-CLIENT] Health check failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def encode_image(
        self,
        image: np.ndarray,
        return_patches: bool = False
    ) -> IWMLatentResult:
        """
        Encode image to latent.
        
        Args:
            image: Image as numpy array [H, W, 3] (uint8)
            return_patches: Return patch latents (else only CLS)
        
        Returns:
            IWMLatentResult with z_cls and optionally z_patches
        """
        try:
            # Convert to PIL and base64
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            
            pil_img = Image.fromarray(image)
            buffer = io.BytesIO()
            pil_img.save(buffer, format='PNG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Request
            payload = {
                'image_b64': img_b64,
                'return_patches': return_patches
            }
            
            session = await self._get_session()
            async with session.post(f"{self.base_url}/encode", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            
            return IWMLatentResult(
                z_cls=np.array(data['z_cls'], dtype=np.float32),
                z_patches=np.array(data['z_patches'], dtype=np.float32) if data['z_patches'] else None,
                timestamp=data['timestamp'],
                latent_dim=data['latent_dim'],
                model_variant=data['model_variant']
            )
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[IWM-CLIENT] Encode error: {e}")
            raise
    
    async def encode_image_path(
        self,
        image_path: str,
        return_patches: bool = False
    ) -> IWMLatentResult:
        """
        Encode image from path.
        
        Args:
            image_path: Path to image file
            return_patches: Return patch latents
        
        Returns:
            IWMLatentResult
        """
        try:
            payload = {
                'image_path': image_path,
                'return_patches': return_patches
            }
            
            session = await self._get_session()
            async with session.post(f"{self.base_url}/encode", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            
            return IWMLatentResult(
                z_cls=np.array(data['z_cls'], dtype=np.float32),
                z_patches=np.array(data['z_patches'], dtype=np.float32) if data['z_patches'] else None,
                timestamp=data['timestamp'],
                latent_dim=data['latent_dim'],
                model_variant=data['model_variant']
            )
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[IWM-CLIENT] Encode (path) error: {e}")
            raise
    
    async def predict_next(
        self,
        z_cls: np.ndarray,
        aug_params: List[float],
        z_patches: Optional[np.ndarray] = None
    ) -> IWMPredictionResult:
        """
        Predict next latent.
        
        Args:
            z_cls: Current global latent [D]
            aug_params: Augmentation/action parameters
            z_patches: Current patch latents [N, D] (optional)
        
        Returns:
            IWMPredictionResult
        """
        try:
            payload = {
                'z_cls': z_cls.tolist(),
                'aug_params': aug_params,
                'z_patches': z_patches.tolist() if z_patches is not None else None
            }
            
            session = await self._get_session()
            async with session.post(f"{self.base_url}/predict", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            
            return IWMPredictionResult(
                z_cls_pred=np.array(data['z_cls_pred'], dtype=np.float32),
                z_patches_pred=np.array(data['z_patches_pred'], dtype=np.float32) if data['z_patches_pred'] else None,
                mrr=data['mrr'],
                uncertainty=data['uncertainty'],
                timestamp=data['timestamp']
            )
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[IWM-CLIENT] Predict error: {e}")
            raise
    
    async def rollout(
        self,
        z_cls: np.ndarray,
        aug_seq: List[List[float]],
        z_patches: Optional[np.ndarray] = None
    ) -> IWMRolloutResult:
        """
        Rollout k-step predictions.
        
        Args:
            z_cls: Starting global latent [D]
            aug_seq: Sequence of augmentation/action parameters
            z_patches: Starting patch latents [N, D] (optional)
        
        Returns:
            IWMRolloutResult with sequences
        """
        try:
            payload = {
                'z_cls': z_cls.tolist(),
                'aug_seq': aug_seq,
                'z_patches': z_patches.tolist() if z_patches is not None else None
            }
            
            session = await self._get_session()
            async with session.post(f"{self.base_url}/rollout", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            self.total_requests += 1
            
            return IWMRolloutResult(
                z_cls_seq=[np.array(z, dtype=np.float32) for z in data['z_cls_seq']],
                z_patches_seq=[np.array(z, dtype=np.float32) for z in data['z_patches_seq']] if data['z_patches_seq'] else None,
                mrr_seq=data['mrr_seq'],
                uncertainty_seq=data['uncertainty_seq'],
                timestamp=data['timestamp']
            )
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[IWM-CLIENT] Rollout error: {e}")
            raise
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._session and not self._session.closed:
            # Try to close (may not work in all contexts)
            try:
                asyncio.get_event_loop().create_task(self.close())
            except:
                pass
