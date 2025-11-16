"""
Test MWM System - Validation script

Tests:
1. MWM module creation
2. Encode → Decode flow
3. Predict flow
4. Integration with BeingState
5. Action scoring

Usage:
    python test_mwm_system.py
"""

import torch
import numpy as np
import time
from loguru import logger

from singularis.mwm import (
    MentalWorldModelModule,
    MentalWorldModelState,
    WorldSlice,
    SelfSlice,
    AffectSlice,
    pack_gwm_features,
    pack_self_features,
    pack_action_features,
    decode_world_slice,
    decode_self_slice,
    decode_affect_slice,
    update_mwm_from_inputs,
    score_action_with_mwm
)

from singularis.core.being_state import BeingState


def test_module_creation():
    """Test 1: Create MWM module."""
    logger.info("Test 1: Creating MWM module...")
    
    try:
        mwm = MentalWorldModelModule(latent_dim=256)
        
        # Check parameter counts
        param_counts = mwm.get_parameter_count()
        logger.info(f"✓ Module created: {param_counts['total']:,} parameters")
        logger.info(f"  Encoders: {param_counts.get('gwm_encoder', 0) + param_counts.get('iwm_encoder', 0) + param_counts.get('self_encoder', 0):,}")
        logger.info(f"  Decoders: {param_counts.get('world_decoder', 0) + param_counts.get('self_decoder', 0) + param_counts.get('affect_decoder', 0):,}")
        
        return mwm
    except Exception as e:
        logger.error(f"✗ Module creation failed: {e}")
        return None


def test_encode_decode(mwm: MentalWorldModelModule, device: torch.device):
    """Test 2: Encode → Decode flow."""
    logger.info("Test 2: Testing encode → decode...")
    
    try:
        # Create dummy inputs
        z_prev = mwm.init_latent(batch_size=1, device=device)
        gwm_feats = torch.randn(1, 16, device=device)
        iwm_latent = torch.randn(1, 768, device=device)
        self_feats = torch.randn(1, 8, device=device)
        
        # Encode
        z_t = mwm.encode(z_prev, gwm_feats, iwm_latent, self_feats)
        logger.info(f"  Encoded latent shape: {z_t.shape}")
        
        # Decode
        decoded = mwm.decode(z_t)
        logger.info(f"  Decoded world: {decoded['world'].shape}")
        logger.info(f"  Decoded self: {decoded['self'].shape}")
        logger.info(f"  Decoded affect: {decoded['affect'].shape}")
        
        logger.info("✓ Encode → decode works")
        return True
    except Exception as e:
        logger.error(f"✗ Encode → decode failed: {e}")
        return False


def test_predict(mwm: MentalWorldModelModule, device: torch.device):
    """Test 3: Predict flow."""
    logger.info("Test 3: Testing predict...")
    
    try:
        # Create dummy latent and action
        z_t = torch.randn(1, 256, device=device)
        action_feats = torch.randn(1, 16, device=device)
        
        # Predict
        z_hat = mwm.predict(z_t, action_feats)
        logger.info(f"  Predicted latent shape: {z_hat.shape}")
        
        # Decode prediction
        decoded = mwm.decode(z_hat)
        logger.info(f"  Predicted world threat: {decoded['world'][0, 0].item():.3f}")
        logger.info(f"  Predicted affect threat: {decoded['affect'][0, 0].item():.3f}")
        
        logger.info("✓ Predict works")
        return True
    except Exception as e:
        logger.error(f"✗ Predict failed: {e}")
        return False


def test_packing_unpacking():
    """Test 4: Packing/unpacking utilities."""
    logger.info("Test 4: Testing packing/unpacking...")
    
    try:
        # Pack GWM features
        gwm_dict = {
            'threat_level': 0.75,
            'num_enemies_total': 3,
            'num_enemies_in_los': 2,
            'nearest_enemy': {'distance': 12.5, 'bearing_deg': 45.0, 'health': 0.6},
            'escape_vector': [-0.8, -0.6],
            'stealth_safety_score': 0.4,
            'loot_opportunity_available': True
        }
        
        gwm_packed = pack_gwm_features(gwm_dict)
        logger.info(f"  Packed GWM shape: {gwm_packed.shape}")
        logger.info(f"  Packed GWM sample: {gwm_packed[:5]}")
        
        # Pack self features
        being_state = BeingState()
        being_state.game_state = {
            'player_health': 0.65,
            'player_stamina': 0.40,
            'player_magicka': 0.80,
            'is_sneaking': True,
            'in_combat': False
        }
        
        self_packed = pack_self_features(being_state)
        logger.info(f"  Packed self shape: {self_packed.shape}")
        logger.info(f"  Packed self sample: {self_packed[:5]}")
        
        # Decode world slice
        world_vec = torch.tensor([0.75, 3.0, 2.0, 0.0, 12.5, 45.0, 0.6, 999.0, 0.0, -0.8, -0.6, 0.4, 0.0, 1.0, 999.0, 0.0])
        world_slice = decode_world_slice(world_vec)
        logger.info(f"  Decoded world: threat={world_slice.threat_level:.2f}, enemies={world_slice.num_enemies}")
        
        logger.info("✓ Packing/unpacking works")
        return True
    except Exception as e:
        logger.error(f"✗ Packing/unpacking failed: {e}")
        return False


