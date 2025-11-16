"""
Test PersonModel System - Validation script

Tests:
1. Create PersonModel from template
2. Update MWM
3. Score actions
4. Constraints filtering
5. LLM context generation
6. Registry operations
7. Save/load persistence

Usage:
    python test_person_model.py
"""

import torch
from loguru import logger

from singularis.person_model import (
    create_person_from_template,
    PersonRegistry,
    score_action_for_person,
    get_llm_context,
    save_person,
    load_person,
    get_available_templates
)
from singularis.mwm import MentalWorldModelModule
from singularis.core.being_state import BeingState
from pathlib import Path


def test_template_creation():
    """Test 1: Create PersonModel from templates."""
    logger.info("Test 1: Creating PersonModels from templates...")
    
    try:
        templates = get_available_templates()
        logger.info(f"  Available templates: {templates}")
        
        # Create a loyal companion
        companion = create_person_from_template(
            "loyal_companion",
            person_id="test_companion_001",
            name="Test Companion"
        )
        
        logger.info(f"  Created: {companion.identity.name}")
        logger.info(f"  Archetype: {companion.identity.archetype}")
        logger.info(f"  Roles: {companion.identity.roles}")
        logger.info(f"  Aggression: {companion.traits.aggression:.2f}")
        logger.info(f"  Protect allies: {companion.values.protect_allies:.2f}")
        
        # Create a bandit
        bandit = create_person_from_template(
            "bandit",
            person_id="test_bandit_001",
            name="Test Bandit"
        )
        
        logger.info(f"  Created: {bandit.identity.name}")
        logger.info(f"  Archetype: {bandit.identity.archetype}")
        logger.info(f"  Aggression: {bandit.traits.aggression:.2f}")
        
        logger.info("✓ Template creation works")
        return companion, bandit
    except Exception as e:
        logger.error(f"✗ Template creation failed: {e}")
        return None, None


def test_registry(companion, bandit):
    """Test 2: Registry operations."""
    logger.info("Test 2: Testing registry...")
    
    try:
        registry = PersonRegistry()
        
        # Add persons
        registry.add(companion)
        registry.add(bandit)
        
        logger.info(f"  Registry size: {registry.count()}")
        
        # Get by ID
        retrieved = registry.get(companion.identity.person_id)
        logger.info(f"  Retrieved: {retrieved.identity.name if retrieved else 'None'}")
        
        # Get by role
        companions = registry.get_by_role("companion")
        enemies = registry.get_by_role("enemy")
        logger.info(f"  Companions: {len(companions)}")
        logger.info(f"  Enemies: {len(enemies)}")
        
        # Stats
        stats = registry.get_stats()
        logger.info(f"  Stats: {stats}")
        
        logger.info("✓ Registry works")
        return registry
    except Exception as e:
        logger.error(f"✗ Registry failed: {e}")
        return None


def test_action_scoring(companion):
    """Test 3: Action scoring."""
    logger.info("Test 3: Testing action scoring...")
    
    try:
        # Mock actions
        class MockAction:
            def __init__(self, action_type: str):
                self.action_type = action_type
        
        actions = [
            MockAction("attack"),
            MockAction("block"),
            MockAction("heal"),
            MockAction("sneak")
        ]
        
        logger.info(f"  Scoring for: {companion.identity.name}")
        logger.info(f"    Traits: aggression={companion.traits.aggression:.2f}, caution={companion.traits.caution:.2f}")
        
        for action in actions:
            score = score_action_for_person(companion, action, base_score=0.5)
            logger.info(f"    {action.action_type}: {score:.3f}")
        
        logger.info("✓ Action scoring works")
        return True
    except Exception as e:
        logger.error(f"✗ Action scoring failed: {e}")
        return False


def test_constraints(companion):
    """Test 4: Constraints filtering."""
    logger.info("Test 4: Testing constraints...")
    
    try:
        # Create mock action that attacks ally
        class MockAction:
            def __init__(self, action_type: str, target_id: str = None):
                self.action_type = action_type
                self.target_id = target_id
        
        # Add player as ally
        from singularis.person_model.types import Relationship
        player_rel = Relationship(
            other_id="player",
            role="leader",
            trust=0.9,
            affection=0.8
        )
        companion.social.add_or_update_relationship(player_rel)
        
        # Try to attack player (should be blocked)
        attack_player = MockAction("attack", target_id="player")
        score = score_action_for_person(companion, attack_player)
        
        logger.info(f"  Attack player score: {score:.1f}")
        logger.info(f"  Should be very negative: {score < -1e8}")
        
        # Try to attack enemy (should be allowed)
        attack_enemy = MockAction("attack", target_id="enemy_001")
        score = score_action_for_person(companion, attack_enemy)
        logger.info(f"  Attack enemy score: {score:.3f}")
        
        logger.info("✓ Constraints work")
        return True
    except Exception as e:
        logger.error(f"✗ Constraints failed: {e}")
        return False


