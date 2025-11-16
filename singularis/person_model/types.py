"""
Person Model Types - Core data structures

Defines the complete PersonModel schema with identity, traits, values,
goals, social relationships, memory, capabilities, and constraints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time

# Import MWM types
from ..mwm.types import MentalWorldModelState


# ========================================
# Identity
# ========================================

class IdentityProfile(BaseModel):
    """
    Who I am.
    
    Stable identity information for the agent.
    """
    person_id: str = Field(..., description="Stable internal ID")
    name: str = Field(..., description="Display name")
    archetype: str = Field("generic", description="e.g., 'cautious_ranger', 'bandit_boss', 'mentor'")
    roles: List[str] = Field(default_factory=list, description="e.g., ['companion', 'healer']")
    backstory_summary: str = Field("", description="Short canonical blurb")
    avatar_tag: Optional[str] = Field(None, description="Link to model/skin/icon")
    
    class Config:
        json_schema_extra = {
            "example": {
                "person_id": "companion_001",
                "name": "Lydia",
                "archetype": "loyal_warrior",
                "roles": ["companion", "warrior", "follower"],
                "backstory_summary": "Sworn to carry your burdens",
                "avatar_tag": "lydia_armor_01"
            }
        }


# ========================================
# Traits (Personality / Temperament)
# ========================================

class TraitProfile(BaseModel):
    """
    How I tend to behave.
    
    0-1 sliders for behavioral style.
    """
    # Combat style
    aggression: float = Field(0.5, ge=0.0, le=1.0, description="Prefers to push vs avoid")
    caution: float = Field(0.5, ge=0.0, le=1.0, description="Risk aversion")
    
    # Approach
    stealth_preference: float = Field(0.5, ge=0.0, le=1.0, description="Prefers sneaking")
    exploration_drive: float = Field(0.5, ge=0.0, le=1.0, description="Likes to wander/investigate")
    
    # Decision style
    impulsiveness: float = Field(0.5, ge=0.0, le=1.0, description="Acts quickly vs deliberates")
    sociability: float = Field(0.5, ge=0.0, le=1.0, description="Talks/interacts vs stays quiet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "aggression": 0.7,
                "caution": 0.3,
                "stealth_preference": 0.2,
                "exploration_drive": 0.6,
                "impulsiveness": 0.4,
                "sociability": 0.8
            }
        }


# ========================================
# Values & Goals
# ========================================

class ValueProfile(BaseModel):
    """
    What I care about.
    
    Normalized weights for internal scoring.
    """
    # Core drives
    survival_priority: float = Field(0.8, ge=0.0, le=1.0, description="Self-preservation")
    damage_priority: float = Field(0.5, ge=0.0, le=1.0, description="Deal damage to enemies")
    
    # Social
    protect_allies: float = Field(0.7, ge=0.0, le=1.0, description="Keep allies alive")
    care_for_civilians: float = Field(0.5, ge=0.0, le=1.0, description="Protect innocents")
    obedience_to_player: float = Field(0.6, ge=0.0, le=1.0, description="Follow player commands")
    
    # Exploration & progression
    greed_for_loot: float = Field(0.4, ge=0.0, le=1.0, description="Desire for items/gold")
    curiosity_drive: float = Field(0.5, ge=0.0, le=1.0, description="Investigate unknown")
    
    class Config:
        json_schema_extra = {
            "example": {
                "survival_priority": 0.9,
                "protect_allies": 0.8,
                "obedience_to_player": 0.9,
                "greed_for_loot": 0.2
            }
        }


class Goal(BaseModel):
    """
    A single goal/intention.
    """
    id: str = Field(..., description="Goal ID")
    description: str = Field(..., description="Natural language description")
    priority: float = Field(0.5, ge=0.0, le=1.0, description="Importance 0-1")
    deadline: Optional[float] = Field(None, description="Game time deadline")
    status: str = Field("active", description="'active', 'achieved', 'failed'")
    created_at: float = Field(default_factory=time.time, description="Creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "goal_protect_player",
                "description": "Keep the player alive during combat",
                "priority": 0.9,
                "status": "active"
            }
        }


class GoalState(BaseModel):
    """
    Collection of active goals at different time scales.
    """
    long_term: List[Goal] = Field(default_factory=list, description="Factional, storyline, life goals")
    mid_term: List[Goal] = Field(default_factory=list, description="Dungeon/quest level")
    current_intentions: List[Goal] = Field(default_factory=list, description="Currently pursuing")
    
    def add_goal(self, goal: Goal, scope: str = "current"):
        """Add a goal to appropriate scope."""
        if scope == "long_term":
            self.long_term.append(goal)
        elif scope == "mid_term":
            self.mid_term.append(goal)
        else:
            self.current_intentions.append(goal)
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals across all scopes."""
        return [g for g in (self.long_term + self.mid_term + self.current_intentions) 
                if g.status == "active"]
    
    def get_highest_priority_goal(self) -> Optional[Goal]:
        """Get the highest priority active goal."""
        active = self.get_active_goals()
        if not active:
            return None
        return max(active, key=lambda g: g.priority)


