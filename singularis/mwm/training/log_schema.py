"""
Training Log Schema - Data format for offline MWM training

Logs (GWM, IWM, self, action, reward) tuples for training.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class TrainingLogEntry(BaseModel):
    """
    Single training data point.
    
    Captures one tick of experience:
    - Observations (GWM, IWM, self-state)
    - Action taken
    - Reward/outcome
    """
    # Meta
    timestamp: float = Field(..., description="Game time")
    cycle_number: int = Field(0, description="AGI cycle number")
    
    # Observations
    gwm_features: Optional[Dict[str, Any]] = Field(None, description="GWM features dict")
    iwm_latent: Optional[List[float]] = Field(None, description="IWM visual latent [768]")
    self_state: Dict[str, Any] = Field(default_factory=dict, description="Self-state features")
    
    # Action
    action_type: str = Field("unknown", description="Action type taken")
    action_params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    
    # Outcome
    reward_proxy: float = Field(0.0, description="Reward signal")
    next_gwm_features: Optional[Dict[str, Any]] = Field(None, description="Next GWM features")
    next_iwm_latent: Optional[List[float]] = Field(None, description="Next IWM latent")
    next_self_state: Dict[str, Any] = Field(default_factory=dict, description="Next self-state")
    
    # Additional context
    was_successful: bool = Field(True, description="Was action successful")
    surprise: float = Field(0.0, description="IWM prediction surprise")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 12345.67,
                "cycle_number": 42,
                "gwm_features": {"threat_level": 0.7, "num_enemies": 2},
                "iwm_latent": [0.1, 0.2],  # ... 768-d
                "self_state": {"health": 0.65, "stamina": 0.4},
                "action_type": "move_forward",
                "action_params": {"duration": 1.0},
                "reward_proxy": 0.12,
                "was_successful": True
            }
        }


class TrainingDataset:
    """
    Collection of training log entries.
    
    Manages loading/saving training data.
    """
    
    def __init__(self, entries: Optional[List[TrainingLogEntry]] = None):
        """Initialize dataset."""
        self.entries = entries or []
    
    def add_entry(self, entry: TrainingLogEntry):
        """Add a log entry."""
        self.entries.append(entry)
    
    def save_jsonl(self, path: Path):
        """
        Save dataset as JSONL.
        
        Args:
            path: Output file path
        """
        with open(path, 'w') as f:
            for entry in self.entries:
                f.write(entry.model_dump_json() + '\n')
    
    @classmethod
    def load_jsonl(cls, path: Path) -> 'TrainingDataset':
        """
        Load dataset from JSONL.
        
        Args:
            path: Input file path
        
        Returns:
            TrainingDataset
        """
        entries = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = TrainingLogEntry.model_validate_json(line)
                    entries.append(entry)
        
        return cls(entries)
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __getitem__(self, idx: int) -> TrainingLogEntry:
        return self.entries[idx]


# ========================================
# Logging Helpers
# ========================================

def log_training_entry(
    gwm_features: Optional[Dict[str, Any]],
    iwm_latent: Optional[List[float]],
    self_state: Dict[str, Any],
    action_type: str,
    action_params: Dict[str, Any],
    reward_proxy: float,
    log_file: Path,
    **kwargs
):
    """
    Append a training entry to log file.
    
    Args:
        gwm_features: GWM features
        iwm_latent: IWM latent
        self_state: Self-state dict
        action_type: Action type
        action_params: Action parameters
        reward_proxy: Reward signal
        log_file: Path to log file
        **kwargs: Additional fields
    """
    import time
    
    entry = TrainingLogEntry(
        timestamp=time.time(),
        gwm_features=gwm_features,
        iwm_latent=iwm_latent,
        self_state=self_state,
        action_type=action_type,
        action_params=action_params,
        reward_proxy=reward_proxy,
        **kwargs
    )
    
    with open(log_file, 'a') as f:
        f.write(entry.model_dump_json() + '\n')