def test_being_state_integration(mwm: MentalWorldModelModule, device: torch.device):
    """Test 5: BeingState integration."""
    logger.info("Test 5: Testing BeingState integration...")
    
    try:
        # Create BeingState with GWM and IWM data
        being_state = BeingState()
        
        # Mock GWM features
        being_state.game_world = {
            'threat_level': 0.7,
            'num_enemies_total': 2,
            'num_enemies_in_los': 1,
            'nearest_enemy': {'distance': 15.0, 'bearing_deg': 30.0, 'health': 0.8},
            'escape_vector': [-0.7, -0.7],
            'stealth_safety_score': 0.5,
            'loot_opportunity_available': False
        }
        
        # Mock IWM latent
        being_state.vision_core_latent = np.random.randn(768).astype(np.float32)
        
        # Mock self-state
        being_state.game_state = {
            'player_health': 0.65,
            'player_stamina': 0.40,
            'player_magicka': 0.80,
            'is_sneaking': False,
            'in_combat': True
        }
        
        # Initialize MWM state
        mwm_state = MentalWorldModelState()
        
        # Update MWM
        new_mwm_state = update_mwm_from_inputs(
            mwm_state=mwm_state,
            gwm_features=being_state.game_world,
            iwm_latent=being_state.vision_core_latent,
            being_state=being_state,
            mwm_module=mwm,
            device=device
        )
        
        logger.info(f"  MWM updated: {new_mwm_state.update_count} updates")
        logger.info(f"  World threat: {new_mwm_state.world.threat_level:.2f}")
        logger.info(f"  Self health: {new_mwm_state.self_state.health:.2f}")
        logger.info(f"  Affect threat: {new_mwm_state.affect.threat:.2f}")
        logger.info(f"  Affect curiosity: {new_mwm_state.affect.curiosity:.2f}")
        logger.info(f"  Affect value: {new_mwm_state.affect.value_estimate:.2f}")
        
        # Write to BeingState
        being_state.mwm = new_mwm_state.model_dump()
        being_state.mwm_threat_perception = new_mwm_state.affect.threat
        being_state.mwm_curiosity = new_mwm_state.affect.curiosity
        being_state.mwm_value_estimate = new_mwm_state.affect.value_estimate
        being_state.mwm_timestamp = time.time()
        
        # Check export
        snapshot = being_state.export_snapshot()
        assert 'mental_world_model' in snapshot
        logger.info(f"  BeingState MWM: {snapshot['mental_world_model']}")
        
        logger.info("✓ BeingState integration works")
        return new_mwm_state
    except Exception as e:
        logger.error(f"✗ BeingState integration failed: {e}")
        return None


def test_action_scoring(mwm: MentalWorldModelModule, mwm_state: MentalWorldModelState, device: torch.device):
    """Test 6: Action scoring."""
    logger.info("Test 6: Testing action scoring...")
    
    try:
        # Mock action
        class MockAction:
            def __init__(self, action_type: str):
                self.action_type = action_type
                self.duration = 1.0
                self.magnitude = 1.0
        
        actions = [
            MockAction("move_forward"),
            MockAction("attack"),
            MockAction("block"),
            MockAction("sneak")
        ]
        
        scores = {}
        for action in actions:
            score = score_action_with_mwm(action, mwm_state, mwm, device)
            scores[action.action_type] = score
            logger.info(f"  {action.action_type}: {score:.3f}")
        
        best_action = max(scores, key=scores.get)
        logger.info(f"  Best action: {best_action}")
        
        logger.info("✓ Action scoring works")
        return True
    except Exception as e:
        logger.error(f"✗ Action scoring failed: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("MWM Mental World Model - System Test")
    logger.info("=" * 60)
    
    # Device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info(f"\nUsing device: {device}")
    
    # Test 1: Module creation
    mwm = test_module_creation()
    if mwm is None:
        return
    
    mwm = mwm.to(device)
    mwm.eval()
    
    # Test 2: Encode → Decode
    if not test_encode_decode(mwm, device):
        return
    
    # Test 3: Predict
    if not test_predict(mwm, device):
        return
    
    # Test 4: Packing/unpacking
    if not test_packing_unpacking():
        return
    
    # Test 5: BeingState integration
    mwm_state = test_being_state_integration(mwm, device)
    if mwm_state is None:
        return
    
    # Test 6: Action scoring
    if not test_action_scoring(mwm, mwm_state, device):
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ All tests passed!")
    logger.info("=" * 60)
    logger.info("\nMWM is ready to integrate into main loop.")
    logger.info("Next steps:")
    logger.info("1. Wire update_mwm_from_inputs into SkyrimAGI cycle")
    logger.info("2. Use mwm_* fields in ActionArbiter scoring")
    logger.info("3. Add training data logging")
    logger.info("4. Train MWM on collected data")


if __name__ == "__main__":
    main()
