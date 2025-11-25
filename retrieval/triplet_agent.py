"""
Triplet Agent for Session 11
Extracts (subject, predicate, object) triplets from text.
"""

from typing import List, Dict, Any
import re


class TripletAgent:
    """Agent for extracting knowledge triplets from text."""
    
    def extract_triplets(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract (subject, predicate, object) triplets from text.
        
        Args:
            text: Text to extract triplets from
        
        Returns:
            List of triplets with confidence scores
        """
        triplets = []
        
        # Simple pattern-based extraction
        # In production, this would use NLP models
        
        # Pattern: "X is Y", "X has Y", "X does Y", etc.
        patterns = [
            (r"(\w+(?:\s+\w+)*)\s+is\s+(\w+(?:\s+\w+)*)", "is"),
            (r"(\w+(?:\s+\w+)*)\s+has\s+(\w+(?:\s+\w+)*)", "has"),
            (r"(\w+(?:\s+\w+)*)\s+does\s+(\w+(?:\s+\w+)*)", "does"),
            (r"(\w+(?:\s+\w+)*)\s+located\s+in\s+(\w+(?:\s+\w+)*)", "located_in"),
            (r"(\w+(?:\s+\w+)*)\s+created\s+(\w+(?:\s+\w+)*)", "created"),
        ]
        
        for pattern, predicate in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                obj = match.group(2).strip()
                
                triplets.append({
                    "subject": subject,
                    "predicate": predicate,
                    "object": obj,
                    "confidence": 0.7  # Base confidence for pattern matching
                })
        
        return triplets

