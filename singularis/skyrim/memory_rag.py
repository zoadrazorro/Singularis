"""
RAG (Retrieval-Augmented Generation) for Perceptual and Cognitive Memories

Enhances planning and decision-making by retrieving relevant past experiences:
1. Stores perceptual memories (what was seen/experienced)
2. Stores cognitive memories (decisions made, outcomes)
3. Retrieves similar experiences using embedding similarity
4. Augments LLM context with relevant memories

Philosophical grounding:
- Memory enables learning from experience
- Similar contexts suggest similar actions
- Past successes guide future decisions
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from collections import deque
import time


@dataclass
class PerceptualMemory:
    """A memory of what was perceived."""
    visual_embedding: np.ndarray
    scene_type: str
    location: str
    timestamp: float
    context: Dict[str, Any]


@dataclass
class CognitiveMemory:
    """A memory of a decision and its outcome."""
    situation: Dict[str, Any]
    action_taken: str
    outcome: Dict[str, Any]
    success: bool
    reasoning: str
    timestamp: float


class MemoryRAG:
    """
    Retrieval-Augmented Generation for game memories.
    
    Stores and retrieves relevant memories to inform decision-making.
    """
    
    def __init__(
        self,
        perceptual_capacity: int = 1000,
        cognitive_capacity: int = 500
    ):
        """
        Initialize memory RAG system.
        
        Args:
            perceptual_capacity: Max perceptual memories
            cognitive_capacity: Max cognitive memories
        """
        self.perceptual_capacity = perceptual_capacity
        self.cognitive_capacity = cognitive_capacity
        
        # Memory stores
        self.perceptual_memories: deque = deque(maxlen=perceptual_capacity)
        self.cognitive_memories: deque = deque(maxlen=cognitive_capacity)
        
        # Indexing for fast retrieval
        self.perceptual_embeddings: List[np.ndarray] = []
        self.cognitive_embeddings: List[np.ndarray] = []
        
        print("[RAG] Memory RAG system initialized")
    
    def store_perceptual_memory(
        self,
        visual_embedding: np.ndarray,
        scene_type: str,
        location: str,
        context: Dict[str, Any]
    ):
        """
        Store a perceptual memory.
        
        Args:
            visual_embedding: CLIP embedding of what was seen
            scene_type: Type of scene
            location: Location name
            context: Additional context
        """
        memory = PerceptualMemory(
            visual_embedding=visual_embedding,
            scene_type=scene_type,
            location=location,
            timestamp=time.time(),
            context=context
        )
        
        self.perceptual_memories.append(memory)
        self.perceptual_embeddings.append(visual_embedding)
        
        # Trim embeddings if needed
        if len(self.perceptual_embeddings) > self.perceptual_capacity:
            self.perceptual_embeddings.pop(0)
    
    def store_cognitive_memory(
        self,
        situation: Dict[str, Any],
        action_taken: str,
        outcome: Dict[str, Any],
        success: bool,
        reasoning: str = ""
    ):
        """
        Store a cognitive memory (decision + outcome).
        
        Args:
            situation: Situation that prompted decision
            action_taken: Action that was taken
            outcome: What happened
            success: Whether it was successful
            reasoning: Why this action was chosen
        """
        memory = CognitiveMemory(
            situation=situation,
            action_taken=action_taken,
            outcome=outcome,
            success=success,
            reasoning=reasoning,
            timestamp=time.time()
        )
        
        self.cognitive_memories.append(memory)
        
        # Create embedding from situation
        situation_embedding = self._create_situation_embedding(situation)
        self.cognitive_embeddings.append(situation_embedding)
        
        # Trim embeddings if needed
        if len(self.cognitive_embeddings) > self.cognitive_capacity:
            self.cognitive_embeddings.pop(0)
    
    def retrieve_similar_perceptions(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[PerceptualMemory, float]]:
        """
        Retrieve perceptual memories similar to query.
        
        Args:
            query_embedding: Visual embedding to match
            top_k: Number of memories to retrieve
            similarity_threshold: Minimum similarity
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        if not self.perceptual_embeddings:
            return []
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(self.perceptual_embeddings):
            similarity = self._cosine_similarity(query_embedding, emb)
            if similarity >= similarity_threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k
        results = []
        for idx, sim in similarities[:top_k]:
            if idx < len(self.perceptual_memories):
                results.append((self.perceptual_memories[idx], sim))
        
        return results
    
    def retrieve_similar_decisions(
        self,
        current_situation: Dict[str, Any],
        top_k: int = 3,
        only_successful: bool = False
    ) -> List[Tuple[CognitiveMemory, float]]:
        """
        Retrieve cognitive memories of similar situations.
        
        Args:
            current_situation: Current situation
            top_k: Number of memories to retrieve
            only_successful: Only retrieve successful decisions
            
        Returns:
            List of (memory, similarity_score) tuples
        """
        if not self.cognitive_embeddings:
            return []
        
        # Create embedding for current situation
        query_embedding = self._create_situation_embedding(current_situation)
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(self.cognitive_embeddings):
            similarity = self._cosine_similarity(query_embedding, emb)
            
            # Filter by success if requested
            if only_successful:
                if i < len(self.cognitive_memories):
                    if not self.cognitive_memories[i].success:
                        continue
            
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k
        results = []
        for idx, sim in similarities[:top_k]:
            if idx < len(self.cognitive_memories):
                results.append((self.cognitive_memories[idx], sim))
        
        return results
    
    def augment_context_with_memories(
        self,
        current_visual: np.ndarray,
        current_situation: Dict[str, Any],
        max_memories: int = 3
    ) -> str:
        """
        Create context string augmented with relevant memories.
        
        Args:
            current_visual: Current visual embedding
            current_situation: Current situation dict
            max_memories: Max memories to include
            
        Returns:
            Formatted memory context string
        """
        context_parts = []
        
        # Retrieve similar perceptions
        similar_perceptions = self.retrieve_similar_perceptions(
            current_visual,
            top_k=max_memories
        )
        
        if similar_perceptions:
            context_parts.append("\nRELEVANT PAST PERCEPTIONS:")
            for i, (memory, similarity) in enumerate(similar_perceptions, 1):
                context_parts.append(
                    f"{i}. Similar scene ({similarity:.2f} match): "
                    f"{memory.scene_type} at {memory.location}"
                )
        
        # Retrieve similar decisions
        similar_decisions = self.retrieve_similar_decisions(
            current_situation,
            top_k=max_memories,
            only_successful=True
        )
        
        if similar_decisions:
            context_parts.append("\nRELEVANT PAST DECISIONS (successful):")
            for i, (memory, similarity) in enumerate(similar_decisions, 1):
                context_parts.append(
                    f"{i}. Similar situation ({similarity:.2f} match): "
                    f"Action '{memory.action_taken}' → "
                    f"{self._summarize_outcome(memory.outcome)}"
                )
                if memory.reasoning:
                    context_parts.append(f"   Reasoning: {memory.reasoning}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _create_situation_embedding(self, situation: Dict[str, Any]) -> np.ndarray:
        """
        Create embedding from situation dict.
        
        Args:
            situation: Situation dictionary
            
        Returns:
            Embedding vector
        """
        # Simple hash-based embedding
        # In production, would use learned embeddings
        features = []
        
        # Extract key features
        features.append(hash(situation.get('scene', '')) % 1000 / 1000.0)
        features.append(situation.get('health', 100) / 100.0)
        features.append(float(situation.get('in_combat', False)))
        features.append(hash(situation.get('location', '')) % 1000 / 1000.0)
        
        # Pad to fixed size
        while len(features) < 16:
            features.append(0.0)
        
        return np.array(features[:16])
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return max(0.0, min(1.0, dot_product / (norm_a * norm_b)))
    
    def _summarize_outcome(self, outcome: Dict[str, Any]) -> str:
        """
        Summarize outcome for display.
        
        Args:
            outcome: Outcome dictionary
            
        Returns:
            Summary string
        """
        parts = []
        
        if 'health' in outcome:
            parts.append(f"health={outcome['health']:.0f}")
        
        if 'scene' in outcome:
            parts.append(f"scene={outcome['scene']}")
        
        if 'progress' in outcome:
            parts.append("progress made")
        
        return ", ".join(parts) if parts else "outcome recorded"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'perceptual_memories': len(self.perceptual_memories),
            'cognitive_memories': len(self.cognitive_memories),
            'total_memories': len(self.perceptual_memories) + len(self.cognitive_memories),
            'perceptual_capacity': self.perceptual_capacity,
            'cognitive_capacity': self.cognitive_capacity
        }
    
    def get_recent_successes(self, n: int = 5) -> List[CognitiveMemory]:
        """
        Get recent successful decisions.
        
        Args:
            n: Number of successes to retrieve
            
        Returns:
            List of successful cognitive memories
        """
        successes = [
            mem for mem in self.cognitive_memories
            if mem.success
        ]
        return list(successes)[-n:]
    
    def clear_old_memories(self, age_threshold_seconds: float = 3600):
        """
        Clear memories older than threshold.
        
        Args:
            age_threshold_seconds: Age threshold in seconds
        """
        current_time = time.time()
        
        # Clear old perceptual memories
        while (self.perceptual_memories and 
               current_time - self.perceptual_memories[0].timestamp > age_threshold_seconds):
            self.perceptual_memories.popleft()
            if self.perceptual_embeddings:
                self.perceptual_embeddings.pop(0)
        
        # Clear old cognitive memories
        while (self.cognitive_memories and 
               current_time - self.cognitive_memories[0].timestamp > age_threshold_seconds):
            self.cognitive_memories.popleft()
            if self.cognitive_embeddings:
                self.cognitive_embeddings.pop(0)
        
        print(f"[RAG] Cleared memories older than {age_threshold_seconds}s")
