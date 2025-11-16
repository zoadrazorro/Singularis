"""
Game World Model - Core Logic

Maintains structured game world state and computes tactical features.
"""

import time
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
import numpy as np
from loguru import logger


# ========================================
# Data Models
# ========================================

@dataclass
class PlayerState:
    """Player state snapshot."""
    id: str = "player"
    pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    facing_yaw: float = 0.0  # degrees
    facing_pitch: float = 0.0
    health: float = 1.0  # 0-1
    stamina: float = 1.0
    magicka: float = 1.0
    sneaking: bool = False
    in_combat: bool = False
    weapon_type: str = "unarmed"
    is_detected: bool = False
    timestamp: float = 0.0


@dataclass
class NPCState:
    """NPC entity state."""
    id: str
    pos: Tuple[float, float, float]
    vel: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    facing_yaw: float = 0.0
    health: float = 1.0
    is_enemy: bool = False
    is_ally: bool = False
    is_alive: bool = True
    is_in_combat: bool = False
    has_line_of_sight_to_player: bool = False
    distance_to_player: float = 0.0
    awareness_level: float = 0.0  # 0-1: how aware of player
    timestamp: float = 0.0


@dataclass
class ObjectState:
    """Interactive object state."""
    id: str
    type: str  # "container", "door", "lever", etc.
    pos: Tuple[float, float, float]
    is_locked: bool = False
    is_open: bool = False
    is_trap: bool = False
    is_quest_object: bool = False
    timestamp: float = 0.0


@dataclass
class CoverSpot:
    """Cover location."""
    id: str
    pos: Tuple[float, float, float]
    cover_rating: float = 0.5  # 0-1: quality of cover
    distance_to_player: float = 0.0
    bearing_deg: float = 0.0  # relative to player facing


@dataclass
class EntityState:
    """Generic entity wrapper."""
    entity_id: str
    entity_type: str  # "player", "npc", "object"
    pos: Tuple[float, float, float]
    data: Any  # PlayerState, NPCState, or ObjectState


@dataclass
class EnemyInfo:
    """Compact enemy info for features."""
    id: str
    distance: float
    bearing_deg: float  # relative to player facing
    has_los: bool
    health: float
    awareness: float


