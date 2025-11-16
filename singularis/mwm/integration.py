"""
MWM Integration - Packing, unpacking, and update utilities

Connects MWM module to BeingState and existing systems (GWM, IWM).
"""

import torch
import numpy as np
import time
from typing import Dict, Any, Optional
from loguru import logger

# Import types (will be available after types.py is loaded)
from .types import (
    WorldSlice,
    SelfSlice,
    AffectSlice,
    MentalWorldModelState
)


# ========================================
# Packing Functions: Python → Tensor
# ========================================

def pack_gwm_features(gwm_features: Optional[Dict[str, Any]]) -> np.ndarray:
    """
    Pack GWM GameWorldFeatures into flat numpy array.
    
    Args:
        gwm_features: GameWorldFeatures dict from GWM service
    
    Returns:
        np.ndarray of shape [16] with packed features
    """
    if gwm_features is None:
        return np.zeros(16, dtype=np.float32)
    
    # Extract fields with defaults
    arr = np.array([
        gwm_features.get('threat_level', 0.0),
        float(gwm_features.get('num_enemies_total', 0)),
        float(gwm_features.get('num_enemies_in_los', 0)),
        float(gwm_features.get('num_enemies_aware', 0)),
        
        # Nearest enemy
        gwm_features.get('nearest_enemy', {}).get('distance', 999.0) if gwm_features.get('nearest_enemy') else 999.0,
        gwm_features.get('nearest_enemy', {}).get('bearing_deg', 0.0) if gwm_features.get('nearest_enemy') else 0.0,
        gwm_features.get('nearest_enemy', {}).get('health', 1.0) if gwm_features.get('nearest_enemy') else 1.0,
        
        # Cover
        gwm_features.get('best_cover_spot', {}).get('distance', 999.0) if gwm_features.get('best_cover_spot') else 999.0,
        gwm_features.get('best_cover_spot', {}).get('cover_rating', 0.0) if gwm_features.get('best_cover_spot') else 0.0,
        
        # Escape vector
        gwm_features.get('escape_vector', [0.0, 0.0])[0] if gwm_features.get('escape_vector') else 0.0,
        gwm_features.get('escape_vector', [0.0, 0.0])[1] if len(gwm_features.get('escape_vector', [])) > 1 else 0.0,
        
        # Stealth
        gwm_features.get('stealth_safety_score', 1.0),
        float(gwm_features.get('is_player_in_stealth_danger', False)),
        
        # Loot
        float(gwm_features.get('loot_opportunity_available', False)),
        gwm_features.get('nearest_loot_distance', 999.0),
        
        # Age
        gwm_features.get('snapshot_age', 0.0),
    ], dtype=np.float32)
    
    return arr


def pack_self_features(being_state: Any) -> np.ndarray:
    """
    Pack self-state from BeingState into flat numpy array.
    
    Args:
        being_state: BeingState object
    
    Returns:
        np.ndarray of shape [8] with packed features
    """
    # Extract from game_state or sensorimotor_state
    game_state = getattr(being_state, 'game_state', {})
    
    arr = np.array([
        game_state.get('player_health', 1.0),
        game_state.get('player_stamina', 1.0),
        game_state.get('player_magicka', 1.0),
        float(game_state.get('is_sneaking', False)),
        float(game_state.get('in_combat', False)),
        
        # Confidence (could be consciousness metrics)
        getattr(being_state, 'consciousness_phi', 0.5),
        
        # Additional context
        float(getattr(being_state, 'is_stuck', False)),
        getattr(being_state, 'action_success_rate', 0.5),
    ], dtype=np.float32)
    
    return arr


def pack_action_features(action: Any, action_type: str = "unknown") -> np.ndarray:
    """
    Pack action into flat numpy array.
    
    Args:
        action: Action object or dict
        action_type: Action type string
    
    Returns:
        np.ndarray of shape [16] with packed features
    """
    # Simple encoding: one-hot + continuous params
    # Extend this based on actual action schema
    
    action_types = [
        "move_forward", "move_backward", "move_left", "move_right",
        "attack", "block", "heal", "sneak",
        "activate", "jump", "sprint", "back"
    ]
    
    # One-hot encoding
    one_hot = np.zeros(12, dtype=np.float32)
    if action_type in action_types:
        one_hot[action_types.index(action_type)] = 1.0
    
    # Continuous params (magnitude, direction, duration, priority)
    continuous = np.array([
        getattr(action, 'magnitude', 1.0) if hasattr(action, 'magnitude') else 1.0,
        getattr(action, 'direction', 0.0) if hasattr(action, 'direction') else 0.0,
        getattr(action, 'duration', 0.5) if hasattr(action, 'duration') else 0.5,
        float(getattr(action, 'priority', 5)) / 10.0 if hasattr(action, 'priority') else 0.5,
    ], dtype=np.float32)
    
    arr = np.concatenate([one_hot, continuous])
    return arr


