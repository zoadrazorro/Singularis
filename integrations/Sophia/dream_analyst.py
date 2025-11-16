"""
Dream Analyst - Jungian/Freudian dream analysis and interpretation.

Integrates with Fitbit for wake detection and Meta Glasses Messenger bot for voice dictation.
"""

from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re


class AnalysisFramework(Enum):
    JUNGIAN = "jungian"
    FREUDIAN = "freudian"
    COMBINED = "combined"


class DreamType(Enum):
    ARCHETYPAL = "archetypal"
    COMPENSATORY = "compensatory"
    PROSPECTIVE = "prospective"
    TRAUMATIC = "traumatic"
    LUCID = "lucid"
    RECURRING = "recurring"
    ORDINARY = "ordinary"


class JungianArchetype(Enum):
    SELF = "self"
    SHADOW = "shadow"
    ANIMA = "anima"
    ANIMUS = "animus"
    PERSONA = "persona"
    WISE_OLD_MAN = "wise_old_man"
    GREAT_MOTHER = "great_mother"
    TRICKSTER = "trickster"
    HERO = "hero"


class FreudianMechanism(Enum):
    WISH_FULFILLMENT = "wish_fulfillment"
    DISPLACEMENT = "displacement"
    CONDENSATION = "condensation"
    SYMBOLIZATION = "symbolization"
    REPRESSION = "repression"


class EmotionalTone(Enum):
    ANXIOUS = "anxious"
    FEARFUL = "fearful"
    JOYFUL = "joyful"
    SAD = "sad"
    ANGRY = "angry"
    CONFUSED = "confused"
    PEACEFUL = "peaceful"
    NEUTRAL = "neutral"


@dataclass
class DreamSymbol:
    symbol: str
    context: str
    jungian_meaning: Optional[str] = None
    freudian_meaning: Optional[str] = None
    archetype: Optional[JungianArchetype] = None


@dataclass
class DreamRecord:
    id: str
    date: datetime
    transcription: str
    narrative: str
    emotional_tone: EmotionalTone
    dream_type: DreamType
    symbols: List[DreamSymbol] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    sleep_quality: Optional[float] = None
    wake_time: Optional[datetime] = None


@dataclass
class DreamAnalysis:
    dream_id: str
    timestamp: datetime
    jungian_interpretation: str
    identified_archetypes: List[Tuple[JungianArchetype, str]]
    freudian_interpretation: str
    latent_content: str
    identified_mechanisms: List[Tuple[FreudianMechanism, str]]
    synthesis: str
    recommendations: List[str]
    confidence_score: float


