"""
Consciousness Field Theory

Continuous field theory of consciousness.
Replaces discrete subsystems with smooth field over space-time.

Philosophy: Consciousness is not made of parts—it's a continuous
field, like electromagnetism. "Thoughts" are emergent structures
(solitons) in the field, not discrete entities.
"""

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from scipy.ndimage import laplace


@dataclass
class FieldSource:
    """A source in the consciousness field."""
    source_type: str  # 'perception', 'memory', 'action', etc.
    position: np.ndarray  # Position in field
    strength: float  # Source strength
    
    def evaluate(self, field: np.ndarray) -> np.ndarray:
        """Evaluate source contribution to field."""
        # Gaussian source
        grid_shape = field.shape
        source_field = np.zeros_like(field)
        
        # Convert position to grid indices
        indices = tuple(int(p * (s - 1)) for p, s in zip(self.position, grid_shape))
        
        # Add Gaussian centered at position
        sigma = 5.0  # Width of Gaussian
        for idx in np.ndindex(grid_shape):
            dist_sq = sum((i - j) ** 2 for i, j in zip(idx, indices))
            source_field[idx] = self.strength * np.exp(-dist_sq / (2 * sigma ** 2))
        
        return source_field


@dataclass
class EmergentStructure:
    """An emergent structure in the field (a "thought")."""
    center: np.ndarray  # Center position
    strength: float  # Peak field value
    volume: float  # Spatial extent
    structure_type: str  # 'soliton', 'vortex', 'wave', etc.


