"""
Person Model Utilities - Helper functions for PersonModel lifecycle

Handles MWM updates, persistence, etc.
"""

import json
from pathlib import Path
from typing import Optional
import torch
from loguru import logger

from .types import PersonModel
from ..mwm import update_mwm_from_inputs, MentalWorldModelState


def update_person_mwm(
    person: PersonModel,
    gwm_features: Optional[dict],
    iwm_latent,
    being_state: any,
    mwm_module: any,
    device: torch.device
) -> PersonModel:
    """
    Update PersonModel's MWM from current observations.
    
    This is the main integration point with MWM.
    
    Args:
        person: PersonModel to update
        gwm_features: GWM features dict
        iwm_latent: IWM visual latent
        being_state: BeingState (for self-state)
        mwm_module: MentalWorldModelModule
        device: Torch device
    
    Returns:
        Updated PersonModel
    """
    try:
        # Update MWM
        new_mwm = update_mwm_from_inputs(
            mwm_state=person.mwm,
            gwm_features=gwm_features,
            iwm_latent=iwm_latent,
            being_state=being_state,
            mwm_module=mwm_module,
            device=device
        )
        
        # Update person
        person.mwm = new_mwm
        person.update_timestamp()
        
        logger.debug(f"[PersonModel] Updated MWM for {person.identity.name}")
        
        return person
    
    except Exception as e:
        logger.error(f"[PersonModel] MWM update error for {person.identity.name}: {e}")
        return person


def save_person(person: PersonModel, path: Path):
    """
    Save PersonModel to disk.
    
    Args:
        person: PersonModel to save
        path: Output file path
    """
    try:
        # Convert to dict
        person_dict = person.model_dump()
        
        # Save as JSON
        with open(path, 'w') as f:
            json.dump(person_dict, f, indent=2)
        
        logger.info(f"[PersonModel] Saved {person.identity.name} to {path}")
    
    except Exception as e:
        logger.error(f"[PersonModel] Save error: {e}")


def load_person(path: Path) -> Optional[PersonModel]:
    """
    Load PersonModel from disk.
    
    Args:
        path: Input file path
    
    Returns:
        PersonModel or None if error
    """
    try:
        # Load JSON
        with open(path, 'r') as f:
            person_dict = json.load(f)
        
        # Create PersonModel
        person = PersonModel(**person_dict)
        
        logger.info(f"[PersonModel] Loaded {person.identity.name} from {path}")
        
        return person
    
    except Exception as e:
        logger.error(f"[PersonModel] Load error: {e}")
        return None
