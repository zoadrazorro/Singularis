"""
MWM (Mental World Model) - Agent's internal state of mind

Fuses:
- GWM: Structured game state (threat, enemies, cover)
- IWM: Visual latents and predictions
- Self-state: Health, stamina, mode, confidence
- Affect: Threat, curiosity, value estimates

Provides:
- encode(): Update mental latent from observations
- predict(): Mentally simulate next state given action
- decode(): Map latent to interpretable features

Integrates with:
- BeingState: Stores MWM state
- ActionArbiter: Uses MWM for scoring actions
- PersonModel: Higher-level personality integration
"""

from .types import (
    WorldSlice,
    SelfSlice,
    AffectSlice,
    Hypothesis,
    HypothesisSlice,
    MentalWorldModelState,
    TraitProfile,
    PersonModel
)

from .mwm_module import MentalWorldModelModule

from .integration import (
    pack_gwm_features,
    pack_self_features,
    pack_action_features,
    decode_world_slice,
    decode_self_slice,
    decode_affect_slice,
    update_mwm_from_inputs
)

__all__ = [
    # Types
    'WorldSlice',
    'SelfSlice',
    'AffectSlice',
    'Hypothesis',
    'HypothesisSlice',
    'MentalWorldModelState',
    'TraitProfile',
    'PersonModel',
    # Module
    'MentalWorldModelModule',
    # Integration
    'pack_gwm_features',
    'pack_self_features',
    'pack_action_features',
    'decode_world_slice',
    'decode_self_slice',
    'decode_affect_slice',
    'update_mwm_from_inputs',
]
