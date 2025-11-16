"""
IWM (Image World Model) - Vision World Model Architecture

ViT-B/16 encoder + transformer predictor for world modeling.
Based on JEPA/IWM research - learns latent world models through prediction.

Phase 1: Single core IWM with augmentation-based actions
Phase 2: Dual-stream (invariant + equivariant)
Phase 3: Action-conditioned for planning

Hardware target: 2x AMD 7900 XT (20GB each)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import numpy as np
from loguru import logger


@dataclass
class IWMConfig:
    """Configuration for IWM model."""
    # Encoder (ViT-B/16)
    image_size: int = 224
    patch_size: int = 16
    encoder_dim: int = 768
    encoder_depth: int = 12
    encoder_heads: int = 12
    encoder_mlp_ratio: float = 4.0
    
    # Predictor (world model)
    predictor_depth: int = 8  # Phase 1: 8 layers (safe for 20GB)
    predictor_heads: int = 12
    predictor_mlp_ratio: float = 4.0
    predictor_dropout: float = 0.1
    
    # Augmentation/action conditioning
    aug_dim: int = 16  # Dimensionality of augmentation/action vector
    
    # Training
    use_ema: bool = True
    ema_momentum: float = 0.999
    
    def __post_init__(self):
        """Calculate derived values."""
        self.num_patches = (self.image_size // self.patch_size) ** 2
        self.total_params_m = self._estimate_params()
    
    def _estimate_params(self) -> float:
        """Estimate total parameters in millions."""
        # ViT-B/16 encoder: ~86M
        encoder = 86.0
        # Predictor: depth * (768^2 * 4 attention + 768^2 * mlp_ratio * 2 for MLP)
        predictor = self.predictor_depth * (
            (self.encoder_dim ** 2 * 4) +  # Attention
            (self.encoder_dim ** 2 * self.predictor_mlp_ratio * 2)  # MLP
        ) / 1e6
        return encoder + predictor


class PatchEmbedding(nn.Module):
    """Convert image to patch embeddings (ViT-style)."""
    
    def __init__(self, img_size: int = 224, patch_size: int = 16, in_chans: int = 3, embed_dim: int = 768):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [B, 3, H, W]
        Returns:
            [B, num_patches, embed_dim]
        """
        x = self.proj(x)  # [B, embed_dim, H/P, W/P]
        x = x.flatten(2).transpose(1, 2)  # [B, num_patches, embed_dim]
        return x


class TransformerBlock(nn.Module):
    """Standard transformer block with pre-norm."""
    
    def __init__(self, dim: int, num_heads: int, mlp_ratio: float = 4.0, dropout: float = 0.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, dim),
            nn.Dropout(dropout)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Self-attention with residual
        x = x + self.attn(self.norm1(x), self.norm1(x), self.norm1(x))[0]
        # MLP with residual
        x = x + self.mlp(self.norm2(x))
        return x


class IWMEncoder(nn.Module):
    """ViT-B/16 encoder for IWM."""
    
    def __init__(self, config: IWMConfig):
        super().__init__()
        self.config = config
        
        # Patch embedding
        self.patch_embed = PatchEmbedding(
            img_size=config.image_size,
            patch_size=config.patch_size,
            embed_dim=config.encoder_dim
        )
        
        # CLS token and positional embedding
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.encoder_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, config.num_patches + 1, config.encoder_dim))
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(
                dim=config.encoder_dim,
                num_heads=config.encoder_heads,
                mlp_ratio=config.encoder_mlp_ratio,
                dropout=0.0  # No dropout in encoder (like ViT-B)
            )
            for _ in range(config.encoder_depth)
        ])
        
        self.norm = nn.LayerNorm(config.encoder_dim)
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights (ViT-style)."""
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: [B, 3, H, W] images
        Returns:
            z_cls: [B, D] class token (global latent)
            z_patches: [B, N, D] patch tokens (local latents)
        """
        B = x.shape[0]
        
        # Patch embedding
        x = self.patch_embed(x)  # [B, N, D]
        
        # Add CLS token
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)  # [B, N+1, D]
        
        # Add positional embedding
        x = x + self.pos_embed
        
        # Transformer blocks
        for block in self.blocks:
            x = block(x)
        
        x = self.norm(x)
        
        # Split CLS and patches
        z_cls = x[:, 0]  # [B, D]
        z_patches = x[:, 1:]  # [B, N, D]
        
        return z_cls, z_patches


class IWMPredictor(nn.Module):
    """Transformer predictor for world model (predicts next latent given current + action)."""
    
    def __init__(self, config: IWMConfig):
        super().__init__()
        self.config = config
        
        # Action/augmentation embedding
        self.aug_embed = nn.Sequential(
            nn.Linear(config.aug_dim, config.encoder_dim),
            nn.GELU(),
            nn.Linear(config.encoder_dim, config.encoder_dim)
        )
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(
                dim=config.encoder_dim,
                num_heads=config.predictor_heads,
                mlp_ratio=config.predictor_mlp_ratio,
                dropout=config.predictor_dropout
            )
            for _ in range(config.predictor_depth)
        ])
        
        self.norm = nn.LayerNorm(config.encoder_dim)
    
    def forward(self, z: torch.Tensor, aug_params: torch.Tensor) -> torch.Tensor:
        """
        Args:
            z: [B, N+1, D] current latents (CLS + patches)
            aug_params: [B, aug_dim] augmentation/action parameters
        Returns:
            z_pred: [B, N+1, D] predicted next latents
        """
        # Embed augmentation/action
        aug_emb = self.aug_embed(aug_params)  # [B, D]
        aug_emb = aug_emb.unsqueeze(1)  # [B, 1, D]
        
        # Concatenate action embedding with latents
        x = torch.cat([aug_emb, z], dim=1)  # [B, N+2, D]
        
        # Transformer blocks
        for block in self.blocks:
            x = block(x)
        
        x = self.norm(x)
        
        # Remove action token, keep predicted latents
        z_pred = x[:, 1:]  # [B, N+1, D]
        
        return z_pred


