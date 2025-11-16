"""
AGI Dream System - Complete integration with Singularis AGI stack.

Full-featured dream analysis using:
- GPT-5 Orchestrator
- Consciousness Bridge
- Adaptive Memory
- Voice System
- Lumen Integration
- Temporal Binding
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
from datetime import datetime
from typing import Optional, Dict

from .agi_dream_analyst import AGIDreamAnalyst
from .fitbit_integration import FitbitIntegration, SleepData
from .messenger_dream_bot import MessengerDreamBot


class AGIDreamSystem:
    """
    Complete AGI-powered dream analysis system.
    
    Enhancements over basic system:
    - GPT-5 meta-cognitive dream interpretation
    - Adaptive learning of personal symbols
    - Consciousness state correlation
    - Spoken analysis via voice system
    - Philosophical grounding via Lumen
    - Temporal pattern recognition
    - Cross-dream narrative synthesis
    """
    
    def __init__(self,
                 openai_api_key: str,
                 gemini_api_key: Optional[str] = None,
                 fitbit_token: Optional[str] = None,
                 fitbit_user_id: Optional[str] = None,
                 messenger_chat_name: str = "Dream Journal",
                 enable_voice: bool = True,
                 user_context: Optional[Dict] = None):
        """
        Initialize AGI dream system.
        
        Args:
            openai_api_key: OpenAI API key for GPT-5
            gemini_api_key: Gemini API key for voice
            fitbit_token: Fitbit OAuth token
            fitbit_user_id: Fitbit user ID
            messenger_chat_name: Messenger chat name
            enable_voice: Enable spoken analysis
            user_context: User's life context for personalization
        """
        print("🌟 Initializing AGI Dream System...")
        
        # Initialize AGI dream analyst
        self.analyst = AGIDreamAnalyst(
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            enable_voice=enable_voice,
            user_context=user_context
        )
        
        # Initialize Fitbit if credentials provided
        self.fitbit = None
        if fitbit_token and fitbit_user_id:
            self.fitbit = FitbitIntegration(fitbit_token, fitbit_user_id)
            self.fitbit.set_wake_callback(self._on_wake_detected)
            print("   Fitbit: Connected")
        else:
            print("   Fitbit: Not configured (manual mode)")
        
        # Initialize Messenger bot
        self.messenger = MessengerDreamBot(messenger_chat_name)
        self.messenger.set_dream_callback(self._on_dream_received)
        print(f"   Messenger: {messenger_chat_name}")
        
        # State
        self.running = False
        self.current_wake_time: Optional[datetime] = None
        self.current_sleep_data: Optional[SleepData] = None
        
        print("✨ AGI Dream System ready!\n")
    
    async def start(self):
        """Start the AGI dream system."""
        self.running = True
        print("🌙 AGI Dream System starting...")
        print("   Using full Singularis AGI stack")
        print("   GPT-5 meta-cognitive analysis enabled")
        print("   Adaptive learning active")
        print("   Consciousness correlation active")
        
        if self.analyst.voice_system:
            print("   Voice system enabled")
        
        print()
        
        if self.fitbit:
            # Start Fitbit monitoring
            await self.fitbit.start_monitoring(check_interval_minutes=5)
        else:
            print("⚠️ Fitbit not configured - use manual dream recording")
            print("   Call: await system.record_dream_manually(transcription)")
    
    def stop(self):
        """Stop the system."""
        self.running = False
        if self.fitbit:
            self.fitbit.stop_monitoring()
        print("\n🛑 AGI Dream System stopped")
    
    async def _on_wake_detected(self, wake_time: datetime, sleep_data: SleepData):
        """Callback when Fitbit detects wake-up."""
        print(f"\n☀️ WAKE-UP DETECTED: {wake_time.strftime('%H:%M')}")
        print(f"   Sleep quality: {sleep_data.sleep_quality}/100")
        print(f"   REM sleep: {sleep_data.minutes_rem} minutes")
        print(f"   Deep sleep: {sleep_data.minutes_deep} minutes")
        
        # Store for later
        self.current_wake_time = wake_time
        self.current_sleep_data = sleep_data
        
        # Send prompt via Messenger
        sleep_dict = {
            'quality': sleep_data.sleep_quality,
            'rem_minutes': sleep_data.minutes_rem,
            'duration_hours': sleep_data.duration_minutes / 60
        }
        
        await self.messenger.send_wake_prompt(wake_time, sleep_dict)
        
        print("   ✅ Dream prompt sent to Messenger")
        print("   ⏳ Waiting for dream dictation...")
    
    async def _on_dream_received(self, transcription: str, timestamp: datetime):
        """Callback when user dictates dream."""
        print(f"\n📝 DREAM RECEIVED: {len(transcription)} characters")
        print(f"   Timestamp: {timestamp.strftime('%H:%M:%S')}")
        
        # Record dream
        sleep_dict = None
        if self.current_sleep_data:
            sleep_dict = {
                'quality': self.current_sleep_data.sleep_quality,
                'duration_hours': self.current_sleep_data.duration_minutes / 60,
                'rem_minutes': self.current_sleep_data.minutes_rem
            }
        
        dream = self.analyst.record_dream(
            transcription=transcription,
            wake_time=self.current_wake_time or timestamp,
            sleep_data=sleep_dict
        )
        
        print(f"   ✅ Dream recorded: {dream.id}")
        print(f"   Emotional tone: {dream.emotional_tone.value}")
        print(f"   Dream type: {dream.dream_type.value}")
        print(f"   Symbols: {len(dream.symbols)}")
        print(f"   Themes: {', '.join(dream.themes) if dream.themes else 'None'}")
        
        # AGI-enhanced analysis
        print(f"\n🧠 Starting AGI-enhanced analysis...")
        print("   This uses the full Singularis AGI stack:")
        print("   • GPT-5 meta-cognitive interpretation")
        print("   • Consciousness state correlation")
        print("   • Adaptive pattern learning")
        print("   • Lumen philosophical grounding")
        print("   • Temporal sequence analysis")
        
        analysis = await self.analyst.analyze_dream_agi(dream.id)
        
        print(f"\n✅ AGI Analysis Complete!")
        print(f"   Confidence: {analysis.confidence_score * 100:.0f}%")
        print(f"   Archetypes: {len(analysis.identified_archetypes)}")
        print(f"   Recommendations: {len(analysis.recommendations)}")
        
        # Send analysis to user
        analysis_dict = {
            'jungian_interpretation': analysis.jungian_interpretation,
            'identified_archetypes': analysis.identified_archetypes,
            'freudian_interpretation': analysis.freudian_interpretation,
            'latent_content': analysis.latent_content,
            'identified_mechanisms': analysis.identified_mechanisms,
            'synthesis': analysis.synthesis,
            'recommendations': analysis.recommendations,
            'confidence_score': analysis.confidence_score
        }
        
        await self.messenger.send_analysis(analysis_dict)
        
        print("   ✅ Analysis sent to user via Messenger")
        
        if self.analyst.voice_system:
            print("   🔊 Spoken analysis delivered")
        
        print("\n✨ AGI dream processing complete!\n")
        
        # Reset state
        self.current_wake_time = None
        self.current_sleep_data = None
    
    async def record_dream_manually(self, transcription: str, wake_time: Optional[datetime] = None):
        """
        Manually record and analyze a dream (without Fitbit).
        
        Args:
            transcription: Dream transcription
            wake_time: Optional wake time (defaults to now)
        """
        timestamp = wake_time or datetime.now()
        await self._on_dream_received(transcription, timestamp)
    
    def get_agi_statistics(self, days: int = 30) -> Dict:
        """Get AGI-enhanced statistics."""
        base_stats = self.analyst.get_dream_report(days)
        
        # Add AGI-specific stats
        agi_stats = {
            'base_stats': base_stats,
            'agi_enhancements': {
                'gpt5_analyses': len(self.analyst.analyses),
                'learned_patterns': len(self.analyst.hierarchical_memory.semantic_memory),
                'personal_symbols': len(self.analyst.personal_symbol_associations),
                'consciousness_correlations': 'Active',
                'lumen_balance': 'Tracked',
                'temporal_coherence': 'Monitored'
            }
        }
        
        if self.fitbit:
            agi_stats['sleep_stats'] = self.fitbit.get_sleep_stats(days)
        
        return agi_stats
    
    async def get_agi_insights(self) -> str:
        """Get AGI-powered insights about dream patterns."""
        
        if len(self.analyst.dreams) < 3:
            return "Not enough dreams for AGI insights (need at least 3)"
        
        # Build context
        recent_dreams = list(self.analyst.dreams.values())[-5:]
        context = {
            'total_dreams': len(self.analyst.dreams),
            'recent_themes': [t for d in recent_dreams for t in d.themes],
            'recent_symbols': [s.symbol for d in recent_dreams for s in d.symbols],
            'emotional_progression': [d.emotional_tone.value for d in recent_dreams]
        }
        
        # Ask GPT-5 for meta-insights
        prompt = f"""Analyze these dream patterns and provide meta-insights:

