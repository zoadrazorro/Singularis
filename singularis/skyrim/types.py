from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator
from singularis.agi_orchestrator import AGIConfig

class SceneType(str, Enum):
    """Enumerates the high-level types of scenes the agent can perceive in Skyrim."""
    OUTDOOR_WILDERNESS = "outdoor_wilderness"
    OUTDOOR_CITY = "outdoor_city"
    INDOOR_DUNGEON = "indoor_dungeon"
    INDOOR_BUILDING = "indoor_building"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    MAP = "map"
    UNKNOWN = "unknown"

class GameState(BaseModel):
    """Represents a snapshot of the current game state with validation."""
    
    # Player stats
    health: float = Field(100.0, ge=0.0, le=10000.0, description="Player's current health")
    magicka: float = Field(100.0, ge=0.0, description="Player's current magicka")
    stamina: float = Field(100.0, ge=0.0, description="Player's current stamina")
    level: int = Field(1, ge=1, description="Player's current level")

    # Position
    position: Optional[Tuple[float, float, float]] = None
    location_name: str = Field("Unknown", description="Name of current location")

    # Environment
    time_of_day: float = Field(12.0, ge=0.0, le=24.0, description="Game hour 0-24")
    weather: str = "clear"

    # NPCs
    nearby_npcs: List[str] = Field(default_factory=list)

    # Inventory/Economy
    gold: int = Field(0, ge=0)
    inventory_items: List[str] = Field(default_factory=list)

    # Quest state
    active_quests: List[str] = Field(default_factory=list)

    # Combat state
    in_combat: bool = False
    enemies_nearby: int = Field(0, ge=0)

    # Dialogue state
    in_dialogue: bool = False

    # Menu state
    in_menu: bool = False
    menu_type: str = ""

    # Action layer awareness
    current_action_layer: str = "Exploration"
    available_actions: List[str] = Field(default_factory=list)
    layer_transition_reason: str = ""
    
    # Scene
    scene: SceneType = SceneType.UNKNOWN
    
    # Metrics (simulated or real)
    movement_score: float = Field(0.0, ge=0.0, le=1.0)
    completed_quests: int = 0
    locations_discovered: int = 0
    npcs_met: int = 0
    mechanics_learned: int = 0
    equipment_quality: float = Field(0.0, ge=0.0, le=1.0)
    carry_weight: float = 0.0
    max_carry_weight: float = 0.0
    combat_win_rate: float = 0.0
    stealth_success_rate: float = 0.0
    persuasion_success_rate: float = 0.0
    average_skill_level: float = 0.0

    model_config = ConfigDict(arbitrary_types_allowed=True)