# ========================================
# Social Model (Relationships)
# ========================================

class Relationship(BaseModel):
    """
    How I see another entity.
    """
    other_id: str = Field(..., description="PersonModel ID or game entity ID")
    role: str = Field("neutral", description="'player', 'follower', 'enemy', 'mentor', etc.")
    
    # Relationship dimensions
    trust: float = Field(0.5, ge=0.0, le=1.0, description="How much I trust them")
    affection: float = Field(0.0, ge=-1.0, le=1.0, description="Hate (-1) to love (1)")
    fear: float = Field(0.0, ge=0.0, le=1.0, description="How much I fear them")
    respect: float = Field(0.5, ge=0.0, le=1.0, description="How much I respect them")
    
    # Meta
    last_interaction_time: float = Field(0.0, description="Last interaction timestamp")
    interaction_count: int = Field(0, description="Number of interactions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "other_id": "player",
                "role": "leader",
                "trust": 0.9,
                "affection": 0.7,
                "fear": 0.1,
                "respect": 0.8
            }
        }


class SocialModel(BaseModel):
    """
    How I see others.
    
    Collection of relationships.
    """
    relationships: List[Relationship] = Field(default_factory=list)
    
    def get_relationship(self, other_id: str) -> Optional[Relationship]:
        """Get relationship with specific entity."""
        for rel in self.relationships:
            if rel.other_id == other_id:
                return rel
        return None
    
    def add_or_update_relationship(self, rel: Relationship):
        """Add or update a relationship."""
        existing = self.get_relationship(rel.other_id)
        if existing:
            # Update existing
            self.relationships.remove(existing)
        self.relationships.append(rel)
    
    def get_allies(self) -> List[Relationship]:
        """Get all allies (high trust + affection)."""
        return [r for r in self.relationships 
                if r.trust > 0.6 and r.affection > 0.3]
    
    def get_enemies(self) -> List[Relationship]:
        """Get all enemies (low trust, negative affection)."""
        return [r for r in self.relationships 
                if r.trust < 0.4 or r.affection < -0.3]


# ========================================
# Memory
# ========================================

class EpisodicMemoryRef(BaseModel):
    """
    Reference to an episodic memory.
    
    Actual content lives in DB/vector store.
    """
    id: str = Field(..., description="Memory ID")
    timestamp: float = Field(..., description="When it happened")
    summary: str = Field("", description="Short summary")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="How important")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "mem_ep_001",
                "timestamp": 12345.67,
                "summary": "Player saved me from bandits",
                "importance": 0.9
            }
        }


class SemanticMemoryRef(BaseModel):
    """
    Reference to semantic memory.
    
    Learned patterns/facts.
    """
    id: str = Field(..., description="Memory ID")
    topic: str = Field(..., description="Topic category")
    summary: str = Field("", description="Short summary")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in this knowledge")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "mem_sem_001",
                "topic": "combat_tactics",
                "summary": "Flanking enemies is effective",
                "confidence": 0.8
            }
        }


class MemoryProfile(BaseModel):
    """
    What I remember.
    
    References to episodic and semantic memory stores.
    """
    episodic: List[EpisodicMemoryRef] = Field(default_factory=list, description="Episodic memories")
    semantic: List[SemanticMemoryRef] = Field(default_factory=list, description="Semantic patterns")
    
    def add_episodic(self, mem: EpisodicMemoryRef):
        """Add episodic memory."""
        self.episodic.append(mem)
        # Keep only most recent N
        if len(self.episodic) > 100:
            # Sort by importance * recency, keep top 100
            self.episodic.sort(key=lambda m: m.importance * (1.0 / (time.time() - m.timestamp + 1)), reverse=True)
            self.episodic = self.episodic[:100]
    
    def add_semantic(self, mem: SemanticMemoryRef):
        """Add semantic memory."""
        self.semantic.append(mem)
    
    def get_recent_episodic(self, n: int = 5) -> List[EpisodicMemoryRef]:
        """Get N most recent episodic memories."""
        sorted_mem = sorted(self.episodic, key=lambda m: m.timestamp, reverse=True)
        return sorted_mem[:n]


