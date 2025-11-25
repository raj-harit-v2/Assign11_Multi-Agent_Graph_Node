"""
Graph Agent for Session 11
Manages knowledge graph operations.
"""

from typing import List, Dict, Any, Optional


class GraphAgent:
    """Agent for knowledge graph operations."""
    
    def __init__(self):
        """Initialize graph agent with in-memory graph storage."""
        # Simple in-memory graph storage
        # In production, this would use a proper graph database
        self.triplets = []  # List of (subject, predicate, object) tuples
        self.entities = {}  # Entity -> List of connections
    
    def upsert_triplets(self, triplets: List[Dict[str, Any]]) -> bool:
        """
        Store triplets in knowledge graph.
        
        Args:
            triplets: List of triplet dictionaries
        
        Returns:
            True if successful
        """
        for triplet in triplets:
            subject = triplet.get("subject", "")
            predicate = triplet.get("predicate", "")
            obj = triplet.get("object", "")
            
            if subject and predicate and obj:
                # Store triplet
                self.triplets.append((subject, predicate, obj))
                
                # Update entity connections
                if subject not in self.entities:
                    self.entities[subject] = []
                self.entities[subject].append((predicate, obj))
        
        return True
    
    def query(self, entity_or_path: str) -> List[Dict[str, Any]]:
        """
        Query knowledge graph for entities or paths.
        
        Args:
            entity_or_path: Entity name or path pattern
        
        Returns:
            List of matching paths/entities
        """
        results = []
        
        # Search for entity
        if entity_or_path in self.entities:
            connections = self.entities[entity_or_path]
            for predicate, obj in connections:
                results.append({
                    "path": f"{entity_or_path} -> {predicate} -> {obj}",
                    "entities": [entity_or_path, obj],
                    "predicate": predicate,
                    "confidence": 0.8
                })
        
        # Search in triplets
        for subject, predicate, obj in self.triplets:
            if entity_or_path.lower() in subject.lower() or \
               entity_or_path.lower() in obj.lower():
                results.append({
                    "path": f"{subject} -> {predicate} -> {obj}",
                    "entities": [subject, obj],
                    "predicate": predicate,
                    "confidence": 0.7
                })
        
        return results