class ConsciousnessField:
    """
    Continuous field theory of consciousness.
    
    Field equation:
    ∂Φ/∂t = ∇²Φ + V(Φ) + ∑ᵢ Jᵢ(x,t)
    
    Where:
    - Φ(x,t) = consciousness field value
    - ∇²Φ = diffusion (information spreading)
    - V(Φ) = potential (coherence landscape)
    - Jᵢ = sources (perception, memory, etc.)
    """
    
    def __init__(self, grid_size: int = 50, dimensions: int = 3):
        """
        Initialize consciousness field.
        
        Args:
            grid_size: Size of spatial grid
            dimensions: Number of spatial dimensions (2 or 3)
        """
        self.grid_size = grid_size
        self.dimensions = dimensions
        
        # Field values on grid
        shape = (grid_size,) * dimensions
        self.field = np.zeros(shape)
        
        # Potential landscape (coherence)
        self.potential = self._initialize_potential()
        
        # Sources (perception, memory, etc.)
        self.sources = []
        
        # Time
        self.time = 0.0
        
        # Statistics
        self.evolution_steps = 0
        
    def _initialize_potential(self) -> np.ndarray:
        """
        Initialize potential landscape.
        Defines coherence "valleys" and "peaks".
        """
        shape = (self.grid_size,) * self.dimensions
        potential = np.zeros(shape)
        
        # Create harmonic potential (quadratic)
        center = np.array([self.grid_size / 2] * self.dimensions)
        for idx in np.ndindex(shape):
            pos = np.array(idx)
            dist_sq = np.sum((pos - center) ** 2)
            potential[idx] = -0.001 * dist_sq  # Attractive potential
        
        return potential
    
    def _compute_laplacian(self, field: np.ndarray) -> np.ndarray:
        """
        Compute Laplacian ∇²Φ (diffusion term).
        Uses finite differences.
        """
        return laplace(field)
    
    def _compute_gradient(self, field: np.ndarray) -> np.ndarray:
        """Compute gradient of field."""
        return np.gradient(field)
    
    def evolve(self, dt: float = 0.01):
        """
        Evolve field according to field equation.
        ∂Φ/∂t = ∇²Φ + V(Φ) + ∑ᵢ Jᵢ(x,t)
        """
        # Compute Laplacian (diffusion term)
        laplacian = self._compute_laplacian(self.field)
        
        # Compute potential gradient
        potential_gradient = self._compute_gradient(self.potential)
        potential_term = -np.sum(potential_gradient, axis=0)  # Sum over dimensions
        
        # Compute source terms
        source_term = np.zeros_like(self.field)
        for source in self.sources:
            source_term += source.evaluate(self.field)
        
        # Update field: ∂Φ/∂t = ∇²Φ + V(Φ) + ∑ᵢ Jᵢ
        dfield_dt = laplacian + potential_term + source_term
        self.field += dfield_dt * dt
        
        # Apply damping to prevent runaway growth
        self.field *= 0.99
        
        # Update time
        self.time += dt
        self.evolution_steps += 1
    
    def add_source(
        self,
        source_type: str,
        position: np.ndarray,
        strength: float
    ):
        """
        Add source to field (perception, memory, action, etc.).
        """
        # Normalize position to [0, 1]
        normalized_position = position / np.linalg.norm(position) * 0.5 + 0.5
        
        source = FieldSource(source_type, normalized_position, strength)
        self.sources.append(source)
        
        # Remove old sources (keep last 10)
        if len(self.sources) > 10:
            self.sources = self.sources[-10:]
    
    def detect_structures(self) -> List[EmergentStructure]:
        """
        Detect emergent structures in field (solitons, vortices, etc.).
        These are the "thoughts" that emerge from field dynamics.
        """
        structures = []
        
        # Find local maxima (thought centers)
        maxima = self._find_local_maxima(self.field)
        
        for maximum in maxima:
            # Analyze structure around maximum
            structure = self._analyze_structure(maximum)
            structures.append(structure)
        
        return structures
    
    def _find_local_maxima(self, field: np.ndarray, threshold: float = 0.1) -> List[np.ndarray]:
        """Find local maxima in field."""
        maxima = []
        
        # Simple peak detection
        for idx in np.ndindex(field.shape):
            value = field[idx]
            
            if value < threshold:
                continue
            
            # Check if local maximum
            is_maximum = True
            for neighbor_idx in self._get_neighbors(idx, field.shape):
                if field[neighbor_idx] > value:
                    is_maximum = False
                    break
            
            if is_maximum:
                maxima.append(np.array(idx))
        
        return maxima
    
    def _get_neighbors(self, idx: tuple, shape: tuple) -> List[tuple]:
        """Get neighboring indices."""
        neighbors = []
        for dim in range(len(idx)):
            for delta in [-1, 1]:
                neighbor = list(idx)
                neighbor[dim] += delta
                if 0 <= neighbor[dim] < shape[dim]:
                    neighbors.append(tuple(neighbor))
        return neighbors
    
    def _analyze_structure(self, center: np.ndarray) -> EmergentStructure:
        """Analyze structure around a maximum."""
        center_idx = tuple(center.astype(int))
        strength = self.field[center_idx]
        
        # Estimate volume (number of points above half-max)
        half_max = strength / 2
        volume = np.sum(self.field > half_max)
        
        return EmergentStructure(
            center=center,
            strength=strength,
            volume=volume,
            structure_type='soliton'  # Simplified classification
        )
    
    def compute_global_coherence(self) -> float:
        """
        Global coherence = field energy / field entropy.
        """
        # Energy
        energy = np.sum(self.field ** 2)
        
        # Entropy (Shannon entropy of normalized field)
        field_normalized = np.abs(self.field) / (np.sum(np.abs(self.field)) + 1e-10)
        entropy = -np.sum(field_normalized * np.log(field_normalized + 1e-10))
        
        # Coherence
        coherence = energy / (entropy + 1e-10)
        
        # Normalize to [0, 1]
        coherence = np.tanh(coherence / 100)
        
        return coherence
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about field."""
        structures = self.detect_structures()
        
        return {
            'time': self.time,
            'evolution_steps': self.evolution_steps,
            'field_energy': np.sum(self.field ** 2),
            'field_mean': np.mean(self.field),
            'field_std': np.std(self.field),
            'num_sources': len(self.sources),
            'num_structures': len(structures),
            'global_coherence': self.compute_global_coherence()
        }