Total dreams recorded: {context['total_dreams']}
Recent themes: {', '.join(set(context['recent_themes']))}
Recent symbols: {', '.join(set(context['recent_symbols']))}
Emotional progression: {' → '.join(context['emotional_progression'])}

Provide:
1. Overall psychological trajectory
2. Emerging patterns across dreams
3. Individuation progress indicators
4. Recommendations for dream work
5. Areas needing conscious attention

Be specific and actionable."""
        
        response = await self.analyst.gpt5.send_message(
            subsystem_id="dream_analyst",
            message_type="meta_insights_request",
            content=prompt,
            metadata=context
        )
        
        return response.get('guidance', 'No insights available')


async def main():
    """Demo AGI dream system."""
    print("=" * 80)
    print("  AGI DREAM SYSTEM - Full Singularis Integration")
    print("=" * 80)
    
    print("\n🔧 REQUIREMENTS:")
    print("   • OpenAI API key (GPT-5)")
    print("   • Gemini API key (Voice)")
    print("   • Fitbit OAuth token (optional)")
    print("   • meta-glasses-api running")
    
    print("\n🌟 AGI ENHANCEMENTS:")
    print("   ✓ GPT-5 meta-cognitive analysis")
    print("   ✓ Consciousness state correlation")
    print("   ✓ Adaptive pattern learning")
    print("   ✓ Spoken analysis delivery")
    print("   ✓ Lumen philosophical grounding")
    print("   ✓ Temporal sequence tracking")
    
    print("\n💡 USAGE:")
    print("   system = AGIDreamSystem(")
    print("       openai_api_key='your_key',")
    print("       gemini_api_key='your_key',")
    print("       fitbit_token='your_token',")
    print("       user_context={'current_life_situation': 'Career transition'}")
    print("   )")
    print("   await system.start()")
    
    print("\n" + "=" * 80)
    print("  Configure API keys and run to start AGI dream analysis!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