@dataclass
class GameWorldFeatures:
    """
    Computed tactical features from game world state.
    
    These are the high-level features that ActionArbiter and LLM use
    for decision-making.
    """
    # Threat assessment
    threat_level: float = 0.0  # 0-1: overall danger
    num_enemies_total: int = 0
    num_enemies_in_los: int = 0
    num_enemies_aware: int = 0  # awareness > 0.5
    
    # Nearest enemy
    nearest_enemy: Optional[EnemyInfo] = None
    
    # Cover & escape
    best_cover_spot: Optional[CoverSpot] = None
    escape_vector: Tuple[float, float] = (0.0, 0.0)  # 2D direction (away from threats)
    
    # Stealth
    is_player_in_stealth_danger: bool = False
    stealth_safety_score: float = 1.0  # 0-1: higher = safer
    
    # Opportunities
    loot_opportunity_available: bool = False
    nearest_loot_distance: float = 999.0
    
    # Environment
    cell_name: str = ""
    is_interior: bool = False
    
    # Meta
    timestamp: float = 0.0
    snapshot_age: float = 0.0  # How stale is the data
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for BeingState."""
        return {
            'threat_level': self.threat_level,
            'num_enemies_total': self.num_enemies_total,
            'num_enemies_in_los': self.num_enemies_in_los,
            'num_enemies_aware': self.num_enemies_aware,
            'nearest_enemy': {
                'id': self.nearest_enemy.id,
                'distance': self.nearest_enemy.distance,
                'bearing_deg': self.nearest_enemy.bearing_deg,
                'has_los': self.nearest_enemy.has_los,
                'health': self.nearest_enemy.health,
                'awareness': self.nearest_enemy.awareness
            } if self.nearest_enemy else None,
            'best_cover_spot': {
                'id': self.best_cover_spot.id,
                'distance': self.best_cover_spot.distance_to_player,
                'bearing_deg': self.best_cover_spot.bearing_deg,
                'cover_rating': self.best_cover_spot.cover_rating
            } if self.best_cover_spot else None,
            'escape_vector': list(self.escape_vector),
            'is_player_in_stealth_danger': self.is_player_in_stealth_danger,
            'stealth_safety_score': self.stealth_safety_score,
            'loot_opportunity_available': self.loot_opportunity_available,
            'nearest_loot_distance': self.nearest_loot_distance,
            'cell_name': self.cell_name,
            'is_interior': self.is_interior,
            'timestamp': self.timestamp,
            'snapshot_age': self.snapshot_age
        }


# ========================================
# Game World Model
# ========================================

class GameWorldModel:
    """
    Maintains structured game world state and computes tactical features.
    
    Architecture:
    1. Receives engine snapshots (JSON from game)
    2. Updates internal entity tracking
    3. Computes derived features (threat, cover, etc.)
    4. Provides features to BeingState / ActionArbiter
    """
    
    def __init__(
        self,
        history_size: int = 10,
        threat_decay_rate: float = 0.95
    ):
        """
        Initialize game world model.
        
        Args:
            history_size: Number of snapshots to keep in history
            threat_decay_rate: How quickly threat decays over time
        """
        # Current state
        self.last_snapshot_time: float = 0.0
        self.player: Optional[PlayerState] = None
        self.npcs: Dict[str, NPCState] = {}
        self.objects: Dict[str, ObjectState] = {}
        self.cover_spots: Dict[str, CoverSpot] = {}
        self.recent_events: deque = deque(maxlen=20)
        
        # History
        self.history_size = history_size
        self.snapshot_history: deque = deque(maxlen=history_size)
        
        # Features
        self.current_features: Optional[GameWorldFeatures] = None
        
        # Config
        self.threat_decay_rate = threat_decay_rate
        
        # Stats
        self.total_updates = 0
        self.total_features_computed = 0
        
        logger.info("[GWM] Game World Model initialized")
    
    def update_from_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """
        Update internal state from engine snapshot.
        
        Args:
            snapshot: Raw snapshot dict from game engine
        """
        try:
            current_time = time.time()
            self.last_snapshot_time = current_time
            
            # Update player
            if 'player' in snapshot:
                self.player = PlayerState(
                    **snapshot['player'],
                    timestamp=current_time
                )
            
            # Update NPCs
            if 'npcs' in snapshot:
                # Clear old NPCs
                old_npc_ids = set(self.npcs.keys())
                new_npc_ids = set()
                
                for npc_data in snapshot['npcs']:
                    npc_id = npc_data['id']
                    self.npcs[npc_id] = NPCState(
                        **npc_data,
                        timestamp=current_time
                    )
                    new_npc_ids.add(npc_id)
                
                # Remove NPCs that disappeared
                for npc_id in old_npc_ids - new_npc_ids:
                    del self.npcs[npc_id]
            
            # Update objects
            if 'objects' in snapshot:
                old_obj_ids = set(self.objects.keys())
                new_obj_ids = set()
                
                for obj_data in snapshot['objects']:
                    obj_id = obj_data['id']
                    self.objects[obj_id] = ObjectState(
                        **obj_data,
                        timestamp=current_time
                    )
                    new_obj_ids.add(obj_id)
                
                for obj_id in old_obj_ids - new_obj_ids:
                    del self.objects[obj_id]
            
            # Update cover spots
            if 'cover_spots_raw' in snapshot:
                self.cover_spots.clear()
                for cover_data in snapshot['cover_spots_raw']:
                    cover_id = cover_data['id']
                    self.cover_spots[cover_id] = CoverSpot(
                        id=cover_id,
                        pos=tuple(cover_data['pos']),
                        cover_rating=cover_data.get('cover_rating', 0.5),
                        distance_to_player=0.0,
                        bearing_deg=0.0
                    )
            
            # Update recent events
            if 'recent_events' in snapshot:
                for event in snapshot['recent_events']:
                    self.recent_events.append((current_time, event))
            
            # Store in history
            self.snapshot_history.append({
                'timestamp': current_time,
                'player': self.player,
                'num_npcs': len(self.npcs),
                'num_objects': len(self.objects)
            })
            
            self.total_updates += 1
            
            logger.debug(
                f"[GWM] Updated: {len(self.npcs)} NPCs, "
                f"{len(self.objects)} objects, {len(self.cover_spots)} cover spots"
            )
        
        except Exception as e:
            logger.error(f"[GWM] Snapshot update error: {e}")
    
    def compute_features(self) -> GameWorldFeatures:
        """
        Compute tactical features from current world state.
        
        Returns:
            GameWorldFeatures with all computed metrics
        """
        try:
            current_time = time.time()
            snapshot_age = current_time - self.last_snapshot_time
            
            features = GameWorldFeatures(
                timestamp=current_time,
                snapshot_age=snapshot_age
            )
            
            if self.player is None:
                logger.warning("[GWM] No player state, returning empty features")
                return features
            
            # Environment
            features.cell_name = getattr(self.player, 'cell_name', '')
            features.is_interior = getattr(self.player, 'is_interior', False)
            
            # Analyze NPCs
            enemies = [npc for npc in self.npcs.values() if npc.is_enemy and npc.is_alive]
            features.num_enemies_total = len(enemies)
            
            if enemies:
                # Count enemies with LOS
                features.num_enemies_in_los = sum(1 for e in enemies if e.has_line_of_sight_to_player)
                features.num_enemies_aware = sum(1 for e in enemies if e.awareness_level > 0.5)
                
                # Find nearest enemy
                nearest = min(enemies, key=lambda e: e.distance_to_player)
                bearing = self._compute_bearing(
                    self.player.pos,
                    self.player.facing_yaw,
                    nearest.pos
                )
                
                features.nearest_enemy = EnemyInfo(
                    id=nearest.id,
                    distance=nearest.distance_to_player,
                    bearing_deg=bearing,
                    has_los=nearest.has_line_of_sight_to_player,
                    health=nearest.health,
                    awareness=nearest.awareness_level
                )
                
                # Compute threat level
                features.threat_level = self._compute_threat_level(
                    enemies,
                    self.player
                )
                
                # Compute escape vector
                features.escape_vector = self._compute_escape_vector(
                    self.player.pos,
                    [e.pos for e in enemies]
                )
            
            # Stealth danger
            if self.player.sneaking:
                features.is_player_in_stealth_danger = self._check_stealth_danger(
                    self.player,
                    enemies
                )
                features.stealth_safety_score = self._compute_stealth_safety(
                    self.player,
                    enemies
                )
            
            # Cover analysis
            if self.cover_spots and features.nearest_enemy:
                features.best_cover_spot = self._find_best_cover(
                    self.player.pos,
                    self.player.facing_yaw,
                    features.nearest_enemy.id
                )
            
            # Loot opportunities
            containers = [obj for obj in self.objects.values() 
                         if obj.type == 'container' and not obj.is_locked]
            
            if containers and features.threat_level < 0.3:
                nearest_container = min(containers, 
                                       key=lambda c: self._distance_3d(self.player.pos, c.pos))
                features.loot_opportunity_available = True
                features.nearest_loot_distance = self._distance_3d(
                    self.player.pos,
                    nearest_container.pos
                )
            
            self.current_features = features
            self.total_features_computed += 1
            
            return features
        
        except Exception as e:
            logger.error(f"[GWM] Feature computation error: {e}")
            return GameWorldFeatures(timestamp=time.time())
    
    def _compute_threat_level(self, enemies: List[NPCState], player: PlayerState) -> float:
        """Compute overall threat level (0-1)."""
        if not enemies:
            return 0.0
        
        threat = 0.0
        
        # Number of enemies (saturates at 5)
        threat += min(len(enemies) / 5.0, 1.0) * 0.3
        
        # Enemies with LOS
        enemies_with_los = sum(1 for e in enemies if e.has_line_of_sight_to_player)
        threat += min(enemies_with_los / 3.0, 1.0) * 0.3
        
        # Proximity (nearest enemy)
        nearest_dist = min(e.distance_to_player for e in enemies)
        proximity_threat = max(0, 1.0 - nearest_dist / 20.0)  # 20m = no threat
        threat += proximity_threat * 0.2
        
        # Player health (low health = higher threat)
        if player.health < 0.5:
            threat += (1.0 - player.health) * 0.2
        
        return min(threat, 1.0)
    
    def _compute_escape_vector(
        self,
        player_pos: Tuple[float, float, float],
        enemy_positions: List[Tuple[float, float, float]]
    ) -> Tuple[float, float]:
        """Compute 2D escape vector (away from enemies)."""
        if not enemy_positions:
            return (0.0, 0.0)
        
        # Compute repulsion from each enemy
        escape_x, escape_y = 0.0, 0.0
        
        for enemy_pos in enemy_positions:
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                # Weight by proximity
                weight = 1.0 / max(dist, 1.0)
                escape_x += (dx / dist) * weight
                escape_y += (dy / dist) * weight
        
        # Normalize
        mag = math.sqrt(escape_x**2 + escape_y**2)
        if mag > 0:
            escape_x /= mag
            escape_y /= mag
        
        return (escape_x, escape_y)
    
    def _check_stealth_danger(self, player: PlayerState, enemies: List[NPCState]) -> bool:
        """Check if player is in stealth danger."""
        if not player.sneaking:
            return False
        
        # Danger if any enemy is close + aware
        for enemy in enemies:
            if enemy.distance_to_player < 5.0 and enemy.awareness_level > 0.6:
                return True
        
        return False
    
    def _compute_stealth_safety(self, player: PlayerState, enemies: List[NPCState]) -> float:
        """Compute stealth safety score (0-1)."""
        if not player.sneaking or not enemies:
            return 1.0
        
        safety = 1.0
        
        for enemy in enemies:
            if enemy.distance_to_player < 15.0:
                # Reduce safety based on proximity and awareness
                proximity_factor = 1.0 - (enemy.distance_to_player / 15.0)
                awareness_factor = enemy.awareness_level
                danger = proximity_factor * awareness_factor * 0.3
                safety -= danger
        
        return max(safety, 0.0)
    
    def _find_best_cover(
        self,
        player_pos: Tuple[float, float, float],
        player_facing: float,
        nearest_enemy_id: str
    ) -> Optional[CoverSpot]:
        """Find best cover spot between player and nearest enemy."""
        if not self.cover_spots:
            return None
        
        # Compute distances and bearings
        best_cover = None
        best_score = -999.0
        
        for cover in self.cover_spots.values():
            dist = self._distance_3d(player_pos, cover.pos)
            cover.distance_to_player = dist
            cover.bearing_deg = self._compute_bearing(player_pos, player_facing, cover.pos)
            
            # Score: closer is better, higher cover rating is better
            score = cover.cover_rating - (dist / 10.0)
            
            if score > best_score:
                best_score = score
                best_cover = cover
        
        return best_cover
    
    def _compute_bearing(
        self,
        from_pos: Tuple[float, float, float],
        facing_yaw: float,
        to_pos: Tuple[float, float, float]
    ) -> float:
        """Compute bearing from one position to another (relative to facing)."""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        # Angle to target
        angle_to_target = math.degrees(math.atan2(dy, dx))
        
        # Relative to facing
        relative_bearing = angle_to_target - facing_yaw
        
        # Normalize to [-180, 180]
        while relative_bearing > 180:
            relative_bearing -= 360
        while relative_bearing < -180:
            relative_bearing += 360
        
        return relative_bearing
    
    def _distance_3d(
        self,
        pos1: Tuple[float, float, float],
        pos2: Tuple[float, float, float]
    ) -> float:
        """Compute 3D Euclidean distance."""
        return math.sqrt(
            (pos1[0] - pos2[0])**2 +
            (pos1[1] - pos2[1])**2 +
            (pos1[2] - pos2[2])**2
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics."""
        return {
            'total_updates': self.total_updates,
            'total_features_computed': self.total_features_computed,
            'num_entities': {
                'npcs': len(self.npcs),
                'objects': len(self.objects),
                'cover_spots': len(self.cover_spots)
            },
            'snapshot_age': time.time() - self.last_snapshot_time,
            'has_player': self.player is not None,
            'history_size': len(self.snapshot_history)
        }
