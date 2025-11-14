"""
Memory Engine v2 - Innovation 5

Temporal-rhythmic memory encoding that:
- Encodes events with rhythm signatures
- Uses interference patterns for recall
- Consolidates episodic → semantic memory
- Implements forgetting as harmonic decay

Key concepts:
- Memories are rhythm patterns, not static vectors
- Recall uses interference-based matching
- Consolidation creates semantic patterns from episodes
- Forgetting respects harmonic structure
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import math
import numpy as np


class MemoryType(Enum):
    """Types of memory"""
    EPISODIC = "episodic"      # Specific events with temporal context
    SEMANTIC = "semantic"      # Abstract patterns/knowledge
    PROCEDURAL = "procedural"  # Skills/habits (rhythm-based)


@dataclass
class RhythmSignature:
    """
    Rhythm signature encoding temporal pattern of an event.
    
    Instead of static vectors, memories are encoded as rhythm patterns:
    - Which tracks were active
    - Phase relationships between tracks
    - Interference patterns
    """
    track_phases: Dict[str, float]  # Phase of each track at encoding time
    track_periods: Dict[str, int]   # Period of each track
    interference_pattern: List[float]  # Interference strength over time
    dominant_frequency: float  # Primary rhythm
    
    def compute_similarity(self, other: 'RhythmSignature') -> float:
        """
        Compute similarity between two rhythm signatures.
        
        Uses phase correlation and frequency matching.
        """
        if not self.track_phases or not other.track_phases:
            return 0.0
        
        # 1. Track overlap
        common_tracks = set(self.track_phases.keys()) & set(other.track_phases.keys())
        if not common_tracks:
            return 0.0
        
        overlap_score = len(common_tracks) / max(len(self.track_phases), len(other.track_phases))
        
        # 2. Phase similarity (circular distance)
        phase_similarities = []
        for track in common_tracks:
            p1 = self.track_phases[track]
            p2 = other.track_phases[track]
            
            # Circular distance (phases wrap at 2π)
            diff = abs(p1 - p2)
            diff = min(diff, 2 * math.pi - diff)
            similarity = 1.0 - (diff / math.pi)
            phase_similarities.append(similarity)
        
        phase_score = sum(phase_similarities) / len(phase_similarities)
        
        # 3. Frequency similarity
        freq_diff = abs(self.dominant_frequency - other.dominant_frequency)
        freq_score = math.exp(-freq_diff / 10.0)
        
        # Weighted combination
        total_similarity = 0.4 * overlap_score + 0.4 * phase_score + 0.2 * freq_score
        
        return total_similarity
    
    def __repr__(self):
        return f"RhythmSignature({len(self.track_phases)} tracks, f={self.dominant_frequency:.2f})"


@dataclass
class MemoryTrace:
    """
    A single memory trace with temporal-rhythmic encoding.
    """
    memory_id: str
    memory_type: MemoryType
    
    # Content
    content: Dict  # Actual memory content (truth values, states, etc.)
    rhythm_signature: RhythmSignature
    
    # Temporal context
    timestamp: float
    context: str  # Context name when encoded
    
    # Strength and consolidation
    strength: float = 1.0
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    
    # Consolidation
    is_consolidated: bool = False
    consolidation_count: int = 0  # How many times reinforced
    
    # Associations
    associated_memories: Set[str] = field(default_factory=set)
    
    def decay(self, rate: float):
        """Apply forgetting decay"""
        self.strength *= (1.0 - rate)
    
    def reinforce(self, amount: float = 0.1):
        """Reinforce memory on access"""
        self.strength = min(1.0, self.strength + amount)
        self.access_count += 1
        self.last_access = time.time()
        self.consolidation_count += 1
    
    def should_consolidate(self, threshold: int = 3) -> bool:
        """Check if memory should be consolidated to semantic"""
        return (
            self.memory_type == MemoryType.EPISODIC and
            self.consolidation_count >= threshold and
            self.strength > 0.5
        )
    
    def __repr__(self):
        return f"Memory({self.memory_id}, {self.memory_type.value}, strength={self.strength:.2f})"


@dataclass
class SemanticPattern:
    """
    Semantic pattern extracted from multiple episodic memories.
    
    Represents abstract knowledge learned from experience.
    """
    pattern_id: str
    pattern_type: str  # e.g., "danger_response", "exploration_strategy"
    
    # Abstracted rhythm signature (average of episodes)
    rhythm_signature: RhythmSignature
    
    # Pattern content
    pattern: Dict  # Abstract pattern representation
    
    # Source episodes
    source_episodes: List[str]
    confidence: float = 0.5
    
    # Usage
    activation_count: int = 0
    last_activated: float = field(default_factory=time.time)
    
    def activate(self):
        """Activate pattern (increases confidence)"""
        self.activation_count += 1
        self.last_activated = time.time()
        self.confidence = min(1.0, self.confidence + 0.05)
    
    def __repr__(self):
        return f"Pattern({self.pattern_id}, {self.pattern_type}, conf={self.confidence:.2f})"


class MemoryEngineV2:
    """
    Temporal-rhythmic memory system.
    
    Key features:
    - Rhythm-based encoding (not static vectors)
    - Interference-based recall
    - Episodic → semantic consolidation
    - Harmonic forgetting
    """
    
    def __init__(
        self,
        episodic_capacity: int = 1000,
        semantic_capacity: int = 500,
        decay_rate: float = 0.001,
        consolidation_threshold: int = 3,
        verbose: bool = True
    ):
        self.episodic_capacity = episodic_capacity
        self.semantic_capacity = semantic_capacity
        self.decay_rate = decay_rate
        self.consolidation_threshold = consolidation_threshold
        self.verbose = verbose
        
        # Memory stores
        self.episodic_memories: Dict[str, MemoryTrace] = {}
        self.semantic_patterns: Dict[str, SemanticPattern] = {}
        
        # Statistics
        self.total_encodings = 0
        self.total_recalls = 0
        self.total_consolidations = 0
        self.total_forgotten = 0
        
        if self.verbose:
            print("[MEMORY ENGINE V2] Initialized")
            print(f"  Episodic capacity: {episodic_capacity}")
            print(f"  Semantic capacity: {semantic_capacity}")
            print(f"  Decay rate: {decay_rate}")
    
    def encode_episodic(
        self,
        memory_id: str,
        content: Dict,
        track_states: Dict[str, Tuple[float, int]],  # (phase, period)
        context: str,
        interference_pattern: Optional[List[float]] = None
    ) -> MemoryTrace:
        """
        Encode a new episodic memory with rhythm signature.
        
        Args:
            memory_id: Unique identifier
            content: Memory content (truth values, states, etc.)
            track_states: Current state of all tracks (phase, period)
            context: Context name
            interference_pattern: Optional pre-computed interference
        
        Returns:
            Created memory trace
        """
        # Create rhythm signature
        track_phases = {name: phase for name, (phase, _) in track_states.items()}
        track_periods = {name: period for name, (_, period) in track_states.items()}
        
        # Compute dominant frequency (average of active tracks)
        if track_periods:
            avg_period = sum(track_periods.values()) / len(track_periods)
            dominant_freq = 1.0 / avg_period if avg_period > 0 else 0.0
        else:
            dominant_freq = 0.0
        
        # Use provided interference or compute simple one
        if interference_pattern is None:
            interference_pattern = self._compute_interference(track_phases, track_periods)
        
        rhythm_sig = RhythmSignature(
            track_phases=track_phases,
            track_periods=track_periods,
            interference_pattern=interference_pattern,
            dominant_frequency=dominant_freq
        )
        
        # Create memory trace
        memory = MemoryTrace(
            memory_id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content=content,
            rhythm_signature=rhythm_sig,
            timestamp=time.time(),
            context=context
        )
        
        # Store memory
        self.episodic_memories[memory_id] = memory
        self.total_encodings += 1
        
        # Check capacity
        if len(self.episodic_memories) > self.episodic_capacity:
            self._forget_weakest_episodic()
        
        if self.verbose:
            print(f"[MEMORY ENGINE V2] Encoded: {memory_id}")
            print(f"  Context: {context}, Tracks: {len(track_phases)}")
        
        return memory
    
    def recall_by_rhythm(
        self,
        query_rhythm: RhythmSignature,
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[Tuple[MemoryTrace, float]]:
        """
        Recall memories by rhythm similarity (interference-based).
        
        Args:
            query_rhythm: Rhythm signature to match
            top_k: Number of memories to return
            threshold: Minimum similarity threshold
        
        Returns:
            List of (memory, similarity) tuples
        """
        self.total_recalls += 1
        
        # Compute similarity with all episodic memories
        similarities = []
        
        for memory_id, memory in self.episodic_memories.items():
            similarity = query_rhythm.compute_similarity(memory.rhythm_signature)
            
            if similarity >= threshold:
                similarities.append((memory, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Reinforce accessed memories
        for memory, sim in similarities[:top_k]:
            memory.reinforce(amount=0.05)
        
        if self.verbose and similarities:
            print(f"[MEMORY ENGINE V2] Recalled {len(similarities[:top_k])} memories")
            for mem, sim in similarities[:top_k]:
                print(f"  {mem.memory_id}: similarity={sim:.3f}")
        
        return similarities[:top_k]
    
    def recall_by_context(
        self,
        context: str,
        top_k: int = 5
    ) -> List[MemoryTrace]:
        """
        Recall memories from specific context.
        
        Args:
            context: Context name
            top_k: Number of memories to return
        
        Returns:
            List of memories
        """
        self.total_recalls += 1
        
        # Filter by context and sort by strength
        context_memories = [
            mem for mem in self.episodic_memories.values()
            if mem.context == context
        ]
        
        context_memories.sort(key=lambda m: m.strength, reverse=True)
        
        # Reinforce
        for memory in context_memories[:top_k]:
            memory.reinforce(amount=0.05)
        
        return context_memories[:top_k]
    
    def consolidate_episodic_to_semantic(
        self,
        pattern_type: str,
        episode_ids: Optional[List[str]] = None
    ) -> Optional[SemanticPattern]:
        """
        Consolidate multiple episodic memories into semantic pattern.
        
        Args:
            pattern_type: Type of pattern to extract
            episode_ids: Specific episodes to consolidate (or auto-select)
        
        Returns:
            Created semantic pattern or None
        """
        # Auto-select episodes if not provided
        if episode_ids is None:
            # Find episodes ready for consolidation
            candidates = [
                mem for mem in self.episodic_memories.values()
                if mem.should_consolidate(self.consolidation_threshold)
            ]
            
            if len(candidates) < 2:
                return None
            
            # Group by context
            context_groups = {}
            for mem in candidates:
                if mem.context not in context_groups:
                    context_groups[mem.context] = []
                context_groups[mem.context].append(mem)
            
            # Pick largest group
            if not context_groups:
                return None
            
            largest_group = max(context_groups.values(), key=len)
            episodes = largest_group[:5]  # Max 5 episodes per pattern
            episode_ids = [mem.memory_id for mem in episodes]
        else:
            episodes = [self.episodic_memories[eid] for eid in episode_ids if eid in self.episodic_memories]
        
        if len(episodes) < 2:
            return None
        
        # Average rhythm signatures
        avg_phases = {}
        avg_periods = {}
        all_tracks = set()
        
        for ep in episodes:
            all_tracks.update(ep.rhythm_signature.track_phases.keys())
        
        for track in all_tracks:
            phases = [ep.rhythm_signature.track_phases.get(track, 0.0) for ep in episodes]
            periods = [ep.rhythm_signature.track_periods.get(track, 100) for ep in episodes]
            
            avg_phases[track] = sum(phases) / len(phases)
            avg_periods[track] = int(sum(periods) / len(periods))
        
        # Average dominant frequency
        avg_freq = sum(ep.rhythm_signature.dominant_frequency for ep in episodes) / len(episodes)
        
        # Create abstracted rhythm signature
        abstract_rhythm = RhythmSignature(
            track_phases=avg_phases,
            track_periods=avg_periods,
            interference_pattern=[],
            dominant_frequency=avg_freq
        )
        
        # Extract pattern (simplified - just average content)
        pattern_content = {}
        
        # Create semantic pattern
        pattern_id = f"pattern_{self.total_consolidations}"
        pattern = SemanticPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            rhythm_signature=abstract_rhythm,
            pattern=pattern_content,
            source_episodes=episode_ids,
            confidence=0.6
        )
        
        self.semantic_patterns[pattern_id] = pattern
        self.total_consolidations += 1
        
        # Mark episodes as consolidated
        for ep in episodes:
            ep.is_consolidated = True
        
        if self.verbose:
            print(f"[MEMORY ENGINE V2] Consolidated pattern: {pattern_id}")
            print(f"  Type: {pattern_type}, Episodes: {len(episode_ids)}")
        
        return pattern
    
    def retrieve_semantic_pattern(
        self,
        pattern_type: str,
        query_rhythm: Optional[RhythmSignature] = None
    ) -> Optional[SemanticPattern]:
        """
        Retrieve semantic pattern by type or rhythm.
        
        Args:
            pattern_type: Type of pattern
            query_rhythm: Optional rhythm to match
        
        Returns:
            Best matching pattern or None
        """
        candidates = [
            p for p in self.semantic_patterns.values()
            if p.pattern_type == pattern_type
        ]
        
        if not candidates:
            return None
        
        if query_rhythm is not None:
            # Find best rhythm match
            best_pattern = None
            best_similarity = 0.0
            
            for pattern in candidates:
                similarity = query_rhythm.compute_similarity(pattern.rhythm_signature)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_pattern = pattern
            
            if best_pattern:
                best_pattern.activate()
                return best_pattern
        else:
            # Return most confident
            best_pattern = max(candidates, key=lambda p: p.confidence)
            best_pattern.activate()
            return best_pattern
        
        return None
    
    def apply_forgetting(self):
        """
        Apply harmonic forgetting to all memories.
        
        Memories decay over time, respecting harmonic structure.
        """
        forgotten_count = 0
        
        # Decay episodic memories
        to_remove = []
        for memory_id, memory in self.episodic_memories.items():
            memory.decay(self.decay_rate)
            
            if memory.strength < 0.1:
                to_remove.append(memory_id)
                forgotten_count += 1
        
        for memory_id in to_remove:
            del self.episodic_memories[memory_id]
        
        self.total_forgotten += forgotten_count
        
        if self.verbose and forgotten_count > 0:
            print(f"[MEMORY ENGINE V2] Forgot {forgotten_count} weak memories")
    
    def _forget_weakest_episodic(self):
        """Remove weakest episodic memory when at capacity"""
        if not self.episodic_memories:
            return
        
        # Find weakest non-consolidated memory
        weakest = min(
            (m for m in self.episodic_memories.values() if not m.is_consolidated),
            key=lambda m: m.strength,
            default=None
        )
        
        if weakest:
            del self.episodic_memories[weakest.memory_id]
            self.total_forgotten += 1
    
    def _compute_interference(
        self,
        track_phases: Dict[str, float],
        track_periods: Dict[str, int],
        window: int = 10
    ) -> List[float]:
        """
        Compute interference pattern over time window.
        
        Returns list of interference strengths.
        """
        if not track_phases:
            return []
        
        interference = []
        
        for t in range(window):
            # Compute phase alignment at time t
            total_alignment = 0.0
            
            for track, base_phase in track_phases.items():
                period = track_periods[track]
                current_phase = (base_phase + (2 * math.pi * t / period)) % (2 * math.pi)
                
                # Alignment is cos(phase) - peaks at 0, 2π
                alignment = math.cos(current_phase)
                total_alignment += alignment
            
            # Normalize
            avg_alignment = total_alignment / len(track_phases)
            interference.append(avg_alignment)
        
        return interference
    
    def get_statistics(self) -> Dict:
        """Get memory system statistics"""
        return {
            'episodic_count': len(self.episodic_memories),
            'semantic_count': len(self.semantic_patterns),
            'total_encodings': self.total_encodings,
            'total_recalls': self.total_recalls,
            'total_consolidations': self.total_consolidations,
            'total_forgotten': self.total_forgotten,
            'avg_episodic_strength': sum(m.strength for m in self.episodic_memories.values()) / max(1, len(self.episodic_memories)),
            'avg_semantic_confidence': sum(p.confidence for p in self.semantic_patterns.values()) / max(1, len(self.semantic_patterns))
        }
    
    def __repr__(self):
        return f"MemoryEngineV2({len(self.episodic_memories)} episodic, {len(self.semantic_patterns)} semantic)"
