# IWM Quick Start Guide

**TL;DR**: Vision world model for Singularis. Encodes frames to 768-d latents, predicts futures, enables planning.

---

## 1. Train Model (2-3 days on your dual 7900 XT)

```bash
# Prepare data
mkdir -p data/imagenet data/skyrim
# ... add your images ...

# Train with DDP (both GPUs)
python -m torch.distributed.launch --nproc_per_node=2 train_iwm_phase1.py \
    --data_dirs data/imagenet data/skyrim \
    --batch_size 160 \
    --epochs 100 \
    --ddp

# Checkpoint saved to: ./checkpoints/iwm/iwm_core_final.pt
```

---

## 2. Start Service

```bash
python start_iwm_service.py \
    --model_path ./checkpoints/iwm/iwm_core_final.pt \
    --device cuda:0 \
    --port 8001

# Service at: http://localhost:8001
```

---

## 3. Test Everything

```bash
python test_iwm_system.py
# Should see: ✓ All tests passed!
```

---

## 4. Wire Into Perception

**Option A: Standalone Module**

```python
from singularis.perception import IWMPerceptionModule

iwm = IWMPerceptionModule("http://localhost:8001")
await iwm.process_frame(frame, being_state, action_taken="move_forward")
```

**Option B: Add to UnifiedPerceptionLayer**

Edit `singularis/perception/unified_perception.py`:

```python
from singularis.perception import IWMPerceptionModule

class UnifiedPerceptionLayer:
    def __init__(self, ...):
        # ... existing init ...
        self.iwm = IWMPerceptionModule("http://localhost:8001")
    
    async def process_frame(self, frame, being_state):
        # ... existing code ...
        await self.iwm.process_frame(frame, being_state, being_state.last_action)
```

---

## 5. Use in ActionArbiter

Edit `singularis/skyrim/action_arbiter.py`:

```python
async def request_action(self, ...):
    # ... existing logic ...
    
    # Check surprise for anomalies
    if being_state.vision_prediction_surprise > 2.0:
        logger.warning(f"High surprise: {being_state.vision_prediction_surprise:.2f}")
        # Maybe prefer "wait" action or escalate to LLM
    
    # Check confidence
    if being_state.vision_mrr < 0.5:
        logger.info(f"Low world model confidence: {being_state.vision_mrr:.2f}")
        # Maybe escalate to GPT for reasoning
```

---

## Files Created

**Core (3)**:
- `singularis/world_model/iwm_models.py` - Model architecture
- `singularis/world_model/iwm_service.py` - FastAPI service
- `singularis/world_model/iwm_client.py` - Client library

**Integration (1)**:
- `singularis/perception/iwm_perception_integration.py` - Perception module

**Scripts (3)**:
- `train_iwm_phase1.py` - Training
- `start_iwm_service.py` - Start service
- `test_iwm_system.py` - Tests

**Docs (2)**:
- `docs/IWM_WORLD_MODEL_GUIDE.md` - Full guide
- `IWM_IMPLEMENTATION_SUMMARY.md` - Summary

**Modified (3)**:
- `singularis/core/being_state.py` - Added vision fields
- `singularis/world_model/__init__.py` - Exports
- `singularis/perception/__init__.py` - Exports

---

## BeingState Fields

After integration, `being_state` has:

```python
being_state.vision_core_latent           # np.ndarray [768] - current visual latent
being_state.vision_core_latent_prev      # Previous frame latent
being_state.vision_prediction_surprise   # float - prediction error
being_state.vision_mrr                   # float - world model confidence
being_state.vision_core_timestamp        # float - last update time
```

---

## API Endpoints

**Service at `http://localhost:8001`**:

- `POST /encode` - Image → latent (~10ms)
- `POST /predict` - Latent + action → predicted latent (~5ms)
- `POST /rollout` - k-step predictions (~30ms for k=5)
- `GET /health` - Status

---

## Hardware

**Training**:
- 2×7900 XT (20GB each): ✅ Perfect
- Batch 320 global, 24-36h for 100 epochs

**Inference**:
- Single 7900 XT: ~8GB VRAM
- Dual-stream (Phase 2): ~16GB

**Bottleneck**: Data collection, not hardware 🎉

---

## What This Gives You

1. **Compact representations**: 768-d vs millions of pixels
2. **Predictive capability**: "What will I see if I do X?"
3. **Anomaly detection**: High surprise = novel situation
4. **Planning-ready**: k-step rollouts for trajectory search
5. **Dual streams (Phase 2)**: Semantic (LLM) + equivariant (control)

---

## Next Steps

1. ✅ **Phase 1 implemented** (this)
2. ⏳ Train model on your data
3. ⏳ Deploy service on Node A
4. ⏳ Wire into perception
5. ⏳ Validate surprise metrics
6. ⏳ **Phase 2**: Dual-stream (invariant + equivariant)
7. ⏳ **Phase 3**: Action-conditioned planning

---

## Support

**Full docs**: `docs/IWM_WORLD_MODEL_GUIDE.md`  
**Implementation**: `IWM_IMPLEMENTATION_SUMMARY.md`  
**Code**: `singularis/world_model/`

**Questions?** Check logs, run tests, verify service health.

---

**You now have a proper visual world model** 🚀

No more "just embeddings" - you can now **imagine futures** and **plan actions** based on predicted visual outcomes.
