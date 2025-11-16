"""
Decorator-based Python↔HaackLang integration.

Provides decorators for mapping Python subsystems to HaackLang constructs:
- @haack_track - Map subsystem to a track
- @haack_truthvalue - Map function to truthvalue update
- @haack_context - Map class to cognitive context
- @haack_guard - Map method to guard condition
"""

from typing import Callable, Optional, Any
from functools import wraps


# Global registry of decorated functions
HAACK_REGISTRY = {
    'tracks': {},
    'truthvalues': {},
    'contexts': {},
    'guards': {}
}


def haack_track(
    track_name: str,
    period: int = 1,
    logic: str = 'classical'
):
    """
    Decorator to map a Python class/function to a HaackLang track.
    
    Example:
        @haack_track('perception', period=1, logic='classical')
        class PerceptionSubsystem:
            def process(self, game_state):
                return threat_level
    
    Args:
        track_name: Name of the track
        period: Beat period for this track
        logic: Logic type ('classical', 'fuzzy', 'paraconsistent')
    """
    def decorator(cls_or_func):
        # Register with HaackLang runtime
        HAACK_REGISTRY['tracks'][track_name] = {
            'target': cls_or_func,
            'period': period,
            'logic': logic
        }
        
        # Add metadata to class/function
        if isinstance(cls_or_func, type):
            cls_or_func._haack_track = track_name
            cls_or_func._haack_period = period
            cls_or_func._haack_logic = logic
        
        return cls_or_func
    
    return decorator


def haack_truthvalue(
    truthvalue_name: str,
    track: Optional[str] = None
):
    """
    Decorator to map a Python function to update a HaackLang truthvalue.
    
    Example:
        @haack_truthvalue('danger', track='perception')
        def detect_threats(game_state):
            return 0.9  # danger level
    
    Args:
        truthvalue_name: Name of the truthvalue in HaackLang
        track: Which track to update (default: auto-detect from context)
    """
    def decorator(func: Callable):
        # Register
        if truthvalue_name not in HAACK_REGISTRY['truthvalues']:
            HAACK_REGISTRY['truthvalues'][truthvalue_name] = []
        
        HAACK_REGISTRY['truthvalues'][truthvalue_name].append({
            'function': func,
            'track': track
        })
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute original function
            result = func(*args, **kwargs)
            
            # Propagate to HaackLang runtime if available
            if hasattr(wrapper, '_haack_runtime'):
                runtime = wrapper._haack_runtime
                track_name = track or _infer_track_from_context()
                runtime.set_truthvalue(truthvalue_name, track_name, result)
            
            return result
        
        wrapper._haack_truthvalue = truthvalue_name
        wrapper._haack_track = track
        
        return wrapper
    
    return decorator


def haack_context(
    context_name: str,
    priority: Optional[list] = None,
    logic: Optional[str] = None
):
    """
    Decorator to map a Python class to a HaackLang context.
    
    Example:
        @haack_context('combat', priority=['reflex', 'perception', 'strategic'])
        class CombatMode:
            def __init__(self):
                self.active = False
            
            def enter(self):
                self.active = True
    
    Args:
        context_name: Name of the context
        priority: Track priority list
        logic: Default logic for this context
    """
    def decorator(cls):
        # Register
        HAACK_REGISTRY['contexts'][context_name] = {
            'class': cls,
            'priority': priority or [],
            'logic': logic
        }
        
        # Add metadata
        cls._haack_context = context_name
        cls._haack_priority = priority
        cls._haack_logic = logic
        
        # Wrap __init__ to notify runtime on instantiation
        original_init = cls.__init__
        
        @wraps(original_init)
        def wrapped_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            # Notify HaackLang runtime if available
            if hasattr(cls, '_haack_runtime'):
                runtime = cls._haack_runtime
                runtime.switch_context(context_name)
        
        cls.__init__ = wrapped_init
        
        return cls
    
    return decorator


