"""
GWM Service - FastAPI microservice for game world model

Provides endpoints:
- POST /snapshot: Receive engine snapshot
- GET /features: Get current tactical features
- GET /entities: Get entity list
- GET /health: Service health

Follows Singularis service patterns (FastAPI, async, loguru).
"""

import asyncio
import time
import os
from typing import Optional, List, Dict, Any
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from loguru import logger

from .game_world_model import (
    GameWorldModel,
    GameWorldFeatures,
    PlayerState,
    NPCState,
    ObjectState,
    CoverSpot
)


# ========================================
# Request/Response Models
# ========================================

class EngineSnapshot(BaseModel):
    """Engine snapshot from game."""
    timestamp: float = Field(..., description="Game time")
    world_time: Optional[float] = Field(None, description="In-game time")
    cell_name: Optional[str] = Field(None, description="Current cell/location")
    is_interior: Optional[bool] = Field(False, description="Interior cell")
    
    player: Optional[Dict[str, Any]] = Field(None, description="Player state")
    npcs: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="NPC states")
    objects: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Object states")
    cover_spots_raw: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Cover spots")
    recent_events: Optional[List[str]] = Field(default_factory=list, description="Recent game events")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 12345.67,
                "cell_name": "BleakFallsBarrow01",
                "is_interior": True,
                "player": {
                    "id": "player",
                    "pos": [0.0, 0.0, 0.0],
                    "facing_yaw": 90.0,
                    "health": 0.74,
                    "in_combat": True
                },
                "npcs": [{
                    "id": "bandit_001",
                    "pos": [10.0, 2.0, 0.0],
                    "health": 0.62,
                    "is_enemy": True,
                    "distance_to_player": 12.3
                }]
            }
        }


class SnapshotUpdate(BaseModel):
    """Response from snapshot update."""
    success: bool
    features_computed: bool
    timestamp: float
    entities_tracked: Dict[str, int]


class FeaturesResponse(BaseModel):
    """Tactical features response."""
    features: Dict[str, Any]
    timestamp: float
    snapshot_age: float


class EntitiesResponse(BaseModel):
    """Entity list response."""
    player: Optional[Dict[str, Any]]
    npcs: List[Dict[str, Any]]
    objects: List[Dict[str, Any]]
    cover_spots: List[Dict[str, Any]]
    timestamp: float


class HealthResponse(BaseModel):
    """Service health."""
    status: str
    uptime_seconds: float
    total_snapshots: int
    total_features_computed: int
    current_entities: Dict[str, int]
    snapshot_age: float


# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="GWM Game World Model Service",
    description="Structured game state modeling for Singularis/SkyrimAGI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Global State
# ========================================

class ServiceState:
    """Service state."""
    def __init__(self):
        self.gwm = GameWorldModel()
        self.start_time = time.time()
        self.total_snapshots = 0


state = ServiceState()


# ========================================
# Startup/Shutdown
# ========================================

@app.on_event("startup")
async def startup():
    """Initialize GWM service."""
    logger.info("[GWM-SERVICE] Starting Game World Model Service...")
    logger.info("[GWM-SERVICE] Endpoints: /snapshot, /features, /entities, /health")
    logger.info("[GWM-SERVICE] Ready to receive engine snapshots")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup."""
    logger.info("[GWM-SERVICE] Shutting down GWM service")


# ========================================
# Endpoints
# ========================================

@app.post("/snapshot", response_model=SnapshotUpdate)
async def receive_snapshot(snapshot: EngineSnapshot):
    """
    Receive game engine snapshot and update world model.
    
    This is the main endpoint that receives structured game state
    from the engine bridge.
    """
    try:
        # Update world model
        snapshot_dict = snapshot.dict()
        state.gwm.update_from_snapshot(snapshot_dict)
        state.total_snapshots += 1
        
        # Compute features
        features = state.gwm.compute_features()
        
        gwm_stats = state.gwm.get_stats()
        
        return SnapshotUpdate(
            success=True,
            features_computed=True,
            timestamp=time.time(),
            entities_tracked=gwm_stats['num_entities']
        )
    
    except Exception as e:
        logger.error(f"[GWM-SERVICE] Snapshot processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features", response_model=FeaturesResponse)
async def get_features():
    """
    Get current tactical features.
    
    Returns the latest computed GameWorldFeatures.
    """
    try:
        if state.gwm.current_features is None:
            # Compute fresh features
            features = state.gwm.compute_features()
        else:
            features = state.gwm.current_features
        
        return FeaturesResponse(
            features=features.to_dict(),
            timestamp=time.time(),
            snapshot_age=features.snapshot_age
        )
    
    except Exception as e:
        logger.error(f"[GWM-SERVICE] Features error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entities", response_model=EntitiesResponse)
async def get_entities():
    """
    Get current entity states.
    
    Returns player, NPCs, objects, and cover spots.
    """
    try:
        return EntitiesResponse(
            player=asdict(state.gwm.player) if state.gwm.player else None,
            npcs=[asdict(npc) for npc in state.gwm.npcs.values()],
            objects=[asdict(obj) for obj in state.gwm.objects.values()],
            cover_spots=[asdict(cover) for cover in state.gwm.cover_spots.values()],
            timestamp=time.time()
        )
    
    except Exception as e:
        logger.error(f"[GWM-SERVICE] Entities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check."""
    gwm_stats = state.gwm.get_stats()
    
    return HealthResponse(
        status="ok",
        uptime_seconds=time.time() - state.start_time,
        total_snapshots=state.total_snapshots,
        total_features_computed=gwm_stats['total_features_computed'],
        current_entities=gwm_stats['num_entities'],
        snapshot_age=gwm_stats['snapshot_age']
    )


# ========================================
# Main
# ========================================

def main():
    """Run service."""
    port = int(os.getenv('GWM_SERVICE_PORT', '8002'))
    host = os.getenv('GWM_SERVICE_HOST', '0.0.0.0')
    
    logger.info(f"[GWM-SERVICE] Starting on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