# ========================================
# Unpacking Functions: Tensor → Python
# ========================================

def decode_world_slice(world_vec: torch.Tensor) -> WorldSlice:
    """
    Decode world features from tensor to WorldSlice.
    
    Args:
        world_vec: [16] tensor from world_decoder
    
    Returns:
        WorldSlice object
    """
    vec = world_vec.cpu().numpy()
    
    # Apply appropriate activations
    threat_level = float(np.clip(vec[0], 0.0, 1.0))
    num_enemies = int(np.clip(vec[1], 0, 100))
    num_enemies_in_los = int(np.clip(vec[2], 0, 100))
    
    # Nearest enemy (optional)
    nearest_enemy_distance = float(vec[4]) if vec[4] < 900 else None
    nearest_enemy_bearing = float(vec[5]) if nearest_enemy_distance else None
    nearest_enemy_id = "enemy_decoded" if nearest_enemy_distance else None
    
    # Cover (optional)
    best_cover_distance = float(vec[7]) if vec[7] < 900 else None
    best_cover_id = "cover_decoded" if best_cover_distance else None
    
    # Escape vector
    escape_x = float(np.clip(vec[9], -1.0, 1.0))
    escape_y = float(np.clip(vec[10], -1.0, 1.0))
    
    # Stealth
    stealth_safety = float(np.clip(vec[11], 0.0, 1.0))
    
    # Loot
    loot_available = bool(vec[13] > 0.5)
    
    return WorldSlice(
        threat_level=threat_level,
        num_enemies=num_enemies,
        num_enemies_in_los=num_enemies_in_los,
        nearest_enemy_id=nearest_enemy_id,
        nearest_enemy_distance=nearest_enemy_distance,
        nearest_enemy_bearing_deg=nearest_enemy_bearing,
        best_cover_spot_id=best_cover_id,
        best_cover_distance=best_cover_distance,
        escape_vector_x=escape_x,
        escape_vector_y=escape_y,
        loot_available=loot_available
    )


def decode_self_slice(self_vec: torch.Tensor) -> SelfSlice:
    """
    Decode self-state from tensor to SelfSlice.
    
    Args:
        self_vec: [8] tensor from self_decoder
    
    Returns:
        SelfSlice object
    """
    vec = self_vec.cpu().numpy()
    
    return SelfSlice(
        health=float(np.clip(vec[0], 0.0, 1.0)),
        stamina=float(np.clip(vec[1], 0.0, 1.0)),
        magicka=float(np.clip(vec[2], 0.0, 1.0)),
        is_sneaking=bool(vec[3] > 0.5),
        in_combat=bool(vec[4] > 0.5),
        confidence=float(np.clip(vec[5], 0.0, 1.0))
    )


def decode_affect_slice(affect_vec: torch.Tensor) -> AffectSlice:
    """
    Decode affect from tensor to AffectSlice.
    
    Args:
        affect_vec: [4] tensor from affect_decoder
    
    Returns:
        AffectSlice object
    """
    vec = affect_vec.cpu().numpy()
    
    return AffectSlice(
        threat=float(np.clip(vec[0], 0.0, 1.0)),
        curiosity=float(np.clip(vec[1], 0.0, 1.0)),
        value_estimate=float(vec[2]),
        surprise=float(np.abs(vec[3]))
    )


# ========================================
# Main Update Function
# ========================================

