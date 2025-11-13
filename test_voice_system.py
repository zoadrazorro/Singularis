"""
Test the AGI Voice System using Gemini 2.5 Pro TTS.

This demonstrates the AGI speaking its thoughts aloud.
"""

import asyncio
from singularis.consciousness import VoiceSystem, VoiceType, ThoughtPriority


async def main():
    print("="*70)
    print("AGI VOICE SYSTEM TEST")
    print("="*70)
    print()
    
    # Initialize voice system
    voice = VoiceSystem(
        voice=VoiceType.NOVA,  # Female, warm voice
        enabled=True,
        min_priority=ThoughtPriority.MEDIUM
    )
    
    print("[VOICE] Voice system initialized")
    print(f"[VOICE] Using {voice.voice.value} voice")
    print()
    
    try:
        # Test different types of vocalizations
        print("[TEST] Speaking a decision...")
        await voice.speak_decision(
            action="explore the northern passage",
            reason="The path appears safe and unexplored"
        )
        
        await asyncio.sleep(1)
        
        print("[TEST] Speaking an insight...")
        await voice.speak_insight(
            "I notice a pattern in enemy behavior. They seem to guard specific locations."
        )
        
        await asyncio.sleep(1)
        
        print("[TEST] Speaking a goal...")
        await voice.speak_goal(
            "Find the ancient artifact in the depths of the dungeon"
        )
        
        await asyncio.sleep(1)
        
        print("[TEST] Speaking a warning...")
        await voice.speak_warning(
            "Health critical! I must find healing immediately."
        )
        
        # Wait for all speech to complete
        await asyncio.sleep(2)
        
        # Show statistics
        stats = voice.get_stats()
        print()
        print("="*70)
        print("VOICE SYSTEM STATISTICS")
        print("="*70)
        print(f"Total thoughts: {stats['total_thoughts']}")
        print(f"Spoken thoughts: {stats['spoken_thoughts']}")
        print(f"Queued thoughts: {stats['queued_thoughts']}")
        print(f"Voice: {stats['voice']}")
        print(f"Enabled: {stats['enabled']}")
        
    finally:
        await voice.close()
        print()
        print("[VOICE] Voice system closed")


if __name__ == "__main__":
    asyncio.run(main())
