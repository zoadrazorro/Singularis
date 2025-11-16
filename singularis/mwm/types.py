"""
MWM Types - Data structures for Mental World Model

Defines the structured representation of the agent's mental state.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import numpy as np


# ========================================
# Decoded Slices
# ========================================

class WorldSlice(BaseModel):
    """
    Decoded world features from mental latent.
    
    Combines GWM structured state with mental model's interpretation.
    """
    # Threat assessment
    threat_level: float = Field(0.0, ge=0.0, le=1.0, description="Overall danger")
    num_enemies: int = Field(0, ge=0, description="Total enemies")
    num_enemies_in_los: int = Field(0, ge=0, description="Enemies with line of sight")
    
    # Nearest enemy
    nearest_enemy_id: Optional[str] = Field(None, description="Nearest enemy ID")
    nearest_enemy_distance: Optional[float] = Field(None, description="Distance to nearest enemy (m)")
    nearest_enemy_bearing_deg: Optional[float] = Field(None, description="Bearing to enemy (degrees)")
    
    # Cover & escape
    best_cover_spot_id: Optional[str] = Field(None, description="Best cover ID")
    best_cover_distance: Optional[float] = Field(None, description="Distance to cover (m)")
    escape_vector_x: float = Field(0.0, description="Escape direction X")
    escape_vector_y: float = Field(0.0, description="Escape direction Y")
    
    # Opportunities
    loot_available: bool = Field(False, description="Safe loot opportunity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "threat_level": 0.75,
                "num_enemies": 2,
                "num_enemies_in_los": 1,
                "nearest_enemy_id": "bandit_001",
                "nearest_enemy_distance": 12.3,
                "escape_vector_x": -0.8,
                "escape_vector_y": -0.6
            }
        }


class SelfSlice(BaseModel):
    """
    Decoded self-state features from mental latent.
    
    Agent's understanding of its own state.
    """
    # Resources
    health: float = Field(1.0, ge=0.0, le=1.0, description="Health 0-1")
    stamina: float = Field(1.0, ge=0.0, le=1.0, description="Stamina 0-1")
    magicka: float = Field(1.0, ge=0.0, le=1.0, description="Magicka 0-1")
    
    # Mode
    is_sneaking: bool = Field(False, description="Currently sneaking")
    in_combat: bool = Field(False, description="In combat")
    
    # Confidence
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Self-assessed confidence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "health": 0.65,
                "stamina": 0.40,
                "magicka": 0.80,
                "is_sneaking": True,
                "in_combat": False,
                "confidence": 0.72
            }
        }


class AffectSlice(BaseModel):
    """
    Decoded affective/motivational features from mental latent.
    
    The agent's emotional and motivational state.
    """
    # Core affects
    threat: float = Field(0.0, ge=0.0, le=1.0, description="Perceived threat")
    curiosity: float = Field(0.0, ge=0.0, le=1.0, description="Drive to explore/investigate")
    value_estimate: float = Field(0.0, description="Expected long-term value of current state")
    
    # Prediction
    surprise: float = Field(0.0, ge=0.0, description="Prediction error / surprise")
    
    class Config:
        json_schema_extra = {
            "example": {
                "threat": 0.72,
                "curiosity": 0.15,
                "value_estimate": 0.45,
                "surprise": 1.2
            }
        }


class Hypothesis(BaseModel):
    """
    Single hypothesis about future state.
    
    Result of mentally simulating an action sequence.
    """
    horizon_steps: int = Field(1, ge=1, description="Steps into future")
    expected_threat: float = Field(0.0, ge=0.0, le=1.0, description="Expected threat level")
    expected_value: float = Field(0.0, description="Expected value")
    action_sequence: Optional[List[str]] = Field(None, description="Actions to reach this state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "horizon_steps": 3,
                "expected_threat": 0.4,
                "expected_value": 0.65,
                "action_sequence": ["move_forward", "attack", "block"]
            }
        }


class HypothesisSlice(BaseModel):
    """
    Collection of hypotheses about future states.
    
    Agent's mental simulations of possible futures.
    """
    rollouts: List[Hypothesis] = Field(default_factory=list, description="Future hypotheses")
    
    def add_hypothesis(self, hyp: Hypothesis):
        """Add a hypothesis."""
        self.rollouts.append(hyp)
    
    def clear(self):
        """Clear all hypotheses."""
        self.rollouts.clear()


# ========================================
# Mental World Model State
# ========================================

class MentalWorldModelState(BaseModel):
    """
    Complete mental state representation.
    
    Contains:
    - latent: Raw latent vector (numpy array)
    - world: Decoded world features
    - self: Decoded self-state
    - affect: Decoded affective state
    - hypotheses: Future predictions
    """
    # Latent vector (numpy array serialized as list for Pydantic)
    latent: Optional[List[float]] = Field(None, description="Mental latent vector")
    
    # Decoded slices
    world: Optional[WorldSlice] = None
    self_state: Optional[SelfSlice] = None  # Renamed to avoid Python keyword
    affect: Optional[AffectSlice] = None
    hypotheses: Optional[HypothesisSlice] = None
    
    # Meta
    timestamp: float = Field(0.0, description="When this state was created")
    update_count: int = Field(0, description="Number of updates")
    
    def get_latent_array(self) -> Optional[np.ndarray]:
        """Get latent as numpy array."""
        if self.latent is None:
            return None
        return np.array(self.latent, dtype=np.float32)
    
    def set_latent_array(self, arr: np.ndarray):
        """Set latent from numpy array."""
        self.latent = arr.tolist()
    
    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "latent": [0.1, 0.2, 0.3],  # ... 256-d
                "world": {"threat_level": 0.75, "num_enemies": 2},
                "self_state": {"health": 0.65, "confidence": 0.72},
                "affect": {"threat": 0.72, "curiosity": 0.15},
                "timestamp": 12345.67,
                "update_count": 42
            }
        }


# ========================================
# Person Model (Higher-level)
# ========================================

class TraitProfile(BaseModel):
    """
    Personality traits that modulate behavior.
    
    These are stable characteristics that influence decision-making.
    """
    aggression: float = Field(0.5, ge=0.0, le=1.0, description="Tendency to engage in combat")
    caution: float = Field(0.5, ge=0.0, le=1.0, description="Risk aversion")
    stealth_preference: float = Field(0.5, ge=0.0, le=1.0, description="Preference for stealth")
    exploration_drive: float = Field(0.5, ge=0.0, le=1.0, description="Curiosity / exploration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "aggression": 0.3,
                "caution": 0.7,
                "stealth_preference": 0.8,
                "exploration_drive": 0.6
            }
        }


class MemoryProfile(BaseModel):
    """
    Memory characteristics and statistics.
    
    Placeholder for future memory system integration.
    """
    episodic_capacity: int = Field(100, description="Episodic memory capacity")
    semantic_patterns: int = Field(0, description="Learned semantic patterns")
    consolidation_count: int = Field(0, description="Memory consolidations performed")


class CapabilityProfile(BaseModel):
    """
    Agent's capabilities and skill levels.
    
    Placeholder for future skill system integration.
    """
    combat_skill: float = Field(0.5, ge=0.0, le=1.0, description="Combat proficiency")
    stealth_skill: float = Field(0.5, ge=0.0, le=1.0, description="Stealth proficiency")
    magic_skill: float = Field(0.5, ge=0.0, le=1.0, description="Magic proficiency")


class PersonModel(BaseModel):
    """
    Complete person model: MWM + traits + memory + capabilities.
    
    This is the highest-level representation of the agent as a "person"
    with mental state, personality, memory, and skills.
    """
    # Core mental state
    mwm: MentalWorldModelState
    
    # Personality
    traits: TraitProfile = Field(default_factory=TraitProfile)
    
    # Memory (placeholder)
    memory: MemoryProfile = Field(default_factory=MemoryProfile)
    
    # Capabilities (placeholder)
    capabilities: CapabilityProfile = Field(default_factory=CapabilityProfile)
    
    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "mwm": {"latent": [...], "world": {...}},
                "traits": {"aggression": 0.3, "caution": 0.7},
                "memory": {"episodic_capacity": 100},
                "capabilities": {"combat_skill": 0.6}
            }
        }