def haack_guard(
    track: str,
    condition: str
):
    """
    Decorator to map a Python method to a HaackLang guard.
    
    Example:
        @haack_guard('reflex', condition='threat_level > 0.8')
        def emergency_dodge(self):
            return Action.DODGE
    
    Args:
        track: Track that must be active for guard to fire
        condition: Boolean condition (evaluated in HaackLang)
    """
    def decorator(method: Callable):
        # Register
        guard_id = f"{method.__name__}_{track}"
        HAACK_REGISTRY['guards'][guard_id] = {
            'method': method,
            'track': track,
            'condition': condition
        }
        
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Check if track is active (if runtime available)
            if hasattr(wrapper, '_haack_runtime'):
                runtime = wrapper._haack_runtime
                active_tracks = runtime.get_active_tracks()
                
                if track not in active_tracks:
                    # Track not active, don't execute
                    return None
                
                # Evaluate condition in HaackLang context
                try:
                    # Get current truthvalue state from runtime
                    truthvalues = runtime.get_truthvalues()
                    
                    # Simple condition evaluation (supports basic comparisons)
                    # Example: "threat_level > 0.8"
                    condition_result = eval(condition, {"__builtins__": {}}, truthvalues)
                    
                    if not condition_result:
                        return None
                except Exception as e:
                    # If condition evaluation fails, log and don't execute
                    print(f"[HAACK-GUARD] Condition evaluation failed: {e}")
                    return None
            
            return method(self, *args, **kwargs)
        
        wrapper._haack_guard_track = track
        wrapper._haack_guard_condition = condition
        
        return wrapper
    
    return decorator


def _infer_track_from_context() -> str:
    """
    Infer which track to use based on current context.
    
    This is a heuristic fallback when track is not explicitly specified.
    
    Returns:
        Track name (default: 'main')
    """
    # This would ideally query the HaackLang runtime for current context
    # and map context → track
    # For now, return default
    return 'main'


def bind_runtime(runtime):
    """
    Bind HaackLang runtime to all decorated functions.
    
    This allows decorated functions to communicate with the HaackLang
    runtime for truthvalue synchronization, track checking, etc.
    
    Args:
        runtime: HaackLangRuntime instance
    """
    # Bind to truthvalue functions
    for tv_name, funcs in HAACK_REGISTRY['truthvalues'].items():
        for func_data in funcs:
            func = func_data['function']
            func._haack_runtime = runtime
    
    # Bind to context classes
    for ctx_name, ctx_data in HAACK_REGISTRY['contexts'].items():
        cls = ctx_data['class']
        cls._haack_runtime = runtime
    
    # Bind to guard methods
    for guard_id, guard_data in HAACK_REGISTRY['guards'].items():
        method = guard_data['method']
        method._haack_runtime = runtime
    
    print(f"[HAACK-BRIDGE] Bound runtime to {len(HAACK_REGISTRY['truthvalues'])} truthvalues, "
          f"{len(HAACK_REGISTRY['contexts'])} contexts, {len(HAACK_REGISTRY['guards'])} guards")


def get_registry():
    """Get the global HaackLang decorator registry."""
    return HAACK_REGISTRY


def print_registry():
    """Print all registered HaackLang decorators."""
    print("\n" + "="*70)
    print("HaackLang Decorator Registry")
    print("="*70)
    
    print(f"\nTracks ({len(HAACK_REGISTRY['tracks'])}):")
    for track_name, data in HAACK_REGISTRY['tracks'].items():
        print(f"  • {track_name}: period={data['period']}, logic={data['logic']}")
    
    print(f"\nTruthValues ({len(HAACK_REGISTRY['truthvalues'])}):")
    for tv_name, funcs in HAACK_REGISTRY['truthvalues'].items():
        print(f"  • {tv_name}: {len(funcs)} functions")
        for func_data in funcs:
            func = func_data['function']
            track = func_data['track'] or 'auto'
            print(f"      - {func.__name__} → track={track}")
    
    print(f"\nContexts ({len(HAACK_REGISTRY['contexts'])}):")
    for ctx_name, data in HAACK_REGISTRY['contexts'].items():
        cls = data['class']
        priority = data['priority'] or []
        print(f"  • {ctx_name}: {cls.__name__}, priority={priority}")
    
    print(f"\nGuards ({len(HAACK_REGISTRY['guards'])}):")
    for guard_id, data in HAACK_REGISTRY['guards'].items():
        method = data['method']
        track = data['track']
        condition = data['condition']
        print(f"  • {guard_id}: {method.__name__} on {track} when {condition}")
    
    print("="*70 + "\n")
