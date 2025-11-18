"""
Runtime Flags - Global configuration switches for Singularis

This module provides global runtime flags that control system behavior.
These flags are set via environment variables and used throughout the system.

Environment Variables:
    SINGULARIS_LOCAL_ONLY: Set to "1" to enforce local-only LLM mode (no cloud API calls)
    NODE_ROLE: Node role in cluster (inference_primary, inference_secondary, lifeops_core)
"""

import os

# ════════════════════════════════════════════════════════════════════════
# LOCAL-ONLY MODE
# ════════════════════════════════════════════════════════════════════════

LOCAL_ONLY_LLM = os.getenv("SINGULARIS_LOCAL_ONLY", "0") == "1"
"""
If True, all LLM traffic must use local endpoints (LM Studio, vLLM, etc.).
No HTTP calls to OpenAI, Anthropic, Gemini, Perplexity, or OpenRouter.

When enabled:
- OpenAIClient will only work with localhost/LAN URLs
- UnifiedConsciousnessLayer will route to local LM Studio endpoint
- Cloud API fallbacks are disabled
- System will fail explicitly if local endpoint is unavailable

Set via: export SINGULARIS_LOCAL_ONLY=1
"""

# ════════════════════════════════════════════════════════════════════════
# NODE ROLES (for cluster distribution)
# ════════════════════════════════════════════════════════════════════════

NODE_ROLE = os.getenv("NODE_ROLE", "standalone")
"""
Node role in Sephirot cluster:
- 'inference_primary': MacBook Pro - primary LM Studio inference server
- 'inference_secondary': NVIDIA laptop - optional secondary inference
- 'lifeops_core': AMD box - runs LifeOps orchestration + Singularis AGI
- 'standalone': Single-machine mode (default)

Set via: export NODE_ROLE=inference_primary
"""

# ════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════

def is_local_url(url: str) -> bool:
    """
    Check if a URL points to a local/LAN endpoint.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is local/LAN, False otherwise
    """
    if not url:
        return False
        
    url_lower = url.lower()
    
    # Check for localhost
    if "localhost" in url_lower or "127.0.0.1" in url_lower:
        return True
    
    # Check for private network ranges
    # 192.168.x.x (common home/office LANs)
    if "192.168." in url:
        return True
    
    # 10.x.x.x (private network)
    if url.startswith("http://10.") or url.startswith("https://10."):
        return True
    
    # 172.16.x.x - 172.31.x.x (private network)
    for i in range(16, 32):
        if f"172.{i}." in url:
            return True
    
    return False


def get_runtime_info() -> dict:
    """
    Get current runtime configuration info.
    
    Returns:
        Dict with runtime flags and their values
    """
    return {
        "local_only_llm": LOCAL_ONLY_LLM,
        "node_role": NODE_ROLE,
        "singularis_local_only_env": os.getenv("SINGULARIS_LOCAL_ONLY", "not set"),
        "node_role_env": os.getenv("NODE_ROLE", "not set"),
    }


def print_runtime_config():
    """Print current runtime configuration to console."""
    info = get_runtime_info()
    print("\n" + "=" * 60)
    print("SINGULARIS RUNTIME CONFIGURATION")
    print("=" * 60)
    print(f"  LOCAL_ONLY_LLM:     {info['local_only_llm']}")
    print(f"  NODE_ROLE:          {info['node_role']}")
    print(f"  Environment:")
    print(f"    SINGULARIS_LOCAL_ONLY = {info['singularis_local_only_env']}")
    print(f"    NODE_ROLE             = {info['node_role_env']}")
    print("=" * 60 + "\n")
