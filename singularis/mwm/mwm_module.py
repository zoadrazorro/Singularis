"""
MWM PyTorch Module - Core neural architecture

Maintains latent mental state and provides:
- encode: Update z_t from observations (GWM, IWM, self)
- predict: Simulate next state given action
- decode: Map latent to interpretable features
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Tuple, Optional
from loguru import logger


class MentalWorldModelModule(nn.Module):
    """
    Core latent MWM module.
    
    Architecture:
    - Encoders: Map GWM, IWM, self-state to latent space
    - Latent update: GRU-based recurrent update
    - Dynamics: Predict next latent given action
    - Decoders: Map latent to interpretable features
    
    Dimensions:
    - GWM: 16 features (threat, enemies, cover, etc.)
    - IWM: 768 features (visual latent from ViT-B/16)
    - Self: 8 features (health, stamina, mode, confidence)
    - Action: 16 features (type, magnitude, direction)
    - Latent: 256 (configurable)
    """
    
    def __init__(
        self,
        latent_dim: int = 256,
        gwm_dim: int = 16,
        iwm_dim: int = 768,
        self_dim: int = 8,
        action_dim: int = 16,
        world_output_dim: int = 16,
        self_output_dim: int = 8,
        affect_output_dim: int = 4
    ):
        """
        Initialize MWM module.
        
        Args:
            latent_dim: Dimension of mental latent vector
            gwm_dim: GWM feature dimension
            iwm_dim: IWM latent dimension
            self_dim: Self-state feature dimension
            action_dim: Action encoding dimension
            world_output_dim: World decoder output dimension
            self_output_dim: Self decoder output dimension
            affect_output_dim: Affect decoder output dimension
        """
        super().__init__()
        
        self.latent_dim = latent_dim
        self.gwm_dim = gwm_dim
        self.iwm_dim = iwm_dim
        self.self_dim = self_dim
        self.action_dim = action_dim
        
        # ========================================
        # Encoders: Map inputs to latent space
        # ========================================
        
        # GWM encoder: 16 → 128 → 256
        self.gwm_encoder = nn.Sequential(
            nn.Linear(gwm_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, latent_dim),
        )
        
        # IWM encoder: 768 → 512 → 256
        self.iwm_encoder = nn.Sequential(
            nn.Linear(iwm_dim, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, latent_dim),
        )
        
        # Self encoder: 8 → 64 → 256
        self.self_encoder = nn.Sequential(
            nn.Linear(self_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, latent_dim),
        )
        
        # ========================================
        # Latent Update: Recurrent fusion
        # ========================================
        
        # Combine all encoded inputs
        self.latent_update = nn.GRUCell(
            input_size=latent_dim * 3,  # gwm + iwm + self
            hidden_size=latent_dim,
        )
        
        # ========================================
        # Dynamics: Action-conditioned prediction
        # ========================================
        
        # Action encoder: 16 → 64 → 256
        self.action_encoder = nn.Sequential(
            nn.Linear(action_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, latent_dim),
        )
        
        # Dynamics model: predict z_{t+1} from z_t + action
        self.dynamics = nn.GRUCell(
            input_size=latent_dim,  # action embedding
            hidden_size=latent_dim,
        )
        
        # ========================================
        # Decoders: Map latent to interpretable features
        # ========================================
        
        # World decoder: 256 → 128 → 16
        self.world_decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, world_output_dim),
        )
        
        # Self decoder: 256 → 64 → 8
        self.self_decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, self_output_dim),
        )
        
        # Affect decoder: 256 → 64 → 4
        self.affect_decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, affect_output_dim),
        )
        
        logger.info(f"[MWM] Initialized with latent_dim={latent_dim}")
        logger.info(f"[MWM] Input dims: GWM={gwm_dim}, IWM={iwm_dim}, Self={self_dim}, Action={action_dim}")
    
    def encode(
        self,
        z_prev: torch.Tensor,
        gwm_feats: torch.Tensor,
        iwm_latent: torch.Tensor,
        self_feats: torch.Tensor,
    ) -> torch.Tensor:
        """
        Update latent z_t from previous z_{t-1} and current inputs.
        
        Args:
            z_prev: [B, D] - Previous latent state
            gwm_feats: [B, G] - GWM features (flattened)
            iwm_latent: [B, V] - IWM visual latent
            self_feats: [B, S] - Self-state features
        
        Returns:
            z_t: [B, D] - Updated latent state
        """
        # Encode each modality
        gwm_emb = self.gwm_encoder(gwm_feats)      # [B, D]
        iwm_emb = self.iwm_encoder(iwm_latent)     # [B, D]
        self_emb = self.self_encoder(self_feats)   # [B, D]
        
        # Concatenate all embeddings
        combined = torch.cat([gwm_emb, iwm_emb, self_emb], dim=-1)  # [B, 3D]
        
        # Recurrent update
        z_t = self.latent_update(combined, z_prev)  # [B, D]
        
        return z_t
    
    def predict(
        self,
        z_t: torch.Tensor,
        action_feats: torch.Tensor,
    ) -> torch.Tensor:
        """
        Predict next latent z_hat_{t+1} given current z_t and action.
        
        This is the "mental simulation" function - agent imagines
        what its mental state will be after taking an action.
        
        Args:
            z_t: [B, D] - Current latent state
            action_feats: [B, A] - Encoded action features
        
        Returns:
            z_hat_t1: [B, D] - Predicted next latent state
        """
        # Encode action
        a_emb = self.action_encoder(action_feats)  # [B, D]
        
        # Use dynamics model to predict next state
        # GRU takes (input, hidden) and returns new hidden
        z_hat_t1 = self.dynamics(a_emb, z_t)  # [B, D]
        
        return z_hat_t1
    
    def decode(
        self,
        z_t: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """
        Decode latent into interpretable features.
        
        Args:
            z_t: [B, D] - Latent state
        
        Returns:
            Dictionary with decoded features:
            - "world": [B, W] - World features (threat, enemies, etc.)
            - "self": [B, S] - Self-state (health, stamina, etc.)
            - "affect": [B, A] - Affect (threat, curiosity, value, surprise)
        """
        world_vec = self.world_decoder(z_t)    # [B, W]
        self_vec = self.self_decoder(z_t)      # [B, S]
        affect_vec = self.affect_decoder(z_t)  # [B, A]
        
        return {
            "world": world_vec,
            "self": self_vec,
            "affect": affect_vec,
        }
    
    def forward(
        self,
        z_prev: torch.Tensor,
        gwm_feats: torch.Tensor,
        iwm_latent: torch.Tensor,
        self_feats: torch.Tensor,
        action_feats: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor], Optional[torch.Tensor]]:
        """
        Full forward pass: encode → decode [→ predict].
        
        Args:
            z_prev: [B, D] - Previous latent
            gwm_feats: [B, G] - GWM features
            iwm_latent: [B, V] - IWM latent
            self_feats: [B, S] - Self features
            action_feats: [B, A] - Optional action for prediction
        
        Returns:
            z_t: [B, D] - Current latent
            decoded: Dict of decoded features
            z_hat_t1: [B, D] - Optional predicted next latent
        """
        # Encode
        z_t = self.encode(z_prev, gwm_feats, iwm_latent, self_feats)
        
        # Decode
        decoded = self.decode(z_t)
        
        # Predict (if action provided)
        z_hat_t1 = None
        if action_feats is not None:
            z_hat_t1 = self.predict(z_t, action_feats)
        
        return z_t, decoded, z_hat_t1
    
    def init_latent(self, batch_size: int = 1, device: Optional[torch.device] = None) -> torch.Tensor:
        """
        Initialize latent state (zeros).
        
        Args:
            batch_size: Batch size
            device: Device to create tensor on
        
        Returns:
            z_0: [B, D] - Initial latent state
        """
        if device is None:
            device = next(self.parameters()).device
        return torch.zeros(batch_size, self.latent_dim, device=device)
    
    def get_parameter_count(self) -> Dict[str, int]:
        """Get parameter counts for each component."""
        counts = {}
        
        for name, module in self.named_children():
            counts[name] = sum(p.numel() for p in module.parameters())
        
        counts['total'] = sum(p.numel() for p in self.parameters())
        
        return counts


# ========================================
# Training Utilities (for future use)
# ========================================

class MWMLoss(nn.Module):
    """
    Combined loss for MWM training.
    
    Losses:
    1. Reconstruction: Decode(Encode(x)) ≈ x
    2. Prediction: Predict(z_t, a_t) ≈ z_{t+1}
    3. Affect prediction: Decode_affect(z_t) ≈ reward/value
    """
    
    def __init__(
        self,
        recon_weight: float = 1.0,
        pred_weight: float = 1.0,
        affect_weight: float = 1.0
    ):
        super().__init__()
        self.recon_weight = recon_weight
        self.pred_weight = pred_weight
        self.affect_weight = affect_weight
        
        self.mse = nn.MSELoss()
        self.bce = nn.BCEWithLogitsLoss()
    
    def forward(
        self,
        decoded: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor],
        z_pred: Optional[torch.Tensor] = None,
        z_target: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Compute combined loss.
        
        Args:
            decoded: Decoded features from model
            targets: Target features
            z_pred: Predicted next latent (optional)
            z_target: Target next latent (optional)
        
        Returns:
            loss: Combined loss
            loss_dict: Individual loss components
        """
        losses = {}
        total_loss = 0.0
        
        # Reconstruction loss
        if "world" in decoded and "world" in targets:
            losses["recon_world"] = self.mse(decoded["world"], targets["world"])
            total_loss += self.recon_weight * losses["recon_world"]
        
        if "self" in decoded and "self" in targets:
            losses["recon_self"] = self.mse(decoded["self"], targets["self"])
            total_loss += self.recon_weight * losses["recon_self"]
        
        # Prediction loss
        if z_pred is not None and z_target is not None:
            losses["pred_latent"] = self.mse(z_pred, z_target)
            total_loss += self.pred_weight * losses["pred_latent"]
        
        # Affect loss (value prediction)
        if "affect" in decoded and "affect" in targets:
            losses["affect"] = self.mse(decoded["affect"], targets["affect"])
            total_loss += self.affect_weight * losses["affect"]
        
        # Convert to floats for logging
        loss_dict = {k: v.item() for k, v in losses.items()}
        loss_dict["total"] = total_loss.item() if isinstance(total_loss, torch.Tensor) else total_loss
        
        return total_loss, loss_dict
