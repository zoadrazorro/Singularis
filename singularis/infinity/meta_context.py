"""
Meta-Context System - Hierarchical Temporal Contexts

Implements context stacks + timed contexts for hierarchical, temporal
cognitive organization.

Key features:
- Context stacks (micro/macro/conditional)
- Timed contexts (auto-expire)
- Conditional transitions
- Context-specific cognitive modifiers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import time


class ContextLevel(Enum):
    """Hierarchical context levels"""
    MICRO = "micro"      # Short-lived, focused (e.g., "evaluate_threat for 3 beats")
    MACRO = "macro"      # Long-term operational mode (e.g., "exploration")
    CONDITIONAL = "conditional"  # Rule-based transitions


@dataclass
class Context:
    """
    Individual context with metadata and modifiers.
    
    A context represents a cognitive mode with specific:
    - Track amplifications/suppressions
    - Coherence thresholds
    - Emotional modulation
    - Memory priorities
    """
    name: str
    level: ContextLevel
    
    # Temporal
    expires_at: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    duration: Optional[float] = None
    
    # Hierarchy
    parent_context: Optional['Context'] = None
    child_contexts: List['Context'] = field(default_factory=list)
    
    # Cognitive modifiers
    track_amplifications: Dict[str, float] = field(default_factory=dict)
    track_suppressions: Dict[str, float] = field(default_factory=dict)
    coherence_threshold: Optional[float] = None
    emotion_modulation: Dict[str, float] = field(default_factory=dict)
    plasticity_factor: float = 1.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if context has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def time_remaining(self) -> Optional[float]:
        """Get remaining time in seconds"""
        if self.expires_at is None:
            return None
        return max(0.0, self.expires_at - time.time())
    
    def age(self) -> float:
        """Get context age in seconds"""
        return time.time() - self.created_at
    
    def __repr__(self):
        status = "expired" if self.is_expired() else "active"
        if self.expires_at:
            remaining = self.time_remaining()
            return f"Context({self.name}, {self.level.value}, {status}, {remaining:.1f}s left)"
        return f"Context({self.name}, {self.level.value}, {status})"


@dataclass
class ConditionalRule:
    """
    Rule for automatic context transitions.
    
    When condition(state) is True, perform action on target_context.
    """
    condition: Callable[['CognitiveState'], bool]
    action: str  # 'enter' or 'exit'
    target_context: Context
    priority: int = 0
    cooldown: float = 0.0  # Minimum time between activations
    last_triggered: float = 0.0
    
    def can_trigger(self) -> bool:
        """Check if enough time has passed since last trigger"""
        return (time.time() - self.last_triggered) >= self.cooldown
    
    def trigger(self):
        """Mark as triggered"""
        self.last_triggered = time.time()


class ContextStack:
    """
    Stack-based context management.
    
    Contexts are pushed/popped in LIFO order.
    Top of stack = currently active context.
    """
    
    def __init__(self, max_depth: int = 10):
        self.stack: List[Context] = []
        self.max_depth = max_depth
    
    def push(self, context: Context) -> bool:
        """
        Push context onto stack.
        
        Returns:
            True if successful, False if stack full
        """
        if len(self.stack) >= self.max_depth:
            return False
        
        # Set parent relationship
        if self.stack:
            context.parent_context = self.stack[-1]
            self.stack[-1].child_contexts.append(context)
        
        self.stack.append(context)
        return True
    
    def pop(self) -> Optional[Context]:
        """Pop context from stack"""
        if not self.stack:
            return None
        
        context = self.stack.pop()
        
        # Clear parent relationship
        if context.parent_context:
            context.parent_context.child_contexts.remove(context)
            context.parent_context = None
        
        return context
    
    def peek(self) -> Optional[Context]:
        """Get top context without removing"""
        return self.stack[-1] if self.stack else None
    
    def find(self, name: str) -> Optional[Context]:
        """Find context by name in stack"""
        for context in self.stack:
            if context.name == name:
                return context
        return None
    
    def remove(self, context: Context) -> bool:
        """Remove specific context from stack"""
        if context in self.stack:
            self.stack.remove(context)
            return True
        return False
    
    def clear(self):
        """Clear entire stack"""
        self.stack.clear()
    
    def depth(self) -> int:
        """Get current stack depth"""
        return len(self.stack)
    
    def __repr__(self):
        contexts = " -> ".join(c.name for c in self.stack)
        return f"ContextStack[{contexts}]"


class MetaContextSystem:
    """
    Hierarchical temporal context management.
    
    Manages context stacks, timed contexts, and conditional transitions.
    Applies context-specific cognitive modifications.
    """
    
    def __init__(self, verbose: bool = True):
        self.context_stack = ContextStack()
        self.active_contexts: List[Context] = []
        self.context_rules: List[ConditionalRule] = []
        self.context_history: List[Context] = []
        self.verbose = verbose
        
        # Statistics
        self.total_transitions = 0
        self.total_expirations = 0
        self.total_rule_triggers = 0
        
        if verbose:
            print("[META-CONTEXT] System initialized")
    
    def push_context(
        self,
        context: Context,
        duration: Optional[float] = None
    ) -> bool:
        """
        Push new context onto stack.
        
        Args:
            context: Context to activate
            duration: Optional duration in seconds (for timed contexts)
        
        Returns:
            True if successful
        """
        # Set expiration if duration provided
        if duration is not None:
            context.duration = duration
            context.expires_at = time.time() + duration
        
        # Push onto stack
        success = self.context_stack.push(context)
        
        if success:
            self.active_contexts.append(context)
            self.total_transitions += 1
            
            # Apply context modifiers
            self.apply_context_modifiers(context)
            
            if self.verbose:
                print(f"[META-CONTEXT] + Pushed: {context}")
                print(f"[META-CONTEXT]   Stack depth: {self.context_stack.depth()}")
        
        return success
    
    def pop_context(self, context: Optional[Context] = None) -> Optional[Context]:
        """
        Remove context from stack.
        
        Args:
            context: Specific context to remove, or None for top of stack
        
        Returns:
            Removed context
        """
        if context is None:
            # Pop from top
            removed = self.context_stack.pop()
        else:
            # Remove specific context
            self.context_stack.remove(context)
            removed = context
        
        if removed:
            if removed in self.active_contexts:
                self.active_contexts.remove(removed)
            
            self.context_history.append(removed)
            self.total_transitions += 1
            
            # Restore previous context
            self.restore_previous_context()
            
            if self.verbose:
                print(f"[META-CONTEXT] - Popped: {removed.name}")
                print(f"[META-CONTEXT]   Stack depth: {self.context_stack.depth()}")
        
        return removed
    
    def update_contexts(self, cognitive_state: 'CognitiveState'):
        """
        Update contexts based on rules and timers.
        
        This should be called every cognitive cycle to:
        - Expire timed contexts
        - Evaluate conditional rules
        - Apply context transitions
        """
        # 1. Check timed contexts for expiration
        expired = [c for c in self.active_contexts if c.is_expired()]
        for context in expired:
            if self.verbose:
                print(f"[META-CONTEXT] EXPIRED: {context.name}")
            self.pop_context(context)
            self.total_expirations += 1
        
        # 2. Evaluate conditional context rules
        for rule in sorted(self.context_rules, key=lambda r: r.priority, reverse=True):
            if not rule.can_trigger():
                continue
            
            try:
                if rule.condition(cognitive_state):
                    if rule.action == 'enter':
                        # Check if already active
                        if not self.context_stack.find(rule.target_context.name):
                            self.push_context(rule.target_context)
                            rule.trigger()
                            self.total_rule_triggers += 1
                            
                            if self.verbose:
                                print(f"[META-CONTEXT] RULE triggered: {rule.target_context.name}")
                    
                    elif rule.action == 'exit':
                        existing = self.context_stack.find(rule.target_context.name)
                        if existing:
                            self.pop_context(existing)
                            rule.trigger()
                            self.total_rule_triggers += 1
            
            except Exception as e:
                if self.verbose:
                    print(f"[META-CONTEXT] WARNING Rule error: {e}")
    
    def apply_context_modifiers(self, context: Context):
        """
        Apply cognitive modifications for active context.
        
        This modifies the cognitive state based on context-specific settings.
        """
        if self.verbose and (context.track_amplifications or context.track_suppressions):
            print(f"[META-CONTEXT] Applying modifiers for '{context.name}'")
        
        # Track amplifications
        for track, factor in context.track_amplifications.items():
            if self.verbose:
                print(f"  + Amplify {track} by {factor}x")
        
        # Track suppressions
        for track, factor in context.track_suppressions.items():
            if self.verbose:
                print(f"  - Suppress {track} by {factor}x")
        
        # Coherence threshold
        if context.coherence_threshold is not None:
            if self.verbose:
                print(f"  * Coherence threshold: {context.coherence_threshold}")
        
        # Emotion modulation
        for emotion, factor in context.emotion_modulation.items():
            if self.verbose:
                print(f"  ~ Modulate {emotion} by {factor}x")
        
        # Plasticity
        if context.plasticity_factor != 1.0:
            if self.verbose:
                print(f"  @ Plasticity: {context.plasticity_factor}x")
    
    def restore_previous_context(self):
        """Restore modifiers from previous context"""
        previous = self.context_stack.peek()
        if previous:
            self.apply_context_modifiers(previous)
    
    def add_rule(self, rule: ConditionalRule):
        """Add conditional context rule"""
        self.context_rules.append(rule)
        if self.verbose:
            print(f"[META-CONTEXT] + Added rule: {rule.action} '{rule.target_context.name}'")
    
    def remove_rule(self, rule: ConditionalRule):
        """Remove conditional rule"""
        if rule in self.context_rules:
            self.context_rules.remove(rule)
    
    def get_active_context(self) -> Optional[Context]:
        """Get currently active context (top of stack)"""
        return self.context_stack.peek()
    
    def get_all_active_contexts(self) -> List[Context]:
        """Get all active contexts in stack order"""
        return list(self.context_stack.stack)
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        return {
            'total_transitions': self.total_transitions,
            'total_expirations': self.total_expirations,
            'total_rule_triggers': self.total_rule_triggers,
            'active_contexts': len(self.active_contexts),
            'stack_depth': self.context_stack.depth(),
            'total_rules': len(self.context_rules),
            'history_size': len(self.context_history),
        }
    
    def __repr__(self):
        return f"MetaContextSystem({self.context_stack})"


# ========== Predefined Context Templates ==========

def create_survival_context() -> Context:
    """Create survival/danger context"""
    return Context(
        name='survival',
        level=ContextLevel.MACRO,
        track_amplifications={
            'perception': 1.5,
            'fast_response': 1.8,
        },
        track_suppressions={
            'reflection': 0.3,
            'creativity': 0.2,
        },
        emotion_modulation={
            'fear': 1.2,
            'alertness': 1.5,
        },
        coherence_threshold=0.5,
        plasticity_factor=0.7,
    )


def create_creative_context() -> Context:
    """Create creative/exploration context"""
    return Context(
        name='creative',
        level=ContextLevel.MACRO,
        track_amplifications={
            'intuition': 1.4,
            'divergent_thinking': 1.6,
        },
        track_suppressions={
            'critical_analysis': 0.6,
        },
        emotion_modulation={
            'curiosity': 1.3,
            'openness': 1.4,
        },
        coherence_threshold=0.6,  # Lower threshold = more tolerance for chaos
        plasticity_factor=1.3,
    )


def create_learning_context() -> Context:
    """Create learning/consolidation context"""
    return Context(
        name='learning',
        level=ContextLevel.MACRO,
        track_amplifications={
            'reflection': 1.5,
            'memory_consolidation': 1.8,
        },
        emotion_modulation={
            'focus': 1.3,
        },
        coherence_threshold=0.7,
        plasticity_factor=1.5,  # High plasticity for learning
    )


def create_reflection_context() -> Context:
    """Create reflection/metacognition context"""
    return Context(
        name='reflection',
        level=ContextLevel.MACRO,
        track_amplifications={
            'metacognition': 1.6,
            'introspection': 1.5,
        },
        track_suppressions={
            'fast_response': 0.4,
        },
        coherence_threshold=0.8,  # High coherence required
        plasticity_factor=1.0,
    )


def create_threat_evaluation_context(duration: float = 3.0) -> Context:
    """Create micro-context for threat evaluation"""
    return Context(
        name='evaluate_threat',
        level=ContextLevel.MICRO,
        duration=duration,
        track_amplifications={
            'perception': 2.0,
            'danger_assessment': 1.8,
        },
        track_suppressions={
            'reflection': 0.1,
        },
    )


# ========== Mock CognitiveState ==========

class CognitiveState:
    """Mock cognitive state for type hints"""
    def __init__(self):
        self.truth_values: Dict = {}
        self.tracks: List = []
        self.context: str = 'default'
        self.danger: float = 0.0
        self.stress: float = 0.0
