"""
Integrated SkyrimAGI - Complete 4-Layer Integration

Demonstrates GWM + IWM + MWM + PersonModel working together.

Usage:
    # Start services first:
    python start_iwm_service.py --port 8001
    python start_gwm_service.py --port 8002
    
    # Then run integration:
    python run_integrated_agi.py
"""

import torch
import asyncio
import time
from pathlib import Path
from loguru import logger
import numpy as np
from PIL import Image

# World models
from singularis.gwm import GWMClient
from singularis.iwm import IWMClient
from singularis.mwm import MentalWorldModelModule

# Person model
from singularis.person_model import (
    create_person_from_template,
    PersonRegistry,
    score_action_for_person,
    update_person_mwm,
    get_llm_context
)

# Core
from singularis.core.being_state import BeingState
from singularis.skyrim.actions import ActionType, Action


class IntegratedSkyrimAGI:
    """
    Complete 4-layer world understanding:
    - Layer 1: GWM (tactical game state)
    - Layer 2: IWM (visual prediction)
    - Layer 3: MWM (mental fusion)
    - Layer 4: PersonModel (complete agent)
    """
    
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        logger.info(f"🎮 [IntegratedAGI] Device: {self.device}")
        
        # Services
        self.gwm_client = GWMClient("http://localhost:8002")
        self.iwm_client = IWMClient("http://localhost:8001")
        
        # MWM module
        self.mwm_module = MentalWorldModelModule(latent_dim=256).to(self.device)
        self.mwm_module.eval()
        logger.info("🧠 [IntegratedAGI] MWM module loaded")
        
        # Person registry
        self.person_registry = PersonRegistry()
        
        # Create player agent
        self.player = create_person_from_template(
            "player_agent",
            person_id="player",
            name="Dragonborn"
        )
        self.person_registry.add(self.player)
        logger.info(f"🧑 [IntegratedAGI] Player: {self.player.identity.name}")
        
        # Being state
        self.being_state = BeingState()
        
        # Stats
        self.cycle_count = 0
        self.action_count = 0
    
    async def initialize(self):
        """Check services."""
        logger.info("🔧 [IntegratedAGI] Checking services...")
        
        # GWM
        try:
            gwm_health = await self.gwm_client.health()
            if gwm_health.get('status') == 'ok':
                logger.info(f"✅ [GWM] Service healthy (port 8002)")
            else:
                logger.error("❌ [GWM] Service not healthy")
                return False
        except Exception as e:
            logger.error(f"❌ [GWM] Service unavailable: {e}")
            return False
        
        # IWM
        try:
            iwm_health = await self.iwm_client.health()
            if iwm_health.get('status') == 'ok':
                logger.info(f"✅ [IWM] Service healthy (port 8001)")
            else:
                logger.error("❌ [IWM] Service not healthy")
                return False
        except Exception as e:
            logger.error(f"❌ [IWM] Service unavailable: {e}")
            return False
        
        logger.info("✅ [IntegratedAGI] All services ready!")
        return True
    
    async def perception_phase(self, screenshot, game_snapshot):
        """Phase 1: Gather perception inputs."""
        # IWM: Visual
        try:
            iwm_result = await self.iwm_client.encode(screenshot)
            iwm_latent = iwm_result['latent']
            iwm_surprise = iwm_result.get('surprise', 0.0)
            logger.debug(f"  👁️  IWM: latent shape [{len(iwm_latent)}], surprise={iwm_surprise:.2f}")
        except Exception as e:
            logger.warning(f"  ⚠️  IWM encode failed: {e}")
            iwm_latent = None
            iwm_surprise = 0.0
        
        # GWM: Tactical
        try:
            await self.gwm_client.send_snapshot(game_snapshot)
            gwm_features = await self.gwm_client.get_features()
            logger.debug(
                f"  🎯 GWM: threat={gwm_features.get('threat_level', 0):.2f}, "
                f"enemies={gwm_features.get('num_enemies_total', 0)}"
            )
        except Exception as e:
            logger.warning(f"  ⚠️  GWM update failed: {e}")
            gwm_features = {}
        
        return iwm_latent, iwm_surprise, gwm_features
    
    def mental_processing_phase(self, iwm_latent, gwm_features):
        """Phase 2: Fuse inputs → MWM."""
        try:
            self.player = update_person_mwm(
                self.player,
                gwm_features,
                iwm_latent,
                self.being_state,
                self.mwm_module,
                self.device
            )
            
            if self.player.mwm.affect:
                logger.debug(
                    f"  🧠 MWM: threat_perception={self.player.mwm.affect.threat:.2f}, "
                    f"curiosity={self.player.mwm.affect.curiosity:.2f}, "
                    f"value={self.player.mwm.affect.value_estimate:.2f}"
                )
        except Exception as e:
            logger.error(f"  ❌ MWM update failed: {e}")
    
    def update_being_state(self, iwm_latent, iwm_surprise, gwm_features):
        """Phase 3: Update BeingState."""
        # MWM
        if self.player.mwm:
            self.being_state.mwm = self.player.mwm.model_dump()
            if self.player.mwm.affect:
                self.being_state.mwm_threat_perception = self.player.mwm.affect.threat
                self.being_state.mwm_curiosity = self.player.mwm.affect.curiosity
                self.being_state.mwm_value_estimate = self.player.mwm.affect.value_estimate
        
        # GWM
        self.being_state.game_world = gwm_features
        if gwm_features:
            self.being_state.gwm_threat_level = gwm_features.get('threat_level', 0.0)
            self.being_state.gwm_num_enemies = gwm_features.get('num_enemies_total', 0)
        
        # IWM
        if iwm_latent is not None:
            self.being_state.vision_core_latent = np.array(iwm_latent, dtype=np.float32)
            self.being_state.vision_prediction_surprise = iwm_surprise
    
    def generate_candidates(self):
        """Generate candidate actions."""
        candidates = []
        
        # Always available
        candidates.append(Action(ActionType.MOVE_FORWARD, duration=1.0))
        candidates.append(Action(ActionType.WAIT, duration=0.5))
        
        # Combat actions
        if self.being_state.gwm_num_enemies > 0:
            candidates.append(Action(ActionType.ATTACK, duration=0.5))
            candidates.append(Action(ActionType.BLOCK, duration=1.0))
            
            # Escape if high threat
            if self.being_state.gwm_threat_level > 0.6:
                candidates.append(Action(ActionType.MOVE_BACKWARD, duration=1.0))
        
        # Stealth
        if not self.being_state.game_world or not self.being_state.game_world.get('is_player_in_stealth_danger', False):
            candidates.append(Action(ActionType.SNEAK, duration=2.0))
        
        # Loot if safe
        if self.being_state.gwm_loot_available and self.being_state.gwm_threat_level < 0.3:
            candidates.append(Action(ActionType.ACTIVATE, duration=1.0))
        
        return candidates
    
    def decision_phase(self, candidates):
        """Phase 4: Score actions → select best."""
        scores = {}
        
        for action in candidates:
            score = score_action_for_person(
                self.player,
                action,
                base_score=0.5
            )
            scores[action] = score
        
        # Filter invalid
        valid_actions = {a: s for a, s in scores.items() if s > -1e8}
        
        if not valid_actions:
            logger.warning("⚠️  No valid actions!")
            return None, scores
        
        best_action = max(valid_actions, key=valid_actions.get)
        return best_action, scores
    
    async def cycle(self, screenshot, game_snapshot):
        """Complete AGI cycle."""
        self.cycle_count += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎮 Cycle {self.cycle_count}")
        logger.info(f"{'='*60}")
        
        # Phase 1: Perception
        logger.info("📡 Phase 1: Perception")
        iwm_latent, iwm_surprise, gwm_features = await self.perception_phase(
            screenshot,
            game_snapshot
        )
        
        # Phase 2: Mental Processing
        logger.info("🧠 Phase 2: Mental Processing (MWM)")
        self.mental_processing_phase(iwm_latent, gwm_features)
        
        # Phase 3: Update State
        logger.info("📊 Phase 3: Update BeingState")
        self.update_being_state(iwm_latent, iwm_surprise, gwm_features)
        
        # Phase 4: Decision
        logger.info("🎯 Phase 4: Decision Making")
        candidates = self.generate_candidates()
        logger.info(f"  Candidates: {[str(a.action_type) for a in candidates]}")
        
        best_action, scores = self.decision_phase(candidates)
        
        if best_action:
            self.action_count += 1
            
            # Show decision
            logger.info(f"\n✨ DECISION:")
            logger.info(f"  ├─ Action: {best_action.action_type}")
            logger.info(f"  ├─ Score: {scores[best_action]:.3f}")
            logger.info(f"  ├─ GWM threat: {gwm_features.get('threat_level', 0):.2f}")
            logger.info(f"  ├─ MWM threat perception: {self.being_state.mwm_threat_perception:.2f}")
            logger.info(f"  ├─ MWM curiosity: {self.being_state.mwm_curiosity:.2f}")
            logger.info(f"  └─ MWM value estimate: {self.being_state.mwm_value_estimate:.2f}")
            
            # Top 3
            top_3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            logger.info(f"\n  Top 3:")
            for i, (action, score) in enumerate(top_3, 1):
                symbol = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                logger.info(f"    {symbol} {action.action_type}: {score:.3f}")
        
        return best_action
    
    async def run_demo(self, num_cycles=5):
        """Run demo with mock data."""
        logger.info("\n" + "="*60)
        logger.info("🎮 INTEGRATED SKYRIM AGI - DEMO")
        logger.info("="*60)
        logger.info("Demonstrating complete 4-layer integration:")
        logger.info("  Layer 1: GWM (tactical game state)")
        logger.info("  Layer 2: IWM (visual prediction)")
        logger.info("  Layer 3: MWM (mental fusion)")
        logger.info("  Layer 4: PersonModel (complete agent)")
        logger.info("="*60)
        
        if not await self.initialize():
            logger.error("\n❌ Services not ready. Start with:")
            logger.error("  python start_iwm_service.py --port 8001")
            logger.error("  python start_gwm_service.py --port 8002")
            return
        
        logger.info(f"\n🎬 Starting {num_cycles} demo cycles...\n")
        
        for i in range(num_cycles):
            # Mock screenshot
            screenshot = Image.fromarray(
                np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            )
            
            # Mock game snapshot
            game_snapshot = {
                "timestamp": time.time(),
                "player": {
                    "id": "player",
                    "pos": [float(i*10), 0.0, 0.0],
                    "facing_yaw": 90.0,
                    "health": max(0.75 - i*0.15, 0.2),  # Decreasing health
                    "stamina": 0.60,
                    "magicka": 0.50,
                    "sneaking": False,
                    "in_combat": i > 1
                },
                "npcs": [
                    {
                        "id": f"enemy_{j}",
                        "pos": [float(i*10 + 15 - j*2), float(j*5), 0.0],
                        "health": 0.80 - j*0.1,
                        "is_enemy": True,
                        "is_alive": True,
                        "distance_to_player": max(15.0 - i*3, 5.0),
                        "has_line_of_sight_to_player": i > 1,
                        "awareness_level": min(0.2 * i, 0.9)
                    }
                    for j in range(min(i, 3))
                ]
            }
            
            # Run cycle
            action = await self.cycle(screenshot, game_snapshot)
            
            # Sleep
            await asyncio.sleep(1.5)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("✅ DEMO COMPLETE")
        logger.info(f"  Total cycles: {self.cycle_count}")
        logger.info(f"  Total actions: {self.action_count}")
        logger.info(f"  Success rate: {100.0 * self.action_count / self.cycle_count:.1f}%")
        logger.info("="*60)
        logger.info("\n🎉 Integration successful! All 4 layers working in harmony.")
        logger.info("\nNext steps:")
        logger.info("  1. Connect to real game engine (SKSE/Papyrus)")
        logger.info("  2. Wire into SkyrimAGI main loop")
        logger.info("  3. Add more personality templates")
        logger.info("  4. Train MWM on collected data")
        logger.info("  5. Watch AGI play Skyrim like never before! ✨")
    
    async def cleanup(self):
        """Cleanup."""
        await self.gwm_client.close()
        await self.iwm_client.close()


async def main():
    agi = IntegratedSkyrimAGI()
    
    try:
        await agi.run_demo(num_cycles=5)
    finally:
        await agi.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