class DreamAnalyst:
    """
    Dream Analyst with Jungian and Freudian interpretation.
    
    Integrates with:
    - Fitbit API for wake detection
    - Meta Glasses Messenger bot for voice dictation
    """
    
    def __init__(self):
        self.dreams: Dict[str, DreamRecord] = {}
        self.analyses: Dict[str, DreamAnalysis] = {}
        self.jungian_symbols = self._load_jungian_symbols()
        self.freudian_symbols = self._load_freudian_symbols()
    
    def _load_jungian_symbols(self) -> Dict:
        """Load Jungian symbol dictionary."""
        return {
            'water': {'jungian': 'The unconscious mind', 'archetype': JungianArchetype.SELF},
            'snake': {'jungian': 'Transformation, healing', 'archetype': JungianArchetype.SHADOW},
            'mountain': {'jungian': 'Spiritual ascent, challenge', 'archetype': JungianArchetype.SELF},
            'forest': {'jungian': 'The unconscious, unknown', 'archetype': JungianArchetype.SHADOW},
            'child': {'jungian': 'Innocence, potential', 'archetype': JungianArchetype.SELF},
            'old man': {'jungian': 'Wisdom, guidance', 'archetype': JungianArchetype.WISE_OLD_MAN},
            'mother': {'jungian': 'Nurturing, origin', 'archetype': JungianArchetype.GREAT_MOTHER},
            'fire': {'jungian': 'Transformation, passion', 'archetype': JungianArchetype.SELF},
            'bridge': {'jungian': 'Transition, connection', 'archetype': JungianArchetype.SELF},
            'mirror': {'jungian': 'Self-reflection', 'archetype': JungianArchetype.SELF}
        }
    
    def _load_freudian_symbols(self) -> Dict:
        """Load Freudian symbol dictionary."""
        return {
            'snake': {'freudian': 'Phallic symbol, sexual energy'},
            'water': {'freudian': 'Birth, womb, unconscious desires'},
            'house': {'freudian': 'The self, body'},
            'stairs': {'freudian': 'Sexual intercourse'},
            'flying': {'freudian': 'Sexual desire, freedom'},
            'falling': {'freudian': 'Loss of control, anxiety'},
            'teeth': {'freudian': 'Castration anxiety, aging'},
            'money': {'freudian': 'Feces, anal stage fixation'},
            'weapon': {'freudian': 'Phallic symbol, aggression'},
            'tunnel': {'freudian': 'Vaginal symbol, birth canal'}
        }
    
    def record_dream(self, transcription: str, wake_time: datetime, sleep_data: Optional[Dict] = None) -> DreamRecord:
        """Record dream from voice transcription."""
        dream_id = f"dream_{wake_time.strftime('%Y%m%d_%H%M%S')}"
        narrative = self._clean_narrative(transcription)
        emotional_tone = self._detect_emotional_tone(narrative)
        themes = self._extract_themes(narrative)
        symbols = self._extract_symbols(narrative)
        dream_type = self._classify_dream_type(narrative, symbols, themes)
        
        dream = DreamRecord(
            id=dream_id,
            date=wake_time.date(),
            transcription=transcription,
            narrative=narrative,
            emotional_tone=emotional_tone,
            dream_type=dream_type,
            symbols=symbols,
            themes=themes,
            wake_time=wake_time
        )
        
        if sleep_data:
            dream.sleep_quality = sleep_data.get('quality')
        
        self.dreams[dream_id] = dream
        return dream
    
    def _clean_narrative(self, transcription: str) -> str:
        """Clean voice transcription."""
        fillers = ['um', 'uh', 'like', 'you know']
        narrative = transcription.lower()
        for filler in fillers:
            narrative = re.sub(rf'\b{filler}\b', '', narrative)
        return re.sub(r'\s+', ' ', narrative).strip().capitalize()
    
    def _detect_emotional_tone(self, narrative: str) -> EmotionalTone:
        """Detect emotional tone."""
        emotion_keywords = {
            EmotionalTone.ANXIOUS: ['worried', 'nervous', 'anxious'],
            EmotionalTone.FEARFUL: ['scared', 'afraid', 'terrified'],
            EmotionalTone.JOYFUL: ['happy', 'joyful', 'excited'],
            EmotionalTone.SAD: ['sad', 'crying', 'grief'],
            EmotionalTone.PEACEFUL: ['calm', 'peaceful', 'serene']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(k in narrative.lower() for k in keywords):
                return emotion
        return EmotionalTone.NEUTRAL
    
    def _extract_themes(self, narrative: str) -> List[str]:
        """Extract themes."""
        theme_keywords = {
            'pursuit': ['chasing', 'running', 'escaping'],
            'transformation': ['changing', 'becoming', 'transforming'],
            'falling': ['falling', 'dropping'],
            'flying': ['flying', 'floating'],
            'death': ['dying', 'death', 'dead'],
            'loss': ['lost', 'losing', 'missing']
        }
        
        themes = []
        for theme, keywords in theme_keywords.items():
            if any(k in narrative.lower() for k in keywords):
                themes.append(theme)
        return themes
    
    def _extract_symbols(self, narrative: str) -> List[DreamSymbol]:
        """Extract symbols."""
        symbols = []
        for symbol_text, meanings in self.jungian_symbols.items():
            if symbol_text in narrative.lower():
                symbols.append(DreamSymbol(
                    symbol=symbol_text,
                    context=narrative[:100],
                    jungian_meaning=meanings.get('jungian'),
                    freudian_meaning=self.freudian_symbols.get(symbol_text, {}).get('freudian'),
                    archetype=meanings.get('archetype')
                ))
        return symbols
    
    def _classify_dream_type(self, narrative: str, symbols: List[DreamSymbol], themes: List[str]) -> DreamType:
        """Classify dream type."""
        if 'lucid' in narrative.lower() or 'knew it was a dream' in narrative.lower():
            return DreamType.LUCID
        if len([s for s in symbols if s.archetype]) >= 3:
            return DreamType.ARCHETYPAL
        if 'nightmare' in narrative.lower() or 'terrifying' in narrative.lower():
            return DreamType.TRAUMATIC
        return DreamType.ORDINARY
    
    def analyze_dream(self, dream_id: str) -> DreamAnalysis:
        """Analyze dream with both frameworks."""
        dream = self.dreams[dream_id]
        
        # Jungian analysis
        jungian_archetypes = [(s.archetype, s.jungian_meaning) for s in dream.symbols if s.archetype]
        jungian_interp = f"Jungian: {len(jungian_archetypes)} archetypes identified. "
        jungian_interp += f"Dream type: {dream.dream_type.value}. "
        
        # Freudian analysis
        freudian_mechanisms = []
        if dream.symbols:
            freudian_mechanisms.append((FreudianMechanism.SYMBOLIZATION, "Symbols represent unconscious desires"))
        if dream.emotional_tone in [EmotionalTone.ANXIOUS, EmotionalTone.FEARFUL]:
            freudian_mechanisms.append((FreudianMechanism.REPRESSION, "Anxiety indicates repressed content"))
        
        latent_content = "Latent: "
        for symbol in dream.symbols:
            if symbol.freudian_meaning:
                latent_content += f"{symbol.symbol} = {symbol.freudian_meaning}. "
        
        freudian_interp = f"Freudian: {len(freudian_mechanisms)} mechanisms. Manifest: {dream.narrative[:100]}..."
        
        # Synthesis
        synthesis = f"Both frameworks reveal: Personal unconscious (Freud) + Collective unconscious (Jung). "
        synthesis += f"Emotional tone: {dream.emotional_tone.value}. Themes: {', '.join(dream.themes)}."
        
        # Recommendations
        recs = []
        if dream.emotional_tone in [EmotionalTone.ANXIOUS, EmotionalTone.FEARFUL]:
            recs.append("Practice anxiety reduction techniques")
        if JungianArchetype.SHADOW in [a for a, _ in jungian_archetypes]:
            recs.append("Explore shadow work - integrate repressed aspects")
        if 'pursuit' in dream.themes:
            recs.append("Identify what you're avoiding in waking life")
        
        analysis = DreamAnalysis(
            dream_id=dream_id,
            timestamp=datetime.now(),
            jungian_interpretation=jungian_interp,
            identified_archetypes=jungian_archetypes,
            freudian_interpretation=freudian_interp,
            latent_content=latent_content,
            identified_mechanisms=freudian_mechanisms,
            synthesis=synthesis,
            recommendations=recs,
            confidence_score=0.7
        )
        
        self.analyses[dream_id] = analysis
        return analysis
    
    def get_dream_report(self, days: int = 30) -> Dict:
        """Generate dream report."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [d for d in self.dreams.values() if d.date > cutoff.date()]
        
        if not recent:
            return {'error': 'No dreams recorded'}
        
        # Analyze patterns
        all_themes = []
        all_symbols = []
        for dream in recent:
            all_themes.extend(dream.themes)
            all_symbols.extend([s.symbol for s in dream.symbols])
        
        from collections import Counter
        theme_counts = Counter(all_themes)
        symbol_counts = Counter(all_symbols)
        
        return {
            'total_dreams': len(recent),
            'most_common_themes': theme_counts.most_common(3),
            'most_common_symbols': symbol_counts.most_common(3),
            'emotional_distribution': Counter([d.emotional_tone.value for d in recent]),
            'dream_types': Counter([d.dream_type.value for d in recent]),
            'recommendations': self._generate_pattern_recommendations(theme_counts, symbol_counts)
        }
    
    def _generate_pattern_recommendations(self, themes: Counter, symbols: Counter) -> List[str]:
        """Generate recommendations based on patterns."""
        recs = []
        
        if themes.get('pursuit', 0) > 2:
            recs.append("Recurring pursuit themes - address avoidance patterns")
        if themes.get('falling', 0) > 2:
            recs.append("Recurring falling - examine areas where you feel loss of control")
        if symbols.get('water', 0) > 2:
            recs.append("Water symbol recurring - explore unconscious emotions")
        if symbols.get('snake', 0) > 2:
            recs.append("Snake symbol recurring - transformation or healing needed")
        
        return recs[:5]


if __name__ == "__main__":
    # Demo
    analyst = DreamAnalyst()
    
    # Simulate wake-up dream recording
    dream = analyst.record_dream(
        transcription="I was um like running through a dark forest and there was a snake chasing me I was so scared",
        wake_time=datetime.now(),
        sleep_data={'quality': 65}
    )
    
    print(f"Dream recorded: {dream.id}")
    print(f"Emotional tone: {dream.emotional_tone.value}")
    print(f"Themes: {dream.themes}")
    print(f"Symbols: {[s.symbol for s in dream.symbols]}")
    
    # Analyze
    analysis = analyst.analyze_dream(dream.id)
    print(f"\n{analysis.jungian_interpretation}")
    print(f"\n{analysis.freudian_interpretation}")
    print(f"\nSynthesis: {analysis.synthesis}")
    print(f"\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"  - {rec}")
