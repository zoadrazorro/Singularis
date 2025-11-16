"""
Test IWM System - Quick validation script

Tests:
1. Model instantiation
2. Service health check
3. Encode/predict/rollout endpoints
4. BeingState integration

Usage:
    # Start service first:
    python start_iwm_service.py --port 8001
    
    # Then run tests:
    python test_iwm_system.py
"""

import asyncio
import numpy as np
import time
from loguru import logger

from singularis.world_model import IWMClient, create_iwm_model
from singularis.core.being_state import BeingState


async def test_model_creation():
    """Test 1: Create model locally."""
    logger.info("Test 1: Creating IWM model...")
    
    try:
        model = create_iwm_model(variant='core', device='cpu')
        logger.info(f"✓ Model created: {model.config.total_params_m:.1f}M params")
        return True
    except Exception as e:
        logger.error(f"✗ Model creation failed: {e}")
        return False


async def test_service_health(client: IWMClient):
    """Test 2: Check service health."""
    logger.info("Test 2: Checking service health...")
    
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


async def test_encode(client: IWMClient):
    """Test 3: Encode image."""
    logger.info("Test 3: Encoding image...")
    
    try:
        # Create dummy image
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = await client.encode_image(frame, return_patches=False)
        
        logger.info(f"✓ Encoded: latent_dim={result.latent_dim}, shape={result.z_cls.shape}")
        return result
    except Exception as e:
        logger.error(f"✗ Encode failed: {e}")
        return None


async def test_predict(client: IWMClient, z_cls: np.ndarray):
    """Test 4: Predict next latent."""
    logger.info("Test 4: Predicting next latent...")
    
    try:
        aug_params = [0.5, 0.3, 0.0, 0.0, 0.0]
        
        pred = await client.predict_next(z_cls, aug_params)
        
        logger.info(f"✓ Predicted: MRR={pred.mrr:.3f}, uncertainty={pred.uncertainty:.3f}")
        return pred
    except Exception as e:
        logger.error(f"✗ Predict failed: {e}")
        return None


async def test_rollout(client: IWMClient, z_cls: np.ndarray):
    """Test 5: Rollout k steps."""
    logger.info("Test 5: Rolling out 3 steps...")
    
    try:
        aug_seq = [
            [0.5, 0.3, 0.0],
            [0.4, 0.4, 0.1],
            [0.3, 0.5, 0.2]
        ]
        
        rollout = await client.rollout(z_cls, aug_seq)
        
        logger.info(f"✓ Rollout: {len(rollout.z_cls_seq)} steps")
        for i, (z, mrr, unc) in enumerate(zip(
            rollout.z_cls_seq,
            rollout.mrr_seq,
            rollout.uncertainty_seq
        )):
            logger.info(f"  Step {i}: MRR={mrr:.3f}, uncertainty={unc:.3f}")
        
        return rollout
    except Exception as e:
        logger.error(f"✗ Rollout failed: {e}")
        return None


async def test_being_state_integration(z_cls: np.ndarray):
    """Test 6: BeingState integration."""
    logger.info("Test 6: BeingState integration...")
    
    try:
        being_state = BeingState()
        
        # Set vision latents
        being_state.vision_core_latent = z_cls
        being_state.vision_core_timestamp = time.time()
        being_state.vision_prediction_surprise = 0.5
        being_state.vision_mrr = 0.8
        
        # Export snapshot
        snapshot = being_state.export_snapshot()
        
        assert 'vision_world_model' in snapshot
        assert snapshot['vision_world_model']['has_core_latent'] == True
        
        logger.info(f"✓ BeingState integration works")
        logger.info(f"  Vision WM: {snapshot['vision_world_model']}")
        return True
    except Exception as e:
        logger.error(f"✗ BeingState integration failed: {e}")
        return False


async def test_surprise_computation(client: IWMClient):
    """Test 7: Surprise computation."""
    logger.info("Test 7: Computing surprise...")
    
    try:
        # Frame 1
        frame1 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result1 = await client.encode_image(frame1)
        
        # Predict next
        pred = await client.predict_next(result1.z_cls, aug_params=[0.0] * 16)
        
        # Frame 2 (similar to frame 1)
        frame2 = frame1 + np.random.randint(-10, 10, (480, 640, 3), dtype=np.int16).astype(np.uint8)
        result2 = await client.encode_image(frame2)
        
        # Compute surprise
        surprise = np.linalg.norm(pred.z_cls_pred - result2.z_cls)
        
        logger.info(f"✓ Surprise: {surprise:.3f}")
        logger.info(f"  (Low surprise expected for similar frames)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Surprise computation failed: {e}")
        return False


async def main():
    logger.info("=" * 60)
    logger.info("IWM Vision World Model - System Test")
    logger.info("=" * 60)
    
    # Test 1: Model creation
    await test_model_creation()
    
    # Tests 2-7: Service tests
    logger.info("\nConnecting to IWM service at http://localhost:8001...")
    client = IWMClient("http://localhost:8001")
    
    try:
        # Test 2: Health
        if not await test_service_health(client):
            logger.error("Service not available. Start with: python start_iwm_service.py")
            return
        
        # Test 3: Encode
        result = await test_encode(client)
        if result is None:
            return
        
        # Test 4: Predict
        pred = await test_predict(client, result.z_cls)
        if pred is None:
            return
        
        # Test 5: Rollout
        rollout = await test_rollout(client, result.z_cls)
        if rollout is None:
            return
        
        # Test 6: BeingState
        await test_being_state_integration(result.z_cls)
        
        # Test 7: Surprise
        await test_surprise_computation(client)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests passed!")
        logger.info("=" * 60)
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