class IWM(nn.Module):
    """Complete IWM model: encoder + predictor."""
    
    def __init__(self, config: IWMConfig):
        super().__init__()
        self.config = config
        
        self.encoder = IWMEncoder(config)
        self.predictor = IWMPredictor(config)
        
        # EMA teacher (optional, for training)
        if config.use_ema:
            self.encoder_ema = IWMEncoder(config)
            self.encoder_ema.load_state_dict(self.encoder.state_dict())
            for param in self.encoder_ema.parameters():
                param.requires_grad = False
        else:
            self.encoder_ema = None
        
        logger.info(f"[IWM] Model created: {config.total_params_m:.1f}M parameters")
    
    def encode(self, x: torch.Tensor, use_ema: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode image to latents."""
        encoder = self.encoder_ema if (use_ema and self.encoder_ema is not None) else self.encoder
        return encoder(x)
    
    def predict(self, z_cls: torch.Tensor, z_patches: torch.Tensor, aug_params: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Predict next latent given current + action."""
        # Combine CLS and patches
        z = torch.cat([z_cls.unsqueeze(1), z_patches], dim=1)  # [B, N+1, D]
        
        # Predict
        z_pred = self.predictor(z, aug_params)
        
        # Split back
        z_cls_pred = z_pred[:, 0]
        z_patches_pred = z_pred[:, 1:]
        
        return z_cls_pred, z_patches_pred
    
    def forward(
        self,
        x: torch.Tensor,
        x_aug: torch.Tensor,
        aug_params: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Full forward pass for training.
        
        Args:
            x: [B, 3, H, W] original image
            x_aug: [B, 3, H, W] augmented image
            aug_params: [B, aug_dim] augmentation parameters
        
        Returns:
            dict with z_target, z_pred, loss
        """
        # Encode target (with EMA if available)
        with torch.no_grad():
            z_cls_target, z_patches_target = self.encode(x_aug, use_ema=True)
        
        # Encode source
        z_cls, z_patches = self.encode(x, use_ema=False)
        
        # Predict
        z_cls_pred, z_patches_pred = self.predict(z_cls, z_patches, aug_params)
        
        # Loss: cosine similarity (like JEPA)
        loss_cls = 1 - F.cosine_similarity(z_cls_pred, z_cls_target, dim=-1).mean()
        loss_patches = 1 - F.cosine_similarity(
            z_patches_pred.flatten(1),
            z_patches_target.flatten(1),
            dim=-1
        ).mean()
        
        loss = 0.5 * loss_cls + 0.5 * loss_patches
        
        return {
            'z_cls_target': z_cls_target,
            'z_cls_pred': z_cls_pred,
            'z_patches_target': z_patches_target,
            'z_patches_pred': z_patches_pred,
            'loss': loss,
            'loss_cls': loss_cls,
            'loss_patches': loss_patches
        }
    
    @torch.no_grad()
    def update_ema(self, momentum: Optional[float] = None):
        """Update EMA teacher."""
        if self.encoder_ema is None:
            return
        
        m = momentum if momentum is not None else self.config.ema_momentum
        
        for param, param_ema in zip(self.encoder.parameters(), self.encoder_ema.parameters()):
            param_ema.data.mul_(m).add_(param.data, alpha=1 - m)


@dataclass
class IWMLatent:
    """Structured latent representation from IWM."""
    z_cls: np.ndarray  # [D] global latent
    z_patches: Optional[np.ndarray] = None  # [N, D] patch latents (optional)
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            'z_cls': self.z_cls.tolist(),
            'z_patches': self.z_patches.tolist() if self.z_patches is not None else None,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IWMLatent':
        """Deserialize from dict."""
        return cls(
            z_cls=np.array(data['z_cls']),
            z_patches=np.array(data['z_patches']) if data['z_patches'] is not None else None,
            timestamp=data.get('timestamp', 0.0)
        )


def create_iwm_model(variant: str = 'core', device: Any = 'cuda') -> IWM:
    """Factory function to create IWM models.

    Args:
        variant: 'core' (Phase 1), 'invariant' (Phase 2), 'equivariant' (Phase 2)
        device: torch device or device string ('cpu', 'cuda', 'dml')

    Returns:
        IWM model on the requested device.
    """
    if variant == 'core':
        config = IWMConfig(
            predictor_depth=8,  # Balanced
            predictor_dropout=0.1
        )
    elif variant == 'invariant':
        config = IWMConfig(
            predictor_depth=4,  # Smaller, more invariant
            predictor_dropout=0.15
        )
    elif variant == 'equivariant':
        config = IWMConfig(
            predictor_depth=16,  # Larger, more equivariant
            predictor_dropout=0.05
        )
    else:
        raise ValueError(f"Unknown variant: {variant}")

    # Resolve device
    if isinstance(device, str):
        dev = device.lower()

        if dev == 'dml':
            # DirectML backend (torch-directml)
            try:
                import torch_directml as td
            except ImportError:
                logger.warning("[IWM] 'dml' requested but torch-directml is not installed, falling back to CPU")
                device_obj = torch.device('cpu')
            else:
                device_obj = td.device()
                logger.info(f"[IWM] Using DirectML device: {device_obj}")
        else:
            try:
                device_obj = torch.device(device)
            except Exception:
                logger.warning(f"[IWM] Unknown device '{device}', falling back to CPU")
                device_obj = torch.device('cpu')
    else:
        # Assume already a torch/DirectML device object
        device_obj = device

    model = IWM(config).to(device_obj)
    return model
