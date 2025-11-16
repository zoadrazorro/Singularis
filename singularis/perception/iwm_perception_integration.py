"""
IWM Perception Integration

Integrates IWM world model into perception pipeline.
Adds to BeingState:
- vision_core_latent: Current visual latent
- vision_prediction_surprise: Prediction error
- vision_mrr: World model confidence

Usage:
    from singularis.perception.iwm_perception_integration import IWMPerceptionModule
    
    iwm_module = IWMPerceptionModule(iwm_url="http://localhost:8001")
    await iwm_module.process_frame(frame, being_state, action_taken=None)
"""

import asyncio
import time
from typing import Optional, List
import numpy as np
from loguru import logger

from singularis.core.being_state import BeingState
from singularis.world_model import IWMClient, IWMLatentResult


class IWMPerceptionModule:
    """
    Integrates IWM world model into perception pipeline.
    
    Updates BeingState with:
    - vision_core_latent: Current scene latent
    - vision_prediction_surprise: Surprise from prediction
    - vision_mrr: World model confidence
    
    Can be used standalone or integrated into UnifiedPerceptionLayer.
    """
    
    def __init__(
        self,
        iwm_url: str = "http://localhost:8001",
        enable_surprise: bool = True,
        enable_rollouts: bool = False,
        surprise_threshold: float = 2.0
    ):
        """
        Initialize IWM perception module.
        
        Args:
            iwm_url: URL of IWM service
            enable_surprise: Compute prediction surprise
            enable_rollouts: Enable k-step rollouts (expensive)
            surprise_threshold: Threshold for high surprise warnings
        """
        self.client = IWMClient(iwm_url)
        self.enable_surprise = enable_surprise
        self.enable_rollouts = enable_rollouts
        self.surprise_threshold = surprise_threshold
        
        # Stats
        self.total_frames = 0
        self.total_errors = 0
        self.high_surprise_count = 0
        
        # Last action for conditioning
        self.last_action_params: Optional[List[float]] = None
        
        logger.info(f"[IWM-PERCEPTION] Initialized with service: {iwm_url}")
    
    async def check_health(self) -> bool:
        """Check if IWM service is available."""
        try:
            health = await self.client.health()
            return health.get('status') == 'ok'
        except:
            return False
    
    async def process_frame(
        self,
        frame: np.ndarray,
        being_state: BeingState,
        action_taken: Optional[str] = None
    ) -> bool:
        """
        Process frame through IWM and update BeingState.
        
        Args:
            frame: RGB frame [H, W, 3] (uint8)
            being_state: BeingState to update
            action_taken: Action taken since last frame (optional)
        
        Returns:
            True if successful, False if error
        """
        try:
            start_time = time.time()
            
            # Encode current frame
            result = await self.client.encode_image(frame, return_patches=False)
            
            # Store current latent
            being_state.vision_core_latent_prev = being_state.vision_core_latent
            being_state.vision_core_latent = result.z_cls
            being_state.vision_core_timestamp = time.time()
            
            # Compute surprise if we have previous latent
            if self.enable_surprise and being_state.vision_core_latent_prev is not None:
                surprise = await self._compute_surprise(
                    being_state.vision_core_latent_prev,
                    being_state.vision_core_latent,
                    action_taken
                )
                being_state.vision_prediction_surprise = surprise
                
                # Warning on high surprise
                if surprise > self.surprise_threshold:
                    self.high_surprise_count += 1
                    logger.warning(
                        f"[IWM-PERCEPTION] High surprise: {surprise:.2f} "
                        f"(threshold: {self.surprise_threshold})"
                    )
            
            self.total_frames += 1
            
            latency = (time.time() - start_time) * 1000
            logger.debug(f"[IWM-PERCEPTION] Processed frame in {latency:.1f}ms")
            
            return True
        
        except Exception as e:
            self.total_errors += 1
            logger.error(f"[IWM-PERCEPTION] Frame processing error: {e}")
            return False
    
    async def _compute_surprise(
        self,
        z_prev: np.ndarray,
        z_current: np.ndarray,
        action_taken: Optional[str]
    ) -> float:
        """
        Compute prediction surprise.
        
        Args:
            z_prev: Previous latent
            z_current: Current latent (ground truth)
            action_taken: Action that was taken
        
        Returns:
            Surprise (L2 distance in latent space)
        """
        try:
            # Convert action to parameters (placeholder - customize for your action space)
            if action_taken:
                aug_params = self._action_to_params(action_taken)
            else:
                aug_params = [0.0] * 16  # Neutral/no action
            
            # Predict what next latent should be
            pred = await self.client.predict_next(z_prev, aug_params)
            
            # Compute surprise (L2 distance)
            surprise = float(np.linalg.norm(pred.z_cls_pred - z_current))
            
            return surprise
        
        except Exception as e:
            logger.error(f"[IWM-PERCEPTION] Surprise computation error: {e}")
            return 0.0
    
    def _action_to_params(self, action: str) -> List[float]:
        """
        Convert action string to augmentation/action parameters.
        
        This is a placeholder - customize for your action space.
        
        Args:
            action: Action string (e.g., "move_forward", "turn_left")
        
        Returns:
            Parameter vector [aug_dim]
        """
        # Simple encoding (Phase 1 placeholder)
        # In Phase 3, this becomes more sophisticated
        
        action_map = {
            'move_forward': [1.0, 0.0, 0.0, 0.0],
            'move_backward': [-1.0, 0.0, 0.0, 0.0],
            'turn_left': [0.0, -1.0, 0.0, 0.0],
            'turn_right': [0.0, 1.0, 0.0, 0.0],
            'attack': [0.0, 0.0, 1.0, 0.0],
            'wait': [0.0, 0.0, 0.0, 0.0],
        }
        
        params = action_map.get(action, [0.0, 0.0, 0.0, 0.0])
        
        # Pad to aug_dim (16)
        while len(params) < 16:
            params.append(0.0)
        
        return params
    
    async def imagine_future(
        self,
        being_state: BeingState,
        action_sequence: List[str]
    ) -> Optional[List[np.ndarray]]:
        """
        Imagine future latents for an action sequence (Phase 3 feature).
        
        Args:
            being_state: Current BeingState
            action_sequence: List of actions to imagine
        
        Returns:
            List of predicted latents, or None if error
        """
        if not self.enable_rollouts:
            logger.warning("[IWM-PERCEPTION] Rollouts disabled")
            return None
        
        if being_state.vision_core_latent is None:
            logger.warning("[IWM-PERCEPTION] No current latent for rollout")
            return None
        
        try:
            # Convert actions to parameters
            aug_seq = [self._action_to_params(action) for action in action_sequence]
            
            # Rollout
            rollout = await self.client.rollout(
                being_state.vision_core_latent,
                aug_seq
            )
            
            logger.info(
                f"[IWM-PERCEPTION] Imagined {len(rollout.z_cls_seq)} steps, "
                f"avg MRR: {np.mean(rollout.mrr_seq):.3f}"
            )
            
            return rollout.z_cls_seq
        
        except Exception as e:
            logger.error(f"[IWM-PERCEPTION] Imagination error: {e}")
            return None
    
    def get_stats(self) -> dict:
        """Get module statistics."""
        return {
            'total_frames': self.total_frames,
            'total_errors': self.total_errors,
            'high_surprise_count': self.high_surprise_count,
            'error_rate': self.total_errors / max(1, self.total_frames),
            'high_surprise_rate': self.high_surprise_count / max(1, self.total_frames)
        }
    
    async def close(self):
        """Cleanup."""
        await self.client.close()


# ========================================
# Example Integration with UnifiedPerceptionLayer
# ========================================

# This is how you'd integrate into existing unified_perception.py:
"""
from singularis.perception.iwm_perception_integration import IWMPerceptionModule

class UnifiedPerceptionLayer:
    def __init__(self, ...):
        # ... existing init ...
        
        # Add IWM module
        self.iwm_module = IWMPerceptionModule(
            iwm_url="http://localhost:8001",
            enable_surprise=True,
            surprise_threshold=2.0
        )
    
    async def process_frame(self, frame: np.ndarray, being_state: BeingState):
        # ... existing perception ...
        
        # Add IWM processing
        await self.iwm_module.process_frame(
            frame,
            being_state,
            action_taken=being_state.last_action
        )
        
        # Now being_state.vision_core_latent is populated
        # and can be used by other systems
"""
