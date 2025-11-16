"""
IWM Service - FastAPI microservice for world model inference

Provides endpoints:
- POST /encode: Image → latent
- POST /predict: Latent + action → predicted next latent
- POST /rollout: Latent + action sequence → predicted latent sequence

Follows Singularis service patterns (FastAPI, async, loguru).
"""

import asyncio
import time
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import io
import base64

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from loguru import logger

from .iwm_models import IWM, IWMConfig, IWMLatent, create_iwm_model


# ========================================
# Request/Response Models
# ========================================

class EncodeRequest(BaseModel):
    """Request to encode an image."""
    image_b64: Optional[str] = Field(None, description="Base64-encoded image (PNG/JPG)")
    image_path: Optional[str] = Field(None, description="Path to image file")
    return_patches: bool = Field(False, description="Return patch latents (else only CLS)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_b64": "iVBORw0KGgoAAAANSUhEUg...",
                "return_patches": False
            }
        }


class EncodeResponse(BaseModel):
    """Response from encode."""
    z_cls: List[float] = Field(..., description="Global latent vector (768-d)")
    z_patches: Optional[List[List[float]]] = Field(None, description="Patch latents [196, 768]")
    timestamp: float = Field(..., description="Server timestamp")
    latent_dim: int = Field(..., description="Latent dimensionality")
    model_variant: str = Field(..., description="Model variant (core/inv/equi)")


class PredictRequest(BaseModel):
    """Request to predict next latent."""
    z_cls: List[float] = Field(..., description="Current global latent")
    z_patches: Optional[List[List[float]]] = Field(None, description="Current patch latents")
    aug_params: List[float] = Field(..., description="Augmentation/action parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "z_cls": [0.1] * 768,
                "aug_params": [0.5, 0.3, 0.0, 0.0, 0.0]
            }
        }


class PredictResponse(BaseModel):
    """Response from predict."""
    z_cls_pred: List[float] = Field(..., description="Predicted global latent")
    z_patches_pred: Optional[List[List[float]]] = Field(None, description="Predicted patch latents")
    mrr: float = Field(..., description="Confidence (placeholder)")
    uncertainty: float = Field(..., description="Prediction uncertainty")
    timestamp: float


class RolloutRequest(BaseModel):
    """Request to rollout k steps."""
    z_cls: List[float] = Field(..., description="Starting global latent")
    z_patches: Optional[List[List[float]]] = Field(None, description="Starting patch latents")
    aug_seq: List[List[float]] = Field(..., description="Sequence of augmentation parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "z_cls": [0.1] * 768,
                "aug_seq": [[0.5, 0.3, 0.0], [0.4, 0.4, 0.1]]
            }
        }


class RolloutResponse(BaseModel):
    """Response from rollout."""
    z_cls_seq: List[List[float]] = Field(..., description="Sequence of predicted latents")
    z_patches_seq: Optional[List[List[List[float]]]] = Field(None, description="Sequence of patch latents")
    mrr_seq: List[float] = Field(..., description="Confidence per step")
    uncertainty_seq: List[float] = Field(..., description="Uncertainty per step")
    timestamp: float


class HealthResponse(BaseModel):
    """Service health status."""
    status: str
    model_loaded: bool
    model_variant: str
    device: str
    uptime_seconds: float
    total_encodes: int
    total_predicts: int
    total_rollouts: int


# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="IWM Vision World Model Service",
    description="Image World Model for Singularis/SkyrimAGI",
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

@dataclass
class ServiceState:
    """Service state."""
    model: Optional[IWM] = None
    model_variant: str = "core"
    # device: torch device object (cpu/cuda/privateuseone)
    device: Any = "cuda"
    # device_str: original device string ('cpu', 'cuda', 'dml', ...)
    device_str: str = "cuda"
    config: Optional[IWMConfig] = None
    start_time: float = field(default_factory=time.time)
    
    # Stats
    total_encodes: int = 0
    total_predicts: int = 0
    total_rollouts: int = 0


state = ServiceState()


# ========================================
# Startup/Shutdown
# ========================================

