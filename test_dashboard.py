"""
Test script to simulate real-time Skyrim AGI updates for dashboard testing.
This updates skyrim_agi_state.json every second with changing values.
"""

import json
import time
import random
from datetime import datetime

actions = ['explore', 'move_forward', 'attack', 'look_around', 'jump', 'sneak', 'cast_spell', 'use_item']
scenes = ['outdoor_wilderness', 'outdoor_town', 'indoor_dungeon', 'indoor_building']
sources = ['hybrid', 'moe', 'rl', 'heuristic']

def generate_state(cycle):
    """Generate a realistic AGI state for the given cycle."""
    current_time = time.time()
    
    # Randomly vary metrics
    coherence = 0.3 + (random.random() * 0.3)  # 0.3-0.6
    phi = coherence * 0.9  # Slightly lower than coherence
    health = max(50, 100 - (cycle * 2))  # Slowly decrease
    
    current_action = random.choice(actions)
    
    state = {
        "session_id": "skyrim_agi_test_session",
        "cycle": cycle,
        "uptime": cycle * 2,
        "last_update": datetime.now().isoformat(),
        
        "current_action": current_action,
        "last_action": random.choice(actions),
        "action_source": random.choice(sources),
        
        "recent_actions": [
            {
                "name": random.choice(actions),
                "timestamp": current_time - (i * 2),
                "cycle": cycle - i,
                "source": random.choice(sources)
            }
            for i in range(min(10, cycle))
        ],
        
        "perception": {
            "scene_type": random.choice(scenes),
            "objects": random.sample(['tree', 'rock', 'path', 'building', 'npc', 'chest'], k=3),
            "enemies_nearby": random.random() > 0.7,
            "npcs_nearby": random.random() > 0.5,
            "last_vision_time": random.random() * 2
        },
        
        "game_state": {
            "health": int(health),
            "magicka": random.randint(70, 100),
            "stamina": random.randint(60, 100),
            "in_combat": random.random() > 0.8,
            "in_menu": False,
            "location": "Skyrim Test Area"
        },
        
        "consciousness": {
            "coherence": round(coherence, 3),
            "phi": round(phi, 3),
            "nodes_active": random.randint(18, 22),
            "trend": random.choice(['increasing', 'stable', 'decreasing']),
            "history": [
                {
                    "timestamp": current_time - (i * 2),
                    "cycle": cycle - i,
                    "coherence": round(0.3 + (random.random() * 0.3), 3),
                    "phi": round(0.25 + (random.random() * 0.3), 3)
                }
                for i in range(min(20, cycle))
            ]
        },
        
        "llm_status": {
            "mode": "hybrid",
            "cloud_active": 2,
            "local_active": 0,
            "total_calls": cycle * 3,
            "last_call_time": random.random() * 1.0,
            "active_models": ["Gemini 2.0 Flash", "Claude Sonnet 4.5"]
        },
        
        "performance": {
            "fps": random.randint(50, 60),
            "planning_time": round(0.3 + (random.random() * 0.4), 3),
            "execution_time": round(0.1 + (random.random() * 0.2), 3),
            "vision_time": round(0.05 + (random.random() * 0.1), 3),
            "total_cycle_time": round(0.5 + (random.random() * 0.3), 3),
            "history": [
                {
                    "timestamp": current_time - (i * 2),
                    "cycle": cycle - i,
                    "planning_time": round(0.3 + (random.random() * 0.4), 3),
                    "execution_time": round(0.1 + (random.random() * 0.2), 3)
                }
                for i in range(min(20, cycle))
            ]
        },
        
        "diversity": {
            "score": round(random.random(), 2),
            "unique_actions": random.randint(4, 8),
            "total_actions": cycle,
            "variety_rate": round(random.random(), 2),
            "action_distribution": {
                action: random.randint(1, max(1, cycle // 4))
                for action in random.sample(actions, k=random.randint(3, 6))
            }
        },
        
        "stats": {
            "success_rate": round(0.85 + (random.random() * 0.1), 2),
            "rl_actions": random.randint(0, cycle // 3),
            "llm_actions": random.randint(cycle // 2, cycle),
            "heuristic_actions": random.randint(0, cycle // 4),
            "total_actions": cycle
        },
        
        "world_model": {
            "beliefs": {
                "location_safe": random.random() > 0.3,
                "npcs_friendly": random.random() > 0.4,
                "resources_available": random.random() > 0.5
            },
            "goals": random.sample([
                "Explore the wilderness",
                "Find NPCs",
                "Complete quest",
                "Gather resources",
                "Level up"
            ], k=random.randint(1, 3)),
            "strategy": random.choice(['explore', 'combat', 'stealth', 'social'])
        }
    }
    
    return state

def main():
    """Main test loop - updates state every second."""
    print("🧪 Skyrim AGI Dashboard Test Mode")
    print("=" * 60)
    print("This script simulates real-time AGI updates.")
    print("Dashboard should show changing metrics every second.")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    print()
    
    cycle = 1
    
    try:
        while True:
            # Generate and write state
            state = generate_state(cycle)
            
            with open('skyrim_agi_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"[Cycle {cycle:3d}] Action: {state['current_action']:15s} | "
                  f"Coherence: {state['consciousness']['coherence']:.3f} | "
                  f"Health: {state['game_state']['health']:3d}%")
            
            cycle += 1
            time.sleep(1)  # Update every second
            
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped")
        print(f"Total cycles simulated: {cycle - 1}")

if __name__ == "__main__":
    main()
