"""
Singularis Beta v2 - Configuration Template

Copy this file and customize for your needs.

Usage:
    1. Copy this file: cp beta_v2_config_template.py my_config.py
    2. Edit my_config.py with your settings
    3. Import in run_singularis_beta_v2.py
"""

from singularis.skyrim.config import SkyrimConfig


def create_standard_config() -> SkyrimConfig:
    """
    Standard configuration - balanced performance.
    
    Good for: Most use cases, 30-60 minute sessions
    """
    config = SkyrimConfig()
    
    # Timing
    config.cycle_interval = 2.0  # seconds between cycles
    
    # Features
    config.enable_voice = True
    config.enable_video_interpreter = True
    config.use_wolfram_telemetry = True
    config.use_gpt5_orchestrator = True
    config.use_double_helix = True
    
    # Voice settings
    config.voice_type = "NOVA"  # Alloy, Echo, Fable, Onyx, Nova, Shimmer
    config.voice_min_priority = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    
    # Video settings
    config.video_interpretation_mode = "COMPREHENSIVE"
    config.video_frame_rate = 0.5  # frames per second
    
    # API limits
    config.gemini_rpm_limit = 15
    config.openai_rpm_limit = 50
    
    # Experts
    config.num_gemini_experts = 1
    config.num_openai_experts = 2
    
    # Verbose
    config.verbose = True
    
    return config


def create_fast_config() -> SkyrimConfig:
    """
    Fast configuration - minimal API usage.
    
    Good for: Testing, development, debugging
    """
    config = SkyrimConfig()
    
    # Timing - faster cycles
    config.cycle_interval = 1.0
    
    # Disable expensive features
    config.enable_voice = False
    config.enable_video_interpreter = False
    config.use_wolfram_telemetry = False
    
    # Minimal experts
    config.num_gemini_experts = 1
    config.num_openai_experts = 1
    
    # Verbose for debugging
    config.verbose = True
    
    return config


def create_conservative_config() -> SkyrimConfig:
    """
    Conservative configuration - low API usage.
    
    Good for: Free tier API limits, long sessions, production
    """
    config = SkyrimConfig()
    
    # Timing - slower to reduce API calls
    config.cycle_interval = 5.0
    
    # Reduced API limits
    config.gemini_rpm_limit = 10
    config.openai_rpm_limit = 30
    
    # Minimal experts
    config.num_gemini_experts = 1
    config.num_openai_experts = 1
    
    # Keep essential features
    config.enable_voice = False
    config.enable_video_interpreter = False
    config.use_wolfram_telemetry = True  # Only every 20 cycles
    
    config.verbose = False  # Reduce console spam
    
    return config


def create_premium_config() -> SkyrimConfig:
    """
    Premium configuration - all features enabled.
    
    Good for: Paid API tiers, demonstrations, full experience
    Requires: High API limits
    """
    config = SkyrimConfig()
    
    # Timing - responsive
    config.cycle_interval = 1.5
    
    # All features enabled
    config.enable_voice = True
    config.enable_video_interpreter = True
    config.use_wolfram_telemetry = True
    config.use_gpt5_orchestrator = True
    config.use_double_helix = True
    config.self_improvement_gating = True
    
    # Voice settings - high quality
    config.voice_type = "NOVA"
    config.voice_min_priority = "MEDIUM"  # Speak more often
    
    # Video settings - comprehensive
    config.video_interpretation_mode = "COMPREHENSIVE"
    config.video_frame_rate = 1.0  # 1 FPS
    
    # Higher API limits (requires paid tier)
    config.gemini_rpm_limit = 30
    config.openai_rpm_limit = 100
    
    # More experts
    config.num_gemini_experts = 2
    config.num_openai_experts = 3
    
    # Verbose
    config.verbose = True
    
    return config


def create_research_config() -> SkyrimConfig:
    """
    Research configuration - maximum data collection.
    
    Good for: Research, analysis, data collection
    """
    config = SkyrimConfig()
    
    # Timing - balanced
    config.cycle_interval = 3.0
    
    # Wolfram for analysis
    config.use_wolfram_telemetry = True
    
    # All systems for complete data
    config.use_gpt5_orchestrator = True
    config.use_double_helix = True
    config.self_improvement_gating = True
    
    # Video for visual analysis
    config.enable_video_interpreter = True
    config.video_interpretation_mode = "COMPREHENSIVE"
    config.video_frame_rate = 0.5
    
    # Voice can be disabled for cleaner data
    config.enable_voice = False
    
    # Moderate API usage
    config.gemini_rpm_limit = 15
    config.openai_rpm_limit = 50
    
    # Verbose for detailed logs
    config.verbose = True
    
    return config


def create_silent_config() -> SkyrimConfig:
    """
    Silent configuration - no voice or video, core systems only.
    
    Good for: Background operation, server deployment
    """
    config = SkyrimConfig()
    
    # Timing
    config.cycle_interval = 2.5
    
    # Core systems only
    config.enable_voice = False
    config.enable_video_interpreter = False
    config.use_wolfram_telemetry = True
    config.use_gpt5_orchestrator = True
    
    # Normal API limits
    config.gemini_rpm_limit = 15
    config.openai_rpm_limit = 50
    
    # Quiet operation
    config.verbose = False
    
    return config


# Configuration presets
CONFIGS = {
    'standard': create_standard_config,
    'fast': create_fast_config,
    'conservative': create_conservative_config,
    'premium': create_premium_config,
    'research': create_research_config,
    'silent': create_silent_config,
}


def get_config(preset: str = 'standard') -> SkyrimConfig:
    """
    Get a configuration preset.
    
    Args:
        preset: One of 'standard', 'fast', 'conservative', 'premium', 'research', 'silent'
        
    Returns:
        SkyrimConfig instance
    """
    if preset not in CONFIGS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(CONFIGS.keys())}")
    
    return CONFIGS[preset]()


if __name__ == '__main__':
    # Test configurations
    print("Testing configuration presets...\n")
    
    for name, create_func in CONFIGS.items():
        print(f"[{name.upper()}]")
        config = create_func()
        print(f"  Cycle interval: {config.cycle_interval}s")
        print(f"  Voice: {config.enable_voice}")
        print(f"  Video: {config.enable_video_interpreter}")
        print(f"  Wolfram: {config.use_wolfram_telemetry}")
        print(f"  Gemini RPM: {config.gemini_rpm_limit}")
        print()
    
    print("All presets validated ✓")
