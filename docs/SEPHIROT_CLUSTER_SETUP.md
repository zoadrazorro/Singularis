# Sephirot Cluster Setup Guide

**Local-Only LLM Architecture for Singularis LifeOps**

This guide describes how to distribute Singularis across the Sephirot cluster with all LLM traffic routed to local endpoints (no cloud API calls).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       SEPHIROT CLUSTER                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│   MacBook Pro        │      │   AMD Desktop        │      │   NVIDIA Laptop      │
│   (Inference Node)   │◄────►│   (LifeOps Core)     │◄────►│   (Optional)         │
├──────────────────────┤      ├──────────────────────┤      ├──────────────────────┤
│ • LM Studio          │      │ • Singularis AGI     │      │ • LM Studio/vLLM     │
│ • Port: 1234         │      │ • LifeOps            │      │ • Port: 1235         │
│ • Models:            │      │ • UnifiedConsciousness│      │ • Larger models      │
│   - phi-4-mini       │      │ • Pattern Arbiter    │      │   (optional)         │
│   - reasoning models │      │ • Query Handler      │      │                      │
│                      │      │ • Intervention       │      │                      │
└──────────────────────┘      └──────────────────────┘      └──────────────────────┘
   192.168.1.100:1234           192.168.1.50                  192.168.1.101:1235
```

### Node Roles

| Node | Role | Purpose | Required |
|------|------|---------|----------|
| **MacBook Pro** | `inference_primary` | Primary LM Studio inference server | ✅ Yes |
| **AMD Desktop** | `lifeops_core` | Runs LifeOps orchestration + Singularis AGI | ✅ Yes |
| **NVIDIA Laptop** | `inference_secondary` | Optional secondary inference node | ❌ No |

---

## Configuration

### Global Environment Variables

Set these on **all nodes**:

```bash
# Cluster node role
export NODE_ROLE=<role>  # inference_primary, lifeops_core, or inference_secondary

# Enable local-only mode (no cloud API calls)
export SINGULARIS_LOCAL_ONLY=1
```

---

## Node 1: MacBook Pro (Inference Primary)

**Role:** Primary inference server  
**IP:** `192.168.1.100` (example - use your actual LAN IP)

### Setup

1. **Install LM Studio**
   ```bash
   # Download from https://lmstudio.ai/
   # Or use vLLM/llama.cpp if preferred
   ```

2. **Load Models**
   - Primary reasoning: `microsoft/phi-4-mini-reasoning` (or equivalent)
   - Alternative: `huihui-moe-60b-a38` or other small reasoning models
   - Ensure model is loaded and ready to serve

3. **Configure LM Studio**
   - Enable OpenAI-compatible API
   - Bind to: `0.0.0.0:1234` (listen on all interfaces)
   - Set CORS to allow your LAN

4. **Start LM Studio Server**
   ```bash
   # In LM Studio UI:
   # 1. Go to "Local Server" tab
   # 2. Select loaded model
   # 3. Click "Start Server"
   # 4. Verify: http://localhost:1234/v1/models
   ```

5. **Set Environment Variables**
   ```bash
   export NODE_ROLE=inference_primary
   # No need for SINGULARIS_LOCAL_ONLY on inference nodes
   ```

### Verification

Test the endpoint:
```bash
curl http://192.168.1.100:1234/v1/models

# Expected response:
# {
#   "data": [
#     {
#       "id": "microsoft/phi-4-mini-reasoning",
#       ...
#     }
#   ]
# }
```

---

## Node 2: AMD Desktop (LifeOps Core)

**Role:** AGI orchestration + LifeOps  
**IP:** `192.168.1.50` (example)

### Setup

1. **Clone Singularis Repository**
   ```bash
   git clone <singularis-repo>
   cd singularis
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**
   ```bash
   # Node role
   export NODE_ROLE=lifeops_core

   # Enable local-only mode
   export SINGULARIS_LOCAL_ONLY=1

   # Point to MacBook Pro inference server
   export OPENAI_BASE_URL="http://192.168.1.100:1234/v1"

   # Optional: API key (not required for local endpoints, but can set to "local-only")
   export OPENAI_API_KEY="local-only"
   ```

4. **Configure AGI System**
   ```python
   from singularis.agi_orchestrator import AGIOrchestrator, AGIConfig

   config = AGIConfig(
       # Point to MacBook Pro LM Studio
       lm_studio_url="http://192.168.1.100:1234/v1",
       lm_studio_model="microsoft/phi-4-mini-reasoning",
       
       # GPT-5 models (labels for local models)
       gpt5_model="microsoft/phi-4-mini-reasoning",
       gpt5_nano_model="microsoft/phi-4-mini-reasoning",
       
       # Enable unified consciousness (will use local endpoint)
       use_unified_consciousness=True,
   )

   orchestrator = AGIOrchestrator(config)
   ```

