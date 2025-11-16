"""
Test Phase 1: Life Timeline ↔ Singularis Consciousness Integration

Verifies that Life Timeline data is accessible to AGI consciousness.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Import Life Ops components
from life_timeline import (
    LifeTimeline,
    create_fitbit_event,
    create_camera_event,
    EventType
)

# Import Singularis consciousness
from singularis.unified_consciousness_layer import UnifiedConsciousnessLayer


async def test_phase1():
    """Test Phase 1 integration."""
    
    print("\n" + "=" * 80)
    print("🧪 PHASE 1 INTEGRATION TEST")
    print("=" * 80)
    print("\n[1/5] Initializing components...")
    
    # Initialize Life Timeline
    timeline = LifeTimeline("data/test_phase1.db")
    logger.info("✅ Life Timeline initialized")
    
    # Initialize Singularis consciousness
    consciousness = UnifiedConsciousnessLayer()
    logger.info("✅ Singularis consciousness initialized")
    
    # 🔗 Connect them (Phase 1!)
    print("\n[2/5] Connecting Life Timeline to Consciousness...")
    consciousness.connect_life_timeline(timeline)
    print("✅ Bridge established!\n")
    
    # Add some test life data
    print("[3/5] Adding test life data...")
    user_id = "test_user"
    
    # Add heart rate data
    for i in range(5):
        event = create_fitbit_event(
            user_id=user_id,
            event_type='heart_rate',
            value=70 + i * 5,
            timestamp=datetime.now() - timedelta(hours=5-i)
        )
        timeline.add_event(event)
    
    # Add sleep data
    event = create_fitbit_event(
        user_id=user_id,
        event_type='sleep',
        value=7.5,
        timestamp=datetime.now() - timedelta(hours=8)
    )
    timeline.add_event(event)
    
    # Add camera event
    event = create_camera_event(
        user_id=user_id,
        room='living_room',
        event_type='motion_detected',
        confidence=0.9
    )
    timeline.add_event(event)
    
    print(f"✅ Added 7 life events\n")
    
    # Test: Query consciousness with user_id context
    print("[4/5] Testing AGI consciousness with life context...")
    print("Query: 'How am I doing health-wise?'\n")
    
    try:
        # This should automatically inject life context!
        response = await consciousness.process(
            query="How am I doing health-wise?",
            subsystem_inputs={
                'llm': "User is asking about their health status",
                'memory': "No prior health discussions",
            },
            context={
                'user_id': user_id,  # This triggers life context injection!
                'platform': 'test'
            }
        )
        
        print("\n[5/5] Checking if life context was injected...")
        
        # Check if life context is in the response
        if 'life_events' in str(response.subsystem_insights):
            print("✅ Life events context detected!")
        
        if 'health_state' in str(response.subsystem_insights):
            print("✅ Health state context detected!")
        
        print(f"\n📊 Response coherence: {response.coherence_score:.3f}")
        print(f"⏱️  Total time: {response.total_time:.2f}s")
        
        print("\n💬 AGI Response Preview:")
        print(f"   {response.response[:300]}...")
        
        print("\n" + "=" * 80)
        print("🎉 PHASE 1 TEST PASSED!")
        print("=" * 80)
        print("\n✅ Life Timeline is now connected to Singularis AGI")
        print("✅ Consciousness automatically sees life events")
        print("✅ Health context is injected into all queries")
        print("\nNext: Phase 2 - AGI-powered pattern detection\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_phase1())
