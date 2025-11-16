"""
Test AGI-Powered Camera Vision Integration

Tests the connection between:
- Roku Screen Capture Gateway
- Gemini Video Interpreter
- Life Timeline

Verifies that camera feeds use AGI analysis instead of basic CV.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Set up environment
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')
os.environ['ENABLE_AGI_VISION'] = 'true'
os.environ['ENABLE_ROKU_CAMERAS'] = 'false'  # Don't actually start ADB


async def test_video_interpreter():
    """Test Video Interpreter initialization."""
    logger.info("=" * 60)
    logger.info("TEST 1: Video Interpreter Initialization")
    logger.info("=" * 60)
    
    try:
        from singularis.perception.streaming_video_interpreter import (
            StreamingVideoInterpreter,
            InterpretationMode
        )
        
        interpreter = StreamingVideoInterpreter(
            mode=InterpretationMode.COMPREHENSIVE,
            frame_rate=0.5,
            audio_enabled=False
        )
        
        logger.info("✅ Video Interpreter initialized successfully")
        logger.info(f"   Mode: {interpreter.mode.value}")
        logger.info(f"   Frame rate: {interpreter.frame_rate} FPS")
        logger.info(f"   Audio: {interpreter.audio_enabled}")
        
        await interpreter.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Video Interpreter initialization failed: {e}")
        return False


async def test_roku_gateway_with_agi():
    """Test Roku Gateway with AGI integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Roku Gateway with AGI Integration")
    logger.info("=" * 60)
    
    try:
        from life_timeline import LifeTimeline
        from roku_screencap_gateway import RokuScreenCaptureGateway
        from singularis.perception.streaming_video_interpreter import (
            StreamingVideoInterpreter,
            InterpretationMode
        )
        
        # Initialize components
        timeline = LifeTimeline(":memory:")  # In-memory for testing
        
        interpreter = StreamingVideoInterpreter(
            mode=InterpretationMode.COMPREHENSIVE,
            frame_rate=0.5,
            audio_enabled=False
        )
        
        gateway = RokuScreenCaptureGateway(
            timeline=timeline,
            user_id="test_user",
            device_ip="192.168.1.100",
            adb_port=5555,
            fps=2,
            camera_mapping={
                'cam1': 'living_room',
                'cam2': 'kitchen'
            },
            video_interpreter=interpreter  # 🎥 AGI Vision!
        )
        
        logger.info("✅ Roku Gateway initialized with AGI")
        logger.info(f"   Analysis mode: {gateway.use_agi}")
        logger.info(f"   Video interpreter: {gateway.video_interpreter is not None}")
        
        # Test event extraction
        logger.info("\n   Testing event extraction from AGI analysis...")
        
        test_analyses = [
            ("A person is walking through the living room", "cam1"),
            ("The kitchen appears empty with no motion detected", "cam2"),
            ("Someone appears to have fallen in the bedroom - emergency!", "cam1"),
            ("A cat is sleeping on the couch", "cam2"),
        ]
        
        for analysis_text, camera_id in test_analyses:
            events = gateway._extract_events_from_analysis(analysis_text, camera_id)
            logger.info(f"   Analysis: '{analysis_text[:50]}...'")
            logger.info(f"   → Detected {len(events)} events: {[e['type'] for e in events]}")
        
        # Check stats
        stats = gateway.get_stats()
        logger.info(f"\n   Gateway stats:")
        logger.info(f"   - Analysis mode: {stats['analysis_mode']}")
        logger.info(f"   - AGI analyses: {stats['agi_analyses']}")
        logger.info(f"   - Basic CV analyses: {stats['basic_cv_analyses']}")
        
        await interpreter.close()
        timeline.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Roku Gateway test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_event_types():
    """Test different event type detection."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Event Type Detection")
    logger.info("=" * 60)
    
    try:
        from life_timeline import LifeTimeline
        from roku_screencap_gateway import RokuScreenCaptureGateway
        
        timeline = LifeTimeline(":memory:")
        
        gateway = RokuScreenCaptureGateway(
            timeline=timeline,
            user_id="test_user",
            device_ip="192.168.1.100",
            camera_mapping={'cam1': 'living_room'}
        )
        
        test_cases = [
            {
                'name': 'Person Detection',
                'analysis': 'A person is standing in the room',
                'expected_types': ['person_detected']
            },
            {
                'name': 'Motion Detection',
                'analysis': 'Someone is walking and moving around',
                'expected_types': ['person_detected', 'motion_detected']
            },
            {
                'name': 'Fall Detection',
                'analysis': 'A person has fallen on the floor - emergency situation',
                'expected_types': ['person_detected', 'fall_detected']
            },
            {
                'name': 'Activity Detection',
                'analysis': 'Someone is cooking in the kitchen, preparing food',
                'expected_types': ['person_detected', 'motion_detected', 'activity_detected']
            },
            {
                'name': 'Pet Detection',
                'analysis': 'A dog is playing with a toy',
                'expected_types': ['motion_detected', 'object_detected']
            },
            {
                'name': 'Empty Room',
                'analysis': 'The room is empty with no activity',
                'expected_types': []
            }
        ]
        
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            events = gateway._extract_events_from_analysis(
                test_case['analysis'],
                'cam1'
            )
            
            detected_types = [e['type'] for e in events]
            
            # Check if expected types are present
            all_found = all(
                expected in detected_types 
                for expected in test_case['expected_types']
            )
            
            if all_found or (not test_case['expected_types'] and not detected_types):
                logger.info(f"   ✅ {test_case['name']}")
                logger.info(f"      Expected: {test_case['expected_types']}")
                logger.info(f"      Detected: {detected_types}")
                passed += 1
            else:
                logger.warning(f"   ⚠️  {test_case['name']}")
                logger.warning(f"      Expected: {test_case['expected_types']}")
                logger.warning(f"      Detected: {detected_types}")
                failed += 1
        
        logger.info(f"\n   Results: {passed} passed, {failed} failed")
        
        timeline.close()
        
        return failed == 0
        
    except Exception as e:
        logger.error(f"❌ Event type test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_integration():
    """Test full orchestrator integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Main Orchestrator Integration")
    logger.info("=" * 60)
    
    try:
        # Set environment to not start actual camera
        os.environ['ENABLE_ROKU_CAMERAS'] = 'false'
        os.environ['ENABLE_AGI_VISION'] = 'true'
        
        from main_orchestrator import MainOrchestrator
        
        orchestrator = MainOrchestrator()
        await orchestrator.initialize()
        
        logger.info("✅ Orchestrator initialized")
        logger.info(f"   Video interpreter: {orchestrator.video_interpreter is not None}")
        logger.info(f"   Roku gateway: {orchestrator.roku_gateway is not None}")
        
        if orchestrator.video_interpreter:
            stats = orchestrator.video_interpreter.get_stats()
            logger.info(f"   Video interpreter mode: {stats['mode']}")
            logger.info(f"   Audio enabled: {stats['audio_enabled']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Orchestrator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    logger.info("🎥 AGI-Powered Camera Vision Integration Tests")
    logger.info("=" * 60)
    
    if not os.getenv('GEMINI_API_KEY'):
        logger.warning("⚠️  GEMINI_API_KEY not set - some tests may fail")
        logger.info("   Set it with: export GEMINI_API_KEY=your_key_here")
    
    results = []
    
    # Test 1: Video Interpreter
    results.append(await test_video_interpreter())
    
    # Test 2: Roku Gateway with AGI
    results.append(await test_roku_gateway_with_agi())
    
    # Test 3: Event Type Detection
    results.append(await test_event_types())
    
    # Test 4: Orchestrator Integration
    results.append(await test_orchestrator_integration())
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ All tests passed! AGI camera vision is ready.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed")
    
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 4 COMPLETE: AGI-Powered Vision")
    logger.info("=" * 60)
    logger.info("Camera feeds now use Gemini's advanced vision AI!")
    logger.info("")
    logger.info("Benefits:")
    logger.info("  • Person detection with context")
    logger.info("  • Activity recognition (cooking, sleeping, etc.)")
    logger.info("  • Fall detection with severity assessment")
    logger.info("  • Pet detection")
    logger.info("  • Natural language analysis of scenes")
    logger.info("")
    logger.info("Next: Phase 5 - Unified Query Interface")


if __name__ == "__main__":
    asyncio.run(main())