class SkyrimConfig(BaseModel):
    """Configuration settings for the Skyrim AGI with validation."""
    
    # Perception
    screen_region: Optional[Dict[str, int]] = None
    use_game_api: bool = False

    # Actions
    dry_run: bool = False
    custom_keys: Optional[Dict[str, str]] = None
    
    # Controller
    controller_deadzone_stick: float = Field(0.15, ge=0.0, le=1.0)
    controller_deadzone_trigger: float = Field(0.05, ge=0.0, le=1.0)
    controller_sensitivity: float = Field(1.0, gt=0.0)

    # Gameplay
    autonomous_duration: int = 3600
    cycle_interval: float = 2.0
    save_interval: int = 300
    
    # Async execution
    enable_async_reasoning: bool = True
    action_queue_size: int = 3
    perception_interval: float = 0.35
    max_concurrent_llm_calls: int = 4
    reasoning_throttle: float = 0.1
    
    # Fast reactive loop
    enable_fast_loop: bool = True
    fast_loop_interval: float = 2.0
    fast_loop_planning_timeout: float = 20.0
    fast_health_threshold: float = 30.0
    fast_danger_threshold: int = 3

    # Core models
    phi4_action_model: str = "microsoft/phi-4-mini-reasoning"
    huihui_cognition_model: str = "microsoft/phi-4-mini-reasoning:2"
    qwen3_vl_perception_model: str = "qwen/qwen3-vl-30b"

    # Learning
    surprise_threshold: float = 0.3
    exploration_weight: float = 0.5

    # Reinforcement Learning
    use_rl: bool = True
    rl_learning_rate: float = 0.01
    rl_epsilon_start: float = 0.3
    rl_train_freq: int = 5
    
    # Cloud-Enhanced RL
    use_cloud_rl: bool = True
    rl_memory_dir: str = "skyrim_rl_memory"
    rl_use_rag: bool = True
    use_curriculum_rag: bool = True
    rl_cloud_reward_shaping: bool = True
    rl_moe_evaluation: bool = True
    rl_save_frequency: int = 100

    # Hybrid LLM Architecture
    use_hybrid_llm: bool = True
    use_gemini_vision: bool = True
    gemini_model: str = "gemini-2.5-flash"
    use_claude_reasoning: bool = True
    claude_model: str = "claude-3-5-haiku-20241022"
    claude_sensorimotor_model: str = "claude-3-5-haiku-20241022"
    use_local_fallback: bool = False
    
    # MoE Architecture
    use_moe: bool = False
    num_gemini_experts: int = 2
    num_claude_experts: int = 1
    gemini_rpm_limit: int = 30
    claude_rpm_limit: int = 100
    
    # Parallel Mode
    use_parallel_mode: bool = False
    parallel_consensus_weight_moe: float = 0.6
    parallel_consensus_weight_hybrid: float = 0.4
    
    # Realtime Decision
    use_realtime_coordinator: bool = False
    realtime_decision_frequency: int = 10
    
    # Self-Reflection
    use_self_reflection: bool = False
    self_reflection_frequency: int = 50
    self_reflection_chain_length: int = 3
    
    # Reward Tuning
    use_reward_tuning: bool = False
    reward_tuning_frequency: int = 10
    
    # GPT-5 Orchestrator
    use_gpt5_orchestrator: bool = True
    gpt5_verbose: bool = True
    
    # Voice System
    enable_voice: bool = True
    voice_type: str = "NOVA"
    voice_min_priority: str = "HIGH"
    
    # Video Interpreter
    enable_video_interpreter: bool = True
    video_interpretation_mode: str = "COMPREHENSIVE"
    video_frame_rate: float = 0.5
    
    # Double Helix
    use_double_helix: bool = True
    self_improvement_gating: bool = True
    
    # Beta 1.0 Features
    enable_temporal_binding: bool = True
    temporal_window_size: int = 20
    temporal_timeout: float = 30.0
    enable_adaptive_memory: bool = True
    memory_decay_rate: float = 0.95
    memory_forget_threshold: float = 0.1
    enable_enhanced_coherence: bool = True
    enable_lumen_balance: bool = True
    lumen_severe_threshold: float = 0.5
    lumen_moderate_threshold: float = 0.7
    enable_unified_perception: bool = True
    enable_goal_generation: bool = True
    goal_novelty_threshold: float = 0.7
    enable_live_audio: bool = True
    live_audio_frequency: float = 5.0
    live_audio_style: str = "analytical"
    
    # HaackLang
    use_haacklang: bool = True
    haack_beat_interval: float = 0.1
    haack_verbose: bool = False
    scce_profile: str = "balanced"
    scce_frequency: int = 1
    
    # Infinity Engine
    use_infinity_engine: bool = True
    infinity_verbose: bool = False
    coherence_v2_threshold: float = 0.4
    meta_context_enabled: bool = True
    polyrhythmic_learning_enabled: bool = True
    rhythm_learning_rate: float = 0.01
    harmonic_attraction: float = 0.1
    memory_v2_enabled: bool = True
    memory_v2_capacity: int = 1000
    memory_consolidation_threshold: int = 3
    
    # Legacy
    enable_claude_meta: bool = False
    enable_gemini_vision: bool = False
    gemini_max_output_tokens: int = 768

    model_config = ConfigDict(arbitrary_types_allowed=True)
