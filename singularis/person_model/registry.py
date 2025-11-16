"""
Person Registry - Manage active PersonModels

Tracks all active agents in the game world.
"""

from typing import Dict, Optional, List
from loguru import logger

from .types import PersonModel


class PersonRegistry:
    """
    Registry for all active PersonModels.
    
    Provides lookup by person_id, archetype, roles, etc.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._persons: Dict[str, PersonModel] = {}
        logger.info("[PersonRegistry] Initialized")
    
    def add(self, person: PersonModel):
        """
        Add a PersonModel to registry.
        
        Args:
            person: PersonModel to add
        """
        person_id = person.identity.person_id
        
        if person_id in self._persons:
            logger.warning(f"[PersonRegistry] Overwriting existing person: {person_id}")
        
        self._persons[person_id] = person
        logger.info(f"[PersonRegistry] Added: {person.identity.name} ({person_id})")
    
    def get(self, person_id: str) -> Optional[PersonModel]:
        """
        Get PersonModel by ID.
        
        Args:
            person_id: Person ID to look up
        
        Returns:
            PersonModel or None if not found
        """
        return self._persons.get(person_id)
    
    def remove(self, person_id: str) -> bool:
        """
        Remove PersonModel from registry.
        
        Args:
            person_id: Person ID to remove
        
        Returns:
            True if removed, False if not found
        """
        if person_id in self._persons:
            person = self._persons.pop(person_id)
            logger.info(f"[PersonRegistry] Removed: {person.identity.name} ({person_id})")
            return True
        return False
    
    def all(self) -> List[PersonModel]:
        """Get all PersonModels."""
        return list(self._persons.values())
    
    def get_by_archetype(self, archetype: str) -> List[PersonModel]:
        """
        Get all PersonModels with specific archetype.
        
        Args:
            archetype: Archetype to filter by
        
        Returns:
            List of matching PersonModels
        """
        return [p for p in self._persons.values() 
                if p.identity.archetype == archetype]
    
    def get_by_role(self, role: str) -> List[PersonModel]:
        """
        Get all PersonModels with specific role.
        
        Args:
            role: Role to filter by (e.g., "companion", "enemy")
        
        Returns:
            List of matching PersonModels
        """
        return [p for p in self._persons.values() 
                if role in p.identity.roles]
    
    def get_companions(self) -> List[PersonModel]:
        """Get all companions."""
        return self.get_by_role("companion")
    
    def get_enemies(self) -> List[PersonModel]:
        """Get all enemies."""
        return self.get_by_role("enemy")
    
    def count(self) -> int:
        """Get total number of registered persons."""
        return len(self._persons)
    
    def clear(self):
        """Clear all PersonModels from registry."""
        count = len(self._persons)
        self._persons.clear()
        logger.info(f"[PersonRegistry] Cleared {count} persons")
    
    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics."""
        archetypes = {}
        roles = {}
        
        for person in self._persons.values():
            # Count archetypes
            arch = person.identity.archetype
            archetypes[arch] = archetypes.get(arch, 0) + 1
            
            # Count roles
            for role in person.identity.roles:
                roles[role] = roles.get(role, 0) + 1
        
        return {
            'total_persons': len(self._persons),
            'archetypes': archetypes,
            'roles': roles
        }


# Global registry instance
_global_registry = PersonRegistry()


def get_global_registry() -> PersonRegistry:
    """Get the global PersonRegistry instance."""
    return _global_registry