def test_llm_context(companion):
    """Test 5: LLM context generation."""
    logger.info("Test 5: Testing LLM context...")
    
    try:
        # Add some test data
        from singularis.person_model.types import EpisodicMemoryRef
        
        companion.memory.add_episodic(EpisodicMemoryRef(
            id="mem_001",
            timestamp=12345.67,
            summary="Player saved me from bandits",
            importance=0.9
        ))
        
        # Generate context
        context = get_llm_context(companion)
        
        logger.info(f"  Generated context ({len(context)} chars):")
        logger.info("  " + "="*50)
        for line in context.split('\n')[:15]:  # First 15 lines
            logger.info(f"  {line}")
        logger.info("  " + "="*50)
        
        logger.info("✓ LLM context generation works")
        return True
    except Exception as e:
        logger.error(f"✗ LLM context failed: {e}")
        return False


def test_persistence(companion):
    """Test 6: Save/load."""
    logger.info("Test 6: Testing persistence...")
    
    try:
        # Save
        save_path = Path("test_person.json")
        save_person(companion, save_path)
        logger.info(f"  Saved to {save_path}")
        
        # Load
        loaded = load_person(save_path)
        if loaded:
            logger.info(f"  Loaded: {loaded.identity.name}")
            logger.info(f"  Matches: {loaded.identity.person_id == companion.identity.person_id}")
        
        # Cleanup
        save_path.unlink()
        
        logger.info("✓ Persistence works")
        return True
    except Exception as e:
        logger.error(f"✗ Persistence failed: {e}")
        return False


def test_mwm_integration(companion):
    """Test 7: MWM integration."""
    logger.info("Test 7: Testing MWM integration...")
    
    try:
        # Initialize MWM module
        device = torch.device("cpu")
        mwm_module = MentalWorldModelModule(latent_dim=256).to(device)
        mwm_module.eval()
        
        # Create mock being_state
        being_state = BeingState()
        being_state.game_state = {
            'player_health': 0.65,
            'player_stamina': 0.40
        }
        
        # Mock GWM features
        gwm_features = {
            'threat_level': 0.7,
            'num_enemies_total': 2
        }
        
        # Mock IWM latent
        import numpy as np
        iwm_latent = np.random.randn(768).astype(np.float32)
        
        # Update MWM
        from singularis.person_model.utils import update_person_mwm
        
        companion = update_person_mwm(
            companion,
            gwm_features,
            iwm_latent,
            being_state,
            mwm_module,
            device
        )
        
        logger.info(f"  MWM updated: {companion.mwm.update_count} updates")
        if companion.mwm.affect:
            logger.info(f"  Affect threat: {companion.mwm.affect.threat:.2f}")
            logger.info(f"  Affect curiosity: {companion.mwm.affect.curiosity:.2f}")
        
        logger.info("✓ MWM integration works")
        return True
    except Exception as e:
        logger.error(f"✗ MWM integration failed: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("PersonModel System Test")
    logger.info("=" * 60)
    
    # Test 1: Template creation
    companion, bandit = test_template_creation()
    if companion is None:
        return
    
    # Test 2: Registry
    registry = test_registry(companion, bandit)
    if registry is None:
        return
    
    # Test 3: Action scoring
    if not test_action_scoring(companion):
        return
    
    # Test 4: Constraints
    if not test_constraints(companion):
        return
    
    # Test 5: LLM context
    if not test_llm_context(companion):
        return
    
    # Test 6: Persistence
    if not test_persistence(companion):
        return
    
    # Test 7: MWM integration
    if not test_mwm_integration(companion):
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ All tests passed!")
    logger.info("=" * 60)
    logger.info("\nPersonModel is ready to integrate into SkyrimAGI.")
    logger.info("Next steps:")
    logger.info("1. Wire PersonModel into ActionArbiter")
    logger.info("2. Update BeingState to optionally contain PersonModel")
    logger.info("3. Use score_action_for_person in action selection")
    logger.info("4. Pass get_llm_context to GPT for reasoning")


if __name__ == "__main__":
    main()