@app.on_event("startup")
async def startup():
    """Load IWM model on startup."""
    logger.info("[IWM-SERVICE] Starting IWM Vision World Model Service...")
    
    # Configuration from environment
    model_variant = os.getenv('IWM_MODEL_VARIANT', 'core')
    model_path = os.getenv('IWM_MODEL_PATH', None)
    device_str = os.getenv('IWM_DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')

    # Resolve device string to actual device (supports 'cpu', 'cuda', 'dml')
    dev_lower = device_str.lower()
    if dev_lower == 'dml':
        try:
            import torch_directml as td
        except ImportError:
            logger.warning("[IWM-SERVICE] 'dml' requested but torch-directml is not installed, falling back to CPU")
            device_obj = torch.device('cpu')
            device_str = 'cpu'
        else:
            device_obj = td.device()
            logger.info(f"[IWM-SERVICE] Using DirectML device: {device_obj}")
    else:
        try:
            device_obj = torch.device(device_str)
        except Exception:
            logger.warning(f"[IWM-SERVICE] Unknown device '{device_str}', falling back to CPU")
            device_obj = torch.device('cpu')
            device_str = 'cpu'

    state.model_variant = model_variant
    state.device = device_obj
    state.device_str = device_str

    logger.info(f"[IWM-SERVICE] Device: {device_str}")
    logger.info(f"[IWM-SERVICE] Model variant: {model_variant}")
    
    # Create model on resolved device
    state.model = create_iwm_model(variant=model_variant, device=device_obj)
    state.config = state.model.config
    
    # Load checkpoint if provided
    if model_path and os.path.exists(model_path):
        logger.info(f"[IWM-SERVICE] Loading checkpoint: {model_path}")
        checkpoint = torch.load(model_path, map_location=device_obj)
        state.model.load_state_dict(checkpoint['model'])
        logger.info(f"[IWM-SERVICE] Checkpoint loaded (epoch {checkpoint.get('epoch', '?')})")
    else:
        logger.warning("[IWM-SERVICE] No checkpoint provided, using random weights")
    
    state.model.eval()
    
    logger.info(f"[IWM-SERVICE] Model ready: {state.config.total_params_m:.1f}M params")
    logger.info("[IWM-SERVICE] Endpoints: /encode, /predict, /rollout, /health")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("[IWM-SERVICE] Shutting down IWM service")


# ========================================
# Helper Functions
# ========================================

