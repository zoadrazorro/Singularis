"""
Test GPT-5 Orchestrator with verbose console output.

Demonstrates all systems communicating through GPT-5.
"""

import asyncio
from singularis.llm import GPT5Orchestrator, SystemType


async def main():
    # Initialize orchestrator with verbose output
    orchestrator = GPT5Orchestrator(
        model="gpt-5",  # GPT-5 base model (released August 2025)
        verbose=True,
        log_to_file=True
    )
    
    try:
        # Register all systems
        print("\n[SETUP] Registering AGI subsystems...")
        orchestrator.register_system("sensorimotor", SystemType.PERCEPTION)
        orchestrator.register_system("emotion_system", SystemType.EMOTION)
        orchestrator.register_system("action_planner", SystemType.ACTION)
        orchestrator.register_system("consciousness_bridge", SystemType.CONSCIOUSNESS)
        orchestrator.register_system("world_model", SystemType.COGNITION)
        orchestrator.register_system("voice_system", SystemType.VOICE)
        orchestrator.register_system("video_interpreter", SystemType.VIDEO)
        orchestrator.register_system("reward_tuning", SystemType.LEARNING)
        
        print("\n[SETUP] All systems registered\n")
        await asyncio.sleep(1)
        
        # Simulate system interactions
        
        # 1. Perception system reports
        print("\n[SIMULATION] Sensorimotor perceives environment...")
        response1 = await orchestrator.send_message(
            system_id="sensorimotor",
            message_type="perception",
            content="I detect an enemy ahead at 15 meters. They appear hostile and are approaching.",
            metadata={"distance": 15, "threat_level": "high", "enemy_type": "bandit"}
        )
        await asyncio.sleep(2)
        
        # 2. Emotion system responds
        print("\n[SIMULATION] Emotion system processes threat...")
        response2 = await orchestrator.send_message(
            system_id="emotion_system",
            message_type="emotion",
            content="Threat detected. Experiencing heightened alertness and defensive readiness.",
            metadata={"valence": -0.3, "arousal": 0.8, "affect": "fear"}
        )
        await asyncio.sleep(2)
        
        # 3. Action planner decides
        print("\n[SIMULATION] Action planner formulates response...")
        response3 = await orchestrator.send_message(
            system_id="action_planner",
            message_type="decision",
            content="Planning defensive action. Should I engage in combat or retreat to safer position?",
            metadata={"health": 75, "stamina": 90, "weapons": ["sword", "bow"]}
        )
        await asyncio.sleep(2)
        
        # 4. Voice system announces
        print("\n[SIMULATION] Voice system vocalizes decision...")
        response4 = await orchestrator.send_message(
            system_id="voice_system",
            message_type="vocalization",
            content="I will engage the enemy with a defensive stance. They are within striking distance.",
            metadata={"priority": "HIGH", "voice": "NOVA"}
        )
        await asyncio.sleep(2)
        
        # 5. Video interpreter analyzes
        print("\n[SIMULATION] Video interpreter provides tactical analysis...")
        response5 = await orchestrator.send_message(
            system_id="video_interpreter",
            message_type="analysis",
            content="Visual analysis shows enemy has sword drawn. Terrain favors defensive positioning. Cover available to the right.",
            metadata={"mode": "TACTICAL", "frame_number": 1234}
        )
        await asyncio.sleep(2)
        
        # 6. Consciousness bridge integrates
        print("\n[SIMULATION] Consciousness bridge integrates all inputs...")
        response6 = await orchestrator.send_message(
            system_id="consciousness_bridge",
            message_type="integration",
            content="Integrating perception, emotion, and action planning. Current coherence: 0.85. All systems aligned for combat engagement.",
            metadata={"coherence": 0.85, "consciousness_level": 0.78}
        )
        await asyncio.sleep(2)
        
        # 7. Reward tuning learns
        print("\n[SIMULATION] Reward tuning records outcome...")
        response7 = await orchestrator.send_message(
            system_id="reward_tuning",
            message_type="learning",
            content="Combat successful. Defensive stance was effective. Updating heuristics for similar situations.",
            metadata={"reward": 0.9, "outcome": "success"}
        )
        await asyncio.sleep(2)
        
        # Print final statistics
        orchestrator.print_stats()
        
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    print("\n" + "="*100)
    print("GPT-5 ORCHESTRATOR TEST - ALL SYSTEMS COMMUNICATION".center(100))
    print("="*100)
    print("\nThis demonstrates all AGI subsystems communicating through GPT-5")
    print("with verbose console output showing the entire conversation flow.")
    print("\nUsing GPT-5 base model (released August 2025)")
    print("="*100)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()