5. **Start AGI System**
   ```bash
   python -m singularis.agi_orchestrator
   # Or your specific LifeOps entry point
   ```

### Expected Output

```
================================================================
SINGULARIS RUNTIME CONFIGURATION
================================================================
  LOCAL_ONLY_LLM:     True
  NODE_ROLE:          lifeops_core
  Environment:
    SINGULARIS_LOCAL_ONLY = 1
    NODE_ROLE             = lifeops_core
================================================================

Initializing AGI components...
  [1/7] World model...
  ...
  [8/9] Unified consciousness layer (GPT-5)...
    GPT-5 unified consciousness enabled
[OK] Unified consciousness layer ready (GPT-5 + 5 GPT-5-nano experts)
     Mode: LOCAL-ONLY | Endpoint: http://192.168.1.100:1234/v1
```

---

## Node 3: NVIDIA Laptop (Inference Secondary - Optional)

**Role:** Optional secondary inference node  
**IP:** `192.168.1.101:1235` (example)

This node is **optional**. You can add it later for load balancing or larger models.

### Setup

1. **Install LM Studio or vLLM**
   ```bash
   # vLLM example:
   pip install vllm
   
   python -m vllm.entrypoints.openai.api_server \
       --model <larger-model> \
       --host 0.0.0.0 \
       --port 1235
   ```

2. **Set Environment Variables**
   ```bash
   export NODE_ROLE=inference_secondary
   ```

3. **Future Enhancement**
   To use this node, implement a simple load balancer or health-check router on the main AGI node:
   ```python
   # TODO: Round-robin between primary and secondary
   inference_urls = [
       "http://192.168.1.100:1234/v1",  # MacBook
       "http://192.168.1.101:1235/v1",  # NVIDIA laptop
   ]
   ```

---

## Architecture Details

### Local-Only Enforcement

All LLM traffic is enforced to be local-only through multiple layers:

1. **Runtime Flag**: `SINGULARIS_LOCAL_ONLY=1` sets global flag
2. **OpenAIClient**: Validates URLs in `is_available()`, rejects cloud URLs
3. **UnifiedConsciousnessLayer**: Checks `local_only` flag and raises error if misconfigured
4. **AGIOrchestrator**: Explicitly passes `local_only=True` when constructing UnifiedConsciousnessLayer

### Network Flow

```
LifeOps Query
    ↓
UnifiedConsciousnessLayer.process()
    ↓
OpenAIClient.generate() [base_url=http://192.168.1.100:1234/v1]
    ↓
HTTP POST → MacBook Pro LM Studio
    ↓
Local Model Inference (phi-4-mini-reasoning)
    ↓
Response → UnifiedConsciousnessLayer
    ↓
Synthesized Response → LifeOps
```

**No cloud API calls are made.**

### Code Changes Summary

| File | Change |
|------|--------|
| `singularis/core/runtime_flags.py` | **Created** - Global `LOCAL_ONLY_LLM` flag |
| `singularis/llm/openai_client.py` | **Modified** - Accept `OPENAI_BASE_URL`, validate local URLs |
| `singularis/unified_consciousness_layer.py` | **Modified** - Accept `openai_base_url` and `local_only` params |
| `singularis/agi_orchestrator.py` | **Modified** - Pass `lm_studio_url` with `local_only=True` |

---

## Testing

### Test 1: Runtime Flags

```bash
python -c "from singularis.core.runtime_flags import print_runtime_config; print_runtime_config()"
```

**Expected:**
```
================================================================
SINGULARIS RUNTIME CONFIGURATION
================================================================
  LOCAL_ONLY_LLM:     True
  NODE_ROLE:          lifeops_core
  Environment:
    SINGULARIS_LOCAL_ONLY = 1
    NODE_ROLE             = lifeops_core
================================================================
```

### Test 2: OpenAIClient Local Endpoint

```python
import asyncio
from singularis.llm.openai_client import OpenAIClient

async def test():
    # Point to MacBook Pro
    client = OpenAIClient(
        model="microsoft/phi-4-mini-reasoning",
        base_url="http://192.168.1.100:1234/v1"
    )
    
    print(f"Client available: {client.is_available()}")
    print(f"Base URL: {client.base_url}")
    
    # Test generation
    result = await client.generate_text("Test query")
    print(f"Response: {result[:100]}...")
    
asyncio.run(test())
```

**Expected:**
```
Client available: True
Base URL: http://192.168.1.100:1234/v1
Response: [text from local model]...
```

### Test 3: UnifiedConsciousnessLayer