def decode_image(req: EncodeRequest) -> Image.Image:
    """Decode image from request."""
    if req.image_b64:
        img_bytes = base64.b64decode(req.image_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    elif req.image_path:
        if not os.path.exists(req.image_path):
            raise HTTPException(status_code=400, detail=f"Image not found: {req.image_path}")
        img = Image.open(req.image_path).convert('RGB')
    else:
        raise HTTPException(status_code=400, detail="Must provide image_b64 or image_path")
    
    return img


def preprocess_image(img: Image.Image, size: int = 224) -> torch.Tensor:
    """Preprocess image to tensor."""
    from torchvision import transforms
    
    transform = transforms.Compose([
        transforms.Resize(size, interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return transform(img).unsqueeze(0)  # [1, 3, H, W]


def pad_aug_params(aug_params: List[float], target_dim: int) -> torch.Tensor:
    """Pad augmentation parameters to target dimension."""
    params = list(aug_params)
    if len(params) < target_dim:
        params.extend([0.0] * (target_dim - len(params)))
    elif len(params) > target_dim:
        params = params[:target_dim]
    
    return torch.tensor([params], dtype=torch.float32)


# ========================================
# Endpoints
# ========================================

@app.post("/encode", response_model=EncodeResponse)
async def encode(req: EncodeRequest):
    """Encode image to latent representation."""
    try:
        # Decode image
        img = decode_image(req)
        
        # Preprocess
        img_tensor = preprocess_image(img, state.config.image_size).to(state.device)
        
        # Encode
        with torch.no_grad():
            z_cls, z_patches = state.model.encode(img_tensor, use_ema=False)
        
        # Convert to numpy
        z_cls_np = z_cls.cpu().numpy()[0]
        z_patches_np = z_patches.cpu().numpy()[0] if req.return_patches else None
        
        state.total_encodes += 1
        
        return EncodeResponse(
            z_cls=z_cls_np.tolist(),
            z_patches=z_patches_np.tolist() if z_patches_np is not None else None,
            timestamp=time.time(),
            latent_dim=state.config.encoder_dim,
            model_variant=state.model_variant
        )
    
    except Exception as e:
        logger.error(f"[IWM-SERVICE] Encode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """Predict next latent given current + action."""
    try:
        # Convert inputs to tensors
        z_cls = torch.tensor([req.z_cls], dtype=torch.float32).to(state.device)
        
        if req.z_patches is not None:
            z_patches = torch.tensor([req.z_patches], dtype=torch.float32).to(state.device)
        else:
            # Use dummy patches if not provided
            z_patches = torch.zeros(
                1, state.config.num_patches, state.config.encoder_dim
            ).to(state.device)
        
        aug_params = pad_aug_params(req.aug_params, state.config.aug_dim).to(state.device)
        
        # Predict
        with torch.no_grad():
            z_cls_pred, z_patches_pred = state.model.predict(z_cls, z_patches, aug_params)
        
        # Compute confidence (placeholder: cosine sim with identity)
        mrr = F.cosine_similarity(z_cls, z_cls_pred, dim=-1).item()
        
        # Uncertainty (L2 distance)
        uncertainty = torch.norm(z_cls_pred - z_cls, dim=-1).item()
        
        # Convert to numpy
        z_cls_pred_np = z_cls_pred.cpu().numpy()[0]
        z_patches_pred_np = z_patches_pred.cpu().numpy()[0] if req.z_patches is not None else None
        
        state.total_predicts += 1
        
        return PredictResponse(
            z_cls_pred=z_cls_pred_np.tolist(),
            z_patches_pred=z_patches_pred_np.tolist() if z_patches_pred_np is not None else None,
            mrr=float(mrr),
            uncertainty=float(uncertainty),
            timestamp=time.time()
        )
    
    except Exception as e:
        logger.error(f"[IWM-SERVICE] Predict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rollout", response_model=RolloutResponse)
async def rollout(req: RolloutRequest):
    """Rollout k-step predictions."""
    try:
        # Initial state
        z_cls = torch.tensor([req.z_cls], dtype=torch.float32).to(state.device)
        
        if req.z_patches is not None:
            z_patches = torch.tensor([req.z_patches], dtype=torch.float32).to(state.device)
        else:
            z_patches = torch.zeros(
                1, state.config.num_patches, state.config.encoder_dim
            ).to(state.device)
        
        # Rollout
        z_cls_seq = []
        z_patches_seq = [] if req.z_patches is not None else None
        mrr_seq = []
        uncertainty_seq = []
        
        with torch.no_grad():
            for aug_params_raw in req.aug_seq:
                aug_params = pad_aug_params(aug_params_raw, state.config.aug_dim).to(state.device)
                
                # Predict next
                z_cls_pred, z_patches_pred = state.model.predict(z_cls, z_patches, aug_params)
                
                # Metrics
                mrr = F.cosine_similarity(z_cls, z_cls_pred, dim=-1).item()
                uncertainty = torch.norm(z_cls_pred - z_cls, dim=-1).item()
                
                # Store
                z_cls_seq.append(z_cls_pred.cpu().numpy()[0].tolist())
                if z_patches_seq is not None:
                    z_patches_seq.append(z_patches_pred.cpu().numpy()[0].tolist())
                mrr_seq.append(float(mrr))
                uncertainty_seq.append(float(uncertainty))
                
                # Update for next step
                z_cls = z_cls_pred
                z_patches = z_patches_pred
        
        state.total_rollouts += 1
        
        return RolloutResponse(
            z_cls_seq=z_cls_seq,
            z_patches_seq=z_patches_seq,
            mrr_seq=mrr_seq,
            uncertainty_seq=uncertainty_seq,
            timestamp=time.time()
        )
    
    except Exception as e:
        logger.error(f"[IWM-SERVICE] Rollout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check."""
    return HealthResponse(
        status="ok" if state.model is not None else "model_not_loaded",
        model_loaded=state.model is not None,
        model_variant=state.model_variant,
        device=state.device,
        uptime_seconds=time.time() - state.start_time,
        total_encodes=state.total_encodes,
        total_predicts=state.total_predicts,
        total_rollouts=state.total_rollouts
    )


# ========================================
# Main
# ========================================

def main():
    """Run service."""
    port = int(os.getenv('IWM_SERVICE_PORT', '8001'))
    host = os.getenv('IWM_SERVICE_HOST', '0.0.0.0')
    
    logger.info(f"[IWM-SERVICE] Starting on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