def update_mwm_from_inputs(
    mwm_state: MentalWorldModelState,
    gwm_features: Optional[Dict[str, Any]],
    iwm_latent: Optional[np.ndarray],
    being_state: Any,
    mwm_module: Any,  # MentalWorldModelModule
    device: torch.device,
    action_for_prediction: Optional[Any] = None,
) -> MentalWorldModelState:
    """
    Update MWM state from current observations.
    
    This is the main integration point that:
    1. Packs GWM, IWM, self-state into tensors
    2. Calls mwm_module.encode() and decode()
    3. Optionally predicts next state given action
    4. Returns updated MentalWorldModelState
    
    Args:
        mwm_state: Current MWM state
        gwm_features: GWM features dict
        iwm_latent: IWM visual latent [768]
        being_state: BeingState object
        mwm_module: MentalWorldModelModule instance
        device: Torch device
        action_for_prediction: Optional action to predict next state
    
    Returns:
        Updated MentalWorldModelState
    """
    try:
        # Get previous latent (or initialize)
        if mwm_state.latent is not None:
            z_prev_np = np.array(mwm_state.latent, dtype=np.float32)
        else:
            z_prev_np = np.zeros(mwm_module.latent_dim, dtype=np.float32)
        
        z_prev = torch.from_numpy(z_prev_np).unsqueeze(0).to(device)
        
        # Pack inputs
        gwm_feats_np = pack_gwm_features(gwm_features)
        gwm_feats = torch.from_numpy(gwm_feats_np).unsqueeze(0).to(device)
        
        # Handle IWM latent
        if iwm_latent is not None:
            iwm_latent_np = iwm_latent.astype(np.float32)
        else:
            iwm_latent_np = np.zeros(768, dtype=np.float32)
        iwm_latent_t = torch.from_numpy(iwm_latent_np).unsqueeze(0).to(device)
        
        self_feats_np = pack_self_features(being_state)
        self_feats = torch.from_numpy(self_feats_np).unsqueeze(0).to(device)
        
        # Encode action if provided
        action_feats = None
        if action_for_prediction is not None:
            action_np = pack_action_features(
                action_for_prediction,
                action_type=str(action_for_prediction.action_type) if hasattr(action_for_prediction, 'action_type') else "unknown"
            )
            action_feats = torch.from_numpy(action_np).unsqueeze(0).to(device)
        
        # Forward pass
        with torch.no_grad():
            z_t, decoded, z_hat_t1 = mwm_module.forward(
                z_prev,
                gwm_feats,
                iwm_latent_t,
                self_feats,
                action_feats
            )
        
        # Create new state
        new_state = MentalWorldModelState(
            timestamp=time.time(),
            update_count=mwm_state.update_count + 1
        )
        
        # Set latent
        new_state.set_latent_array(z_t.squeeze(0).cpu().numpy())
        
        # Decode slices
        new_state.world = decode_world_slice(decoded["world"].squeeze(0))
        new_state.self_state = decode_self_slice(decoded["self"].squeeze(0))
        new_state.affect = decode_affect_slice(decoded["affect"].squeeze(0))
        
        # Keep hypotheses if they exist
        if mwm_state.hypotheses is not None:
            new_state.hypotheses = mwm_state.hypotheses
        
        return new_state
    
    except Exception as e:
        logger.error(f"[MWM] Update error: {e}")
        # Return unchanged state on error
        return mwm_state


# ========================================
# Prediction Utilities
# ========================================

def predict_action_outcome(
    mwm_state: MentalWorldModelState,
    action: Any,
    mwm_module: Any,
    device: torch.device
) -> Dict[str, Any]:
    """
    Mentally simulate taking an action.
    
    Args:
        mwm_state: Current MWM state
        action: Action to simulate
        mwm_module: MentalWorldModelModule
        device: Torch device
    
    Returns:
        Dict with predicted world, self, and affect slices
    """
    try:
        # Get current latent
        z_t_np = mwm_state.get_latent_array()
        if z_t_np is None:
            logger.warning("[MWM] No latent in state, cannot predict")
            return {}
        
        z_t = torch.from_numpy(z_t_np).unsqueeze(0).to(device)
        
        # Pack action
        action_np = pack_action_features(
            action,
            action_type=str(action.action_type) if hasattr(action, 'action_type') else "unknown"
        )
        action_feats = torch.from_numpy(action_np).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            z_hat = mwm_module.predict(z_t, action_feats)
            decoded = mwm_module.decode(z_hat)
        
        # Decode predictions
        predicted = {
            'world': decode_world_slice(decoded['world'].squeeze(0)),
            'self': decode_self_slice(decoded['self'].squeeze(0)),
            'affect': decode_affect_slice(decoded['affect'].squeeze(0))
        }
        
        return predicted
    
    except Exception as e:
        logger.error(f"[MWM] Prediction error: {e}")
        return {}


def score_action_with_mwm(
    action: Any,
    mwm_state: MentalWorldModelState,
    mwm_module: Any,
    device: torch.device
) -> float:
    """
    Score an action using mental simulation.
    
    Score = value_estimate - threat
    
    Args:
        action: Action to score
        mwm_state: Current MWM state
        mwm_module: MentalWorldModelModule
        device: Torch device
    
    Returns:
        Action score (higher = better)
    """
    predicted = predict_action_outcome(mwm_state, action, mwm_module, device)
    
    if not predicted or 'affect' not in predicted:
        return 0.0
    
    affect = predicted['affect']
    
    # Simple scoring: high value, low threat
    score = affect.value_estimate - affect.threat
    
    return float(score)
