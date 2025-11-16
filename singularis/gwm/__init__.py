"""
Game World Model (GWM) - Structured game state modeling

Maintains real-time structured representation of game world state.
Computes tactical features for decision-making.

Works alongside:
- IWM (vision world model): Visual latents and predictions
- SkyrimWorldModel (causal reasoning): High-level game logic

GWM provides:
- Entity tracking (player, NPCs, objects)
- Tactical features (threat level, cover, escape vectors)
- Structured state for ActionArbiter and LLM reasoning
"""

from .game_world_model import (
    GameWorldModel,
    GameWorldFeatures,
    EntityState,
    PlayerState,
    NPCState,
    ObjectState,
    CoverSpot
)

from .gwm_service import (
    EngineSnapshot,
    SnapshotUpdate,
    app as gwm_app
)

from .gwm_client import GWMClient

__all__ = [
    'GameWorldModel',
    'GameWorldFeatures',
    'EntityState',
    'PlayerState',
    'NPCState',
    'ObjectState',
    'CoverSpot',
    'EngineSnapshot',
    'SnapshotUpdate',
    'gwm_app',
    'GWMClient',
]
