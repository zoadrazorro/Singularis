"""
Test GWM System - Quick validation script

Tests:
1. Service health check
2. Send snapshot
3. Get features
4. Get entities
5. BeingState integration

Usage:
    # Start service first:
    python start_gwm_service.py --port 8002
    
    # Then run tests:
    python test_gwm_system.py
"""

import asyncio
import time
from loguru import logger

from singularis.gwm import GWMClient
from singularis.core.being_state import BeingState


async def test_service_health(client: GWMClient):
    """Test 1: Check service health."""
    logger.info("Test 1: Checking service health...")
    
    try:
        health = await client.health()
        
        if health['status'] == 'ok':
            logger.info(f"✓ Service healthy: {health}")
            return True
        else:
            logger.error(f"✗ Service not healthy: {health}")
            return False
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False


async def test_send_snapshot(client: GWMClient):
    """Test 2: Send snapshot."""
    logger.info("Test 2: Sending snapshot...")
    
    try:
        # Create test snapshot
        snapshot = {
            "timestamp": time.time(),
            "cell_name": "TestCell",
            "is_interior": False,
            "player": {
                "id": "player",
                "pos": [0.0, 0.0, 0.0],
                "vel": [0.0, 0.0, 0.0],
                "facing_yaw": 90.0,
                "facing_pitch": 0.0,
                "health": 0.75,
                "stamina": 0.60,
                "magicka": 0.50,
                "sneaking": False,
                "in_combat": True,
                "weapon_type": "sword",
                "is_detected": False
            },
            "npcs": [
                {
                    "id": "enemy_001",
                    "pos": [10.0, 2.0, 0.0],
                    "vel": [0.0, 0.0, 0.0],
                    "facing_yaw": 270.0,
                    "health": 0.80,
                    "is_enemy": True,
                    "is_ally": False,
                    "is_alive": True,
                    "is_in_combat": True,
                    "has_line_of_sight_to_player": True,
                    "distance_to_player": 10.2,
                    "awareness_level": 0.9
                },
                {
                    "id": "enemy_002",
                    "pos": [15.0, -3.0, 0.0],
                    "health": 0.60,
                    "is_enemy": True,
                    "is_alive": True,
                    "is_in_combat": True,
                    "has_line_of_sight_to_player": False,
                    "distance_to_player": 15.5,
                    "awareness_level": 0.4
                }
            ],
            "objects": [
                {
                    "id": "chest_01",
                    "type": "container",
                    "pos": [5.0, -3.0, 0.0],
                    "is_locked": False,
                    "is_open": False
                },
                {
                    "id": "door_01",
                    "type": "door",
                    "pos": [20.0, 0.0, 0.0],
                    "is_locked": False,
                    "is_open": True
                }
            ],
            "cover_spots_raw": [
                {
                    "id": "pillar_01",
                    "pos": [3.0, 1.0, 0.0],
                    "cover_rating": 0.8
                }
            ],
            "recent_events": [
                "enemy_spotted_player",
                "player_drew_weapon"
            ]
        }
        
        result = await client.send_snapshot(snapshot)
        
        logger.info(f"✓ Snapshot sent: {result}")
        logger.info(f"  Entities tracked: {result['entities_tracked']}")
        return True
    except Exception as e:
        logger.error(f"✗ Send snapshot failed: {e}")
        return False


async def test_get_features(client: GWMClient):
    """Test 3: Get tactical features."""
    logger.info("Test 3: Getting tactical features...")
    
    try:
        features = await client.get_features()
        
        logger.info(f"✓ Features retrieved:")
        logger.info(f"  Threat level: {features['threat_level']:.2f}")
        logger.info(f"  Num enemies: {features['num_enemies_total']}")
        logger.info(f"  Enemies in LOS: {features['num_enemies_in_los']}")
        
        if features['nearest_enemy']:
            logger.info(f"  Nearest enemy: {features['nearest_enemy']['id']} at {features['nearest_enemy']['distance']:.1f}m")
        
        if features['best_cover_spot']:
            logger.info(f"  Best cover: {features['best_cover_spot']['id']} at {features['best_cover_spot']['distance']:.1f}m")
        
        logger.info(f"  Escape vector: {features['escape_vector']}")
        logger.info(f"  Stealth safety: {features['stealth_safety_score']:.2f}")
        logger.info(f"  Loot available: {features['loot_opportunity_available']}")
        
        return features
    except Exception as e:
        logger.error(f"✗ Get features failed: {e}")
        return None


async def test_get_entities(client: GWMClient):
    """Test 4: Get entity states."""
    logger.info("Test 4: Getting entity states...")
    
    try:
        entities = await client.get_entities()
        
        logger.info(f"✓ Entities retrieved:")
        logger.info(f"  Player: {entities['player']['id'] if entities['player'] else 'None'}")
        logger.info(f"  NPCs: {len(entities['npcs'])}")
        logger.info(f"  Objects: {len(entities['objects'])}")
        logger.info(f"  Cover spots: {len(entities['cover_spots'])}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Get entities failed: {e}")
        return False


async def test_being_state_integration(features: dict):
    """Test 5: BeingState integration."""
    logger.info("Test 5: BeingState integration...")
    
    try:
        being_state = BeingState()
        
        # Set GWM features
        being_state.game_world = features
        being_state.gwm_threat_level = features['threat_level']
        being_state.gwm_num_enemies = features['num_enemies_total']
        being_state.gwm_timestamp = time.time()
        
        if features['nearest_enemy']:
            being_state.gwm_nearest_enemy_distance = features['nearest_enemy']['distance']
        
        if features['best_cover_spot']:
            being_state.gwm_best_cover_distance = features['best_cover_spot']['distance']
        
        being_state.gwm_stealth_safety = features['stealth_safety_score']
        being_state.gwm_loot_available = features['loot_opportunity_available']
        
        # Export snapshot
        snapshot = being_state.export_snapshot()
        
        assert 'game_world_model' in snapshot
        assert snapshot['game_world_model']['has_features'] == True
        
        logger.info(f"✓ BeingState integration works")
        logger.info(f"  GWM data: {snapshot['game_world_model']}")
        return True
    except Exception as e:
        logger.error(f"✗ BeingState integration failed: {e}")
        return False


async def main():
    logger.info("=" * 60)
    logger.info("GWM Game World Model - System Test")
    logger.info("=" * 60)
    
    logger.info("\nConnecting to GWM service at http://localhost:8002...")
    client = GWMClient("http://localhost:8002")
    
    try:
        # Test 1: Health
        if not await test_service_health(client):
            logger.error("Service not available. Start with: python start_gwm_service.py")
            return
        
        # Test 2: Send snapshot
        if not await test_send_snapshot(client):
            return
        
        # Test 3: Get features
        features = await test_get_features(client)
        if features is None:
            return
        
        # Test 4: Get entities
        if not await test_get_entities(client):
            return
        
        # Test 5: BeingState
        await test_being_state_integration(features)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests passed!")
        logger.info("=" * 60)
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