```python
import asyncio
from singularis.unified_consciousness_layer import UnifiedConsciousnessLayer

async def test():
    layer = UnifiedConsciousnessLayer(
        gpt5_model="microsoft/phi-4-mini-reasoning",
        gpt5_nano_model="microsoft/phi-4-mini-reasoning",
        openai_base_url="http://192.168.1.100:1234/v1",
        local_only=True
    )
    
    result = await layer.process(
        query="How should I approach a new habit?",
        subsystem_inputs={
            'llm': "Start small and be consistent",
            'action': "Current motivation: Competence=0.7"
        }
    )
    
    print(f"Response: {result.response[:200]}...")
    print(f"Coherence: {result.coherence_score:.2f}")
    
asyncio.run(test())
```

**Expected:**
```
[GPT-5 Consciousness] Processing query: How should I approach a new habit?...
[OK] Response generated (all traffic routed to http://192.168.1.100:1234/v1)
Coherence: 0.78
```

### Test 4: LifeOps Integration

```python
import asyncio
from singularis.agi_orchestrator import AGIOrchestrator, AGIConfig

async def test():
    config = AGIConfig(
        lm_studio_url="http://192.168.1.100:1234/v1",
        use_unified_consciousness=True
    )
    
    agi = AGIOrchestrator(config)
    await agi.initialize_llm()
    
    # Test LifeOps query
    from singularis.life_ops.life_query_handler import LifeQueryHandler
    from integrations.life_timeline import LifeTimeline
    
    timeline = LifeTimeline("test_user")
    handler = LifeQueryHandler(timeline, agi.unified_consciousness)
    
    result = await handler.handle_query("How did I sleep last night?")
    print(f"Query result: {result.response[:200]}...")
    
asyncio.run(test())
```

**Expected:**
```
[OK] Unified consciousness layer ready (GPT-5 + 5 GPT-5-nano experts)
     Mode: LOCAL-ONLY | Endpoint: http://192.168.1.100:1234/v1
[LifeOps] Processing query...
[GPT-5 Consciousness] All traffic routed to local endpoint
Query result: Based on your sleep data from last night...
```

---

## Troubleshooting

### Error: "UnifiedConsciousnessLayer in LOCAL_ONLY mode but no local LLM endpoint configured"

**Cause:** `SINGULARIS_LOCAL_ONLY=1` is set but `OPENAI_BASE_URL` is not configured.

**Fix:**
```bash
export OPENAI_BASE_URL="http://192.168.1.100:1234/v1"
```

### Error: Connection refused to 192.168.1.100:1234

**Cause:** LM Studio is not running or not accessible on LAN.

**Fix:**
1. Verify LM Studio is running: `curl http://192.168.1.100:1234/v1/models`
2. Check firewall rules on MacBook Pro
3. Ensure LM Studio is bound to `0.0.0.0`, not `127.0.0.1`

### Error: "OpenAI API key not configured"

**Cause:** Cloud fallback attempted but API key missing.

**Fix:**
```bash
# For local endpoints, set dummy key
export OPENAI_API_KEY="local-only"
```

### Performance: Slow responses from local models

**Solutions:**
1. Use smaller, faster models (phi-4-mini-reasoning)
2. Enable GPU acceleration in LM Studio
3. Add NVIDIA laptop as secondary inference node for load balancing

---

## Network Security

### Firewall Rules

On MacBook Pro (inference node):
```bash
# Allow LM Studio port from LAN only
ufw allow from 192.168.1.0/24 to any port 1234
```

On AMD Desktop (core node):
```bash
# No inbound ports needed (outbound only)
```

### API Key Management

Local endpoints do not require API keys. If you set `OPENAI_API_KEY`, use a placeholder:
```bash
export OPENAI_API_KEY="local-only"
```

Do **not** set real cloud API keys on the core node.

---

## Future Enhancements

### Load Balancing

Implement a simple round-robin load balancer:

```python
# singularis/llm/inference_router.py (future)
class InferenceRouter:
    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.current = 0
    
    def get_next_endpoint(self) -> str:
        endpoint = self.endpoints[self.current]
        self.current = (self.current + 1) % len(self.endpoints)
        return endpoint
```

### Health Checks

Add periodic health checks to inference nodes:

```python
async def check_inference_health(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/models", timeout=5) as resp:
                return resp.status == 200
    except:
        return False
```

### Monitoring

Add Prometheus metrics:
- Request latency per inference node
- Model load on each node
- Failure rates

---

## Summary

**Cluster Configuration:**
- MacBook Pro: LM Studio inference on `192.168.1.100:1234`
- AMD Desktop: LifeOps core, routes to MacBook
- NVIDIA Laptop: Optional secondary inference

**Environment Variables:**
- `NODE_ROLE=lifeops_core` (on AMD)
- `SINGULARIS_LOCAL_ONLY=1` (on AMD)
- `OPENAI_BASE_URL=http://192.168.1.100:1234/v1` (on AMD)

**Result:**
- All LLM traffic stays on local network
- No cloud API calls
- Zero cloud costs
- Full data privacy

**Status:** ✅ Production Ready
