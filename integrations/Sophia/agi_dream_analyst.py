"""
AGI-Powered Dream Analyst - Deep psychological analysis using full Singularis AGI stack.

Integrates:
- GPT-5 Orchestrator for meta-cognitive analysis
- Gemini for vision and multimodal understanding
- Claude for analytical depth
- Consciousness Bridge for awareness integration
- Hierarchical Memory for pattern learning
- Voice System for spoken analysis
- Lumen Integration for philosophical grounding
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

# Import base dream analyst
from .dream_analyst import (
    DreamAnalyst, DreamRecord, DreamAnalysis, DreamSymbol,
    AnalysisFramework, DreamType, JungianArchetype, FreudianMechanism, EmotionalTone
)

# Import AGI components
from singularis.llm.gpt5_orchestrator import GPT5Orchestrator
from singularis.consciousness.voice_system import VoiceSystem, VoicePriority
from singularis.consciousness.consciousness_bridge import ConsciousnessBridge
from singularis.learning.hierarchical_memory import AdaptiveHierarchicalMemory
from singularis.consciousness.lumen_integration import LumenIntegration
from singularis.core.temporal_binding import TemporalCoherenceTracker


class AGIDreamAnalyst(DreamAnalyst):
    """
    AGI-powered dream analyst using full Singularis stack.
    
    Enhancements over base DreamAnalyst:
    - GPT-5 meta-cognitive interpretation
    - Deep contextual understanding
    - Adaptive learning of personal symbols
    - Consciousness state correlation
    - Spoken analysis via voice system
    - Philosophical grounding via Lumen
    - Temporal pattern recognition
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 gemini_api_key: Optional[str] = None,
                 enable_voice: bool = True,
                 user_context: Optional[Dict] = None):
        """
        Initialize AGI-powered dream analyst.
        
        Args:
            openai_api_key: OpenAI API key for GPT-5
            gemini_api_key: Optional Gemini API key for voice
            enable_voice: Enable spoken analysis
            user_context: User's life context for personalization
        """
        # Initialize base analyst
        super().__init__()
        
        # Initialize AGI components
        self.gpt5 = GPT5Orchestrator(api_key=openai_api_key, verbose=True)
        
        # Voice system for spoken analysis
        self.voice_system = None
        if enable_voice and gemini_api_key:
            self.voice_system = VoiceSystem(
                api_key=gemini_api_key,
                voice_type="NOVA",
                min_priority=VoicePriority.MEDIUM
            )
        
        # Consciousness bridge for awareness integration
        self.consciousness_bridge = ConsciousnessBridge()
        
        # Hierarchical memory for learning personal patterns
        self.hierarchical_memory = AdaptiveHierarchicalMemory(
            decay_rate=0.95,
            access_boost=1.02,
            forget_threshold=0.1
        )
        
        # Lumen integration for philosophical grounding
        self.lumen = LumenIntegration()
        
        # Temporal binding for dream sequence patterns
        self.temporal_tracker = TemporalCoherenceTracker(unclosed_timeout=30.0)
        
        # User context for personalization
        self.user_context = user_context or {}
        
        # Register with GPT-5 orchestrator
        self.gpt5.register_subsystem(
            subsystem_id="dream_analyst",
            subsystem_type="CONSCIOUSNESS",
            description="Jungian/Freudian dream analysis with AGI enhancement"
        )
        
        print("✨ AGI Dream Analyst initialized")
        print(f"   GPT-5: Connected")
        print(f"   Voice: {'Enabled' if self.voice_system else 'Disabled'}")
        print(f"   Consciousness Bridge: Active")
        print(f"   Adaptive Memory: Active")
    
    async def analyze_dream_agi(self, dream_id: str) -> DreamAnalysis:
        """
        Perform AGI-enhanced dream analysis.
        
        Uses full AGI stack for deep psychological interpretation.
        
        Args:
            dream_id: ID of dream to analyze
        
        Returns:
            Enhanced DreamAnalysis with AGI insights
        """
        if dream_id not in self.dreams:
            raise ValueError(f"Dream {dream_id} not found")
        
        dream = self.dreams[dream_id]
        
        print(f"\n🔮 AGI Dream Analysis: {dream_id}")
        print(f"   Dream type: {dream.dream_type.value}")
        print(f"   Emotional tone: {dream.emotional_tone.value}")
        
        # Step 1: Base analysis (Jungian + Freudian)
        print("\n   📊 Running base analysis...")
        base_analysis = super().analyze_dream(dream_id)
        
        # Step 2: GPT-5 meta-cognitive analysis
        print("   🧠 GPT-5 meta-cognitive analysis...")
        gpt5_insights = await self._gpt5_deep_analysis(dream, base_analysis)
        
        # Step 3: Consciousness correlation
        print("   🌟 Consciousness state correlation...")
        consciousness_insights = await self._consciousness_correlation(dream)
        
        # Step 4: Adaptive learning
        print("   📚 Learning personal patterns...")
        learned_patterns = await self._learn_personal_patterns(dream, base_analysis)
        
        # Step 5: Lumen philosophical grounding
        print("   ⚖️ Lumen philosophical integration...")
        lumen_insights = self._lumen_philosophical_analysis(dream, base_analysis)
        
        # Step 6: Temporal pattern recognition
        print("   ⏱️ Temporal pattern analysis...")
        temporal_patterns = await self._temporal_pattern_analysis(dream)
        
        # Synthesize all insights
        print("   ✨ Synthesizing AGI insights...")
        enhanced_analysis = self._synthesize_agi_analysis(
            base_analysis=base_analysis,
            gpt5_insights=gpt5_insights,
            consciousness_insights=consciousness_insights,
            learned_patterns=learned_patterns,
            lumen_insights=lumen_insights,
            temporal_patterns=temporal_patterns
        )
        
        # Store enhanced analysis
        self.analyses[dream_id] = enhanced_analysis
        
        # Speak analysis if voice enabled
        if self.voice_system:
            await self._speak_analysis(enhanced_analysis)
        
        print(f"   ✅ AGI analysis complete (confidence: {enhanced_analysis.confidence_score * 100:.0f}%)\n")
        
        return enhanced_analysis
    
    async def _gpt5_deep_analysis(self, dream: DreamRecord, base_analysis: DreamAnalysis) -> Dict:
        """Use GPT-5 for deep contextual interpretation."""
        
        # Build context for GPT-5
        context = {
            'dream_narrative': dream.narrative,
            'emotional_tone': dream.emotional_tone.value,
            'dream_type': dream.dream_type.value,
            'symbols': [s.symbol for s in dream.symbols],
            'themes': dream.themes,
            'base_jungian': base_analysis.jungian_interpretation,
            'base_freudian': base_analysis.freudian_interpretation,
            'user_context': self.user_context
        }
        
        # Ask GPT-5 for meta-cognitive analysis
        prompt = f"""Analyze this dream with deep psychological insight:

Dream: {dream.narrative}

Emotional Tone: {dream.emotional_tone.value}
Symbols: {', '.join(s.symbol for s in dream.symbols)}
Themes: {', '.join(dream.themes)}

Base Jungian Analysis: {base_analysis.jungian_interpretation[:200]}...
Base Freudian Analysis: {base_analysis.freudian_interpretation[:200]}...

User Context: {self.user_context.get('current_life_situation', 'Not provided')}

Provide:
1. Deep contextual interpretation considering user's life
2. Hidden psychological dynamics not captured by base analysis
3. Integration of conscious and unconscious elements
4. Specific actionable insights for personal growth
5. Connection to user's individuation journey

Be specific, insightful, and go beyond surface symbolism."""
        
        response = await self.gpt5.send_message(
            subsystem_id="dream_analyst",
            message_type="analysis_request",
            content=prompt,
            metadata=context
        )
        
        return {
            'deep_interpretation': response.get('guidance', ''),
            'hidden_dynamics': response.get('reasoning', ''),
            'confidence': response.get('confidence', 0.8)
        }
    
    async def _consciousness_correlation(self, dream: DreamRecord) -> Dict:
        """Correlate dream with consciousness state."""
        
        # Get current consciousness state
        consciousness_state = self.consciousness_bridge.get_current_state()
        
        # Analyze correlation
        insights = {
            'waking_consciousness_alignment': 0.0,
            'shadow_manifestation': False,
            'integration_opportunity': ''
        }
        
        # Check if dream compensates waking consciousness
        if dream.emotional_tone in [EmotionalTone.ANXIOUS, EmotionalTone.FEARFUL]:
            if consciousness_state.get('emotional_state') == 'calm':
                insights['waking_consciousness_alignment'] = 0.3
                insights['shadow_manifestation'] = True
                insights['integration_opportunity'] = "Dream reveals anxiety not acknowledged in waking life"
        
        # Check for individuation markers
        if len([a for a, _ in self.analyses.get(dream.id, base_analysis).identified_archetypes 
                if a == JungianArchetype.SELF]) > 0:
            insights['integration_opportunity'] = "Strong individuation process - integrating conscious and unconscious"
        
        return insights
    
    async def _learn_personal_patterns(self, dream: DreamRecord, analysis: DreamAnalysis) -> Dict:
        """Learn personal symbol meanings using adaptive memory."""
        
        learned = {
            'personal_symbols': {},
            'recurring_themes': [],
            'pattern_confidence': 0.0
        }
        
        # Store dream in episodic memory
        episode = {
            'dream_id': dream.id,
            'symbols': [s.symbol for s in dream.symbols],
            'themes': dream.themes,
            'emotional_tone': dream.emotional_tone.value,
            'interpretation': analysis.synthesis
        }
        
        self.hierarchical_memory.store_episode(
            episode_id=dream.id,
            content=episode,
            timestamp=datetime.now()
        )
        
        # Check if consolidation threshold reached
        if len(self.hierarchical_memory.episodic_memory) >= 10:
            # Consolidate to semantic memory
            patterns = self.hierarchical_memory.consolidate_to_semantic()
            
            if patterns:
                learned['pattern_confidence'] = 0.8
                
                # Extract personal symbol meanings
                for pattern in patterns:
                    if 'symbols' in pattern.get('pattern', {}):
                        for symbol in pattern['pattern']['symbols']:
                            if symbol not in learned['personal_symbols']:
                                learned['personal_symbols'][symbol] = {
                                    'frequency': pattern.get('frequency', 0),
                                    'contexts': pattern.get('contexts', []),
                                    'personal_meaning': f"Appears in {pattern.get('frequency', 0)} dreams"
                                }
        
        return learned
    
    def _lumen_philosophical_analysis(self, dream: DreamRecord, analysis: DreamAnalysis) -> Dict:
        """Analyze dream through Lumen philosophical framework."""
        
        # Map dream elements to Lumen dimensions
        lumen_mapping = {
            'onticum': 0.0,  # Being, existence
            'structurale': 0.0,  # Structure, form
            'participatum': 0.0  # Participation, connection
        }
        
        # Onticum: Dreams about existence, death, birth
        if any(theme in dream.themes for theme in ['death', 'birth', 'transformation']):
            lumen_mapping['onticum'] = 0.8
        
        # Structurale: Dreams about order, chaos, structure
        if dream.dream_type == DreamType.ARCHETYPAL:
            lumen_mapping['structurale'] = 0.7
        
        # Participatum: Dreams about connection, relationships
        if len(dream.characters) > 2:
            lumen_mapping['participatum'] = 0.6
        
        # Get Lumen balance
        balance_score = self.lumen.calculate_balance(lumen_mapping)
        
        return {
            'lumen_dimensions': lumen_mapping,
            'balance_score': balance_score,
            'philosophical_insight': self._generate_lumen_insight(lumen_mapping, balance_score)
        }
    
    def _generate_lumen_insight(self, dimensions: Dict, balance: float) -> str:
        """Generate philosophical insight from Lumen analysis."""
        
        dominant = max(dimensions, key=dimensions.get)
        
        insights = {
            'onticum': "Dream explores fundamental questions of Being and existence. You're grappling with existential themes.",
            'structurale': "Dream reveals concern with order, structure, and form. You're seeking patterns and meaning.",
            'participatum': "Dream emphasizes connection and participation. You're processing relational dynamics."
        }
        
        insight = insights.get(dominant, "Dream shows balanced philosophical expression.")
        
        if balance < 0.5:
            insight += " Consider integrating other dimensions of Being for wholeness."
        
        return insight
    
    async def _temporal_pattern_analysis(self, dream: DreamRecord) -> Dict:
        """Analyze temporal patterns across dream sequences."""
        
        patterns = {
            'sequence_coherence': 0.0,
            'recurring_narrative': False,
            'temporal_themes': []
        }
        
        # Get recent dreams
        recent_dreams = sorted(
            [d for d in self.dreams.values() if d.date >= (dream.date - timedelta(days=30))],
            key=lambda x: x.date
        )
        
        if len(recent_dreams) < 3:
            return patterns
        
        # Check for narrative continuity
        common_symbols = set(dream.symbols)
        for prev_dream in recent_dreams[-3:]:
            prev_symbols = set(s.symbol for s in prev_dream.symbols)
            if common_symbols & prev_symbols:
                patterns['sequence_coherence'] += 0.3
        
        patterns['sequence_coherence'] = min(patterns['sequence_coherence'], 1.0)
        
        # Check for recurring themes
        theme_counts = {}
        for d in recent_dreams:
            for theme in d.themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        recurring = [t for t, c in theme_counts.items() if c >= 3]
        if recurring:
            patterns['recurring_narrative'] = True
            patterns['temporal_themes'] = recurring
        
        return patterns
    
    def _synthesize_agi_analysis(self,
                                 base_analysis: DreamAnalysis,
                                 gpt5_insights: Dict,
                                 consciousness_insights: Dict,
                                 learned_patterns: Dict,
                                 lumen_insights: Dict,
                                 temporal_patterns: Dict) -> DreamAnalysis:
        """Synthesize all AGI insights into enhanced analysis."""
        
        # Enhanced Jungian interpretation
        enhanced_jungian = base_analysis.jungian_interpretation + "\n\n**AGI Enhancement:**\n"
        enhanced_jungian += gpt5_insights.get('deep_interpretation', '')[:300]
        
        # Enhanced Freudian interpretation  
        enhanced_freudian = base_analysis.freudian_interpretation + "\n\n**Hidden Dynamics:**\n"
        enhanced_freudian += gpt5_insights.get('hidden_dynamics', '')[:300]
        
        # Enhanced synthesis
        enhanced_synthesis = f"""**AGI-Enhanced Synthesis:**

{base_analysis.synthesis}

**Consciousness Correlation:**
{consciousness_insights.get('integration_opportunity', 'No specific correlation detected')}

**Learned Personal Patterns:**
{len(learned_patterns.get('personal_symbols', {}))} personal symbols identified
Pattern confidence: {learned_patterns.get('pattern_confidence', 0) * 100:.0f}%

**Philosophical Grounding (Lumen):**
{lumen_insights.get('philosophical_insight', '')}
Balance score: {lumen_insights.get('balance_score', 0):.2f}

**Temporal Patterns:**
Sequence coherence: {temporal_patterns.get('sequence_coherence', 0) * 100:.0f}%
Recurring narrative: {'Yes' if temporal_patterns.get('recurring_narrative') else 'No'}
"""
        
        # Enhanced recommendations
        enhanced_recs = base_analysis.recommendations.copy()
        
        if consciousness_insights.get('shadow_manifestation'):
            enhanced_recs.insert(0, "🌟 Shadow work: Acknowledge anxieties not expressed in waking life")
        
        if learned_patterns.get('personal_symbols'):
            enhanced_recs.append(f"📚 Personal symbols emerging: {', '.join(list(learned_patterns['personal_symbols'].keys())[:3])}")
        
        if lumen_insights.get('balance_score', 0) < 0.5:
            enhanced_recs.append("⚖️ Seek balance across Being dimensions (existence, structure, connection)")
        
        # Calculate enhanced confidence
        confidence_factors = [
            base_analysis.confidence_score,
            gpt5_insights.get('confidence', 0.8),
            learned_patterns.get('pattern_confidence', 0.5),
            temporal_patterns.get('sequence_coherence', 0.5)
        ]
        enhanced_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return DreamAnalysis(
            dream_id=base_analysis.dream_id,
            timestamp=datetime.now(),
            jungian_interpretation=enhanced_jungian,
            identified_archetypes=base_analysis.identified_archetypes,
            collective_unconscious_themes=base_analysis.collective_unconscious_themes,
            individuation_insights=base_analysis.individuation_insights,
            freudian_interpretation=enhanced_freudian,
            manifest_content=base_analysis.manifest_content,
            latent_content=base_analysis.latent_content,
            identified_mechanisms=base_analysis.identified_mechanisms,
            unconscious_wishes=base_analysis.unconscious_wishes,
            synthesis=enhanced_synthesis,
            recurring_patterns=base_analysis.recurring_patterns + temporal_patterns.get('temporal_themes', []),
            psychological_state=base_analysis.psychological_state,
            recommendations=enhanced_recs[:7],  # Top 7
            confidence_score=enhanced_confidence
        )
    
    async def _speak_analysis(self, analysis: DreamAnalysis):
        """Speak dream analysis using voice system."""
        
        if not self.voice_system:
            return
        
        # Create spoken summary
        spoken_text = f"""Your dream analysis is complete. 

The dream reveals {len(analysis.identified_archetypes)} archetypal elements and {len(analysis.identified_mechanisms)} psychological mechanisms.

Key insight: {analysis.synthesis[:200]}

Top recommendation: {analysis.recommendations[0] if analysis.recommendations else 'Continue dream journaling'}

Confidence level: {analysis.confidence_score * 100:.0f} percent.
"""
        
        await self.voice_system.speak(
            text=spoken_text,
            priority=VoicePriority.HIGH,
            context="dream_analysis"
        )


if __name__ == "__main__":
    # Demo
    print("=== AGI DREAM ANALYST DEMO ===\n")
    print("This requires valid API keys and full AGI stack")
    print("See demo_agi_dream_system.py for complete example")