# ========================================
# Capabilities & Constraints
# ========================================

class CapabilityProfile(BaseModel):
    """
    What I can do.
    
    Defines available actions/skills.
    """
    # Basic combat
    can_use_melee: bool = Field(True, description="Can use melee weapons")
    can_use_ranged: bool = Field(True, description="Can use bows/crossbows")
    can_use_magic: bool = Field(False, description="Can cast spells")
    
    # Stealth & interaction
    can_sneak: bool = Field(True, description="Can enter stealth")
    can_pickpocket: bool = Field(False, description="Can pickpocket")
    can_lockpick: bool = Field(False, description="Can pick locks")
    
    # Special
    special_abilities: List[str] = Field(default_factory=list, description="Special abilities")
    
    # Skill levels (0-1)
    combat_skill: float = Field(0.5, ge=0.0, le=1.0, description="Combat proficiency")
    stealth_skill: float = Field(0.5, ge=0.0, le=1.0, description="Stealth proficiency")
    magic_skill: float = Field(0.5, ge=0.0, le=1.0, description="Magic proficiency")
    
    class Config:
        json_schema_extra = {
            "example": {
                "can_use_melee": True,
                "can_use_magic": False,
                "can_sneak": True,
                "combat_skill": 0.8,
                "special_abilities": ["shield_bash", "power_attack"]
            }
        }


class ConstraintProfile(BaseModel):
    """
    What I must not do.
    
    Hard guardrails on behavior.
    """
    # Social constraints
    allow_friendly_fire: bool = Field(False, description="Can damage allies")
    harm_civilians: bool = Field(False, description="Can harm innocents")
    betray_player: bool = Field(False, description="Can betray the player")
    
    # Legal/moral
    break_law: bool = Field(True, description="Can commit crimes")
    obey_player_orders: bool = Field(True, description="Must follow player commands")
    
    # Self-preservation
    risk_self_sacrifice: bool = Field(False, description="Will die for others")
    
    class Config:
        json_schema_extra = {
            "example": {
                "allow_friendly_fire": False,
                "harm_civilians": False,
                "betray_player": False,
                "obey_player_orders": True,
                "risk_self_sacrifice": True
            }
        }


# ========================================
# Person Model (Complete)
# ========================================

class PersonModel(BaseModel):
    """
    Complete person model - the top-level agent abstraction.
    
    This is what ActionArbiter and LLM should think of as "the agent".
    Wraps MWM (state of mind) and adds identity, personality, values,
    goals, social relationships, memory, capabilities, and constraints.
    """
    # Who I am
    identity: IdentityProfile
    
    # How I see the world right now (state of mind)
    mwm: MentalWorldModelState
    
    # How I tend to behave & what I care about
    traits: TraitProfile = Field(default_factory=TraitProfile)
    values: ValueProfile = Field(default_factory=ValueProfile)
    goals: GoalState = Field(default_factory=GoalState)
    
    # How I see others
    social: SocialModel = Field(default_factory=SocialModel)
    
    # What I remember
    memory: MemoryProfile = Field(default_factory=MemoryProfile)
    
    # What I can do and what I must not do
    capabilities: CapabilityProfile = Field(default_factory=CapabilityProfile)
    constraints: ConstraintProfile = Field(default_factory=ConstraintProfile)
    
    # Meta
    created_at: float = Field(default_factory=time.time)
    last_updated: float = Field(default_factory=time.time)
    
    def update_timestamp(self):
        """Update last_updated timestamp."""
        self.last_updated = time.time()
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        return f"""PersonModel: {self.identity.name} ({self.identity.archetype})
  Roles: {', '.join(self.identity.roles)}
  Traits: aggression={self.traits.aggression:.2f}, caution={self.traits.caution:.2f}
  Active goals: {len(self.goals.get_active_goals())}
  Relationships: {len(self.social.relationships)}
  Memories: {len(self.memory.episodic)} episodic, {len(self.memory.semantic)} semantic
  MWM: threat={self.mwm.affect.threat if self.mwm.affect else 0:.2f}, value={self.mwm.affect.value_estimate if self.mwm.affect else 0:.2f}
"""
    
    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "identity": {
                    "person_id": "companion_lydia",
                    "name": "Lydia",
                    "archetype": "loyal_warrior"
                },
                "traits": {"aggression": 0.7, "caution": 0.5},
                "values": {"survival_priority": 0.9, "protect_allies": 0.9},
                "goals": {"current_intentions": [{"id": "protect_player", "priority": 0.9}]}
            }
        }
