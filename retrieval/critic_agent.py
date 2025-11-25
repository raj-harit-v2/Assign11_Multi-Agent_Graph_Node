"""
Critic Agent for Session 11
Scores retrieval sources for quality and relevance.
"""

from typing import List, Dict, Any


class CriticAgent:
    """Agent for scoring retrieval sources."""
    
    def score(self, sources: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Calculate quality scores for retrieval sources.
        
        Args:
            sources: List of source dictionaries
            query: Original query
        
        Returns:
            Scoring dictionary with metrics
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        scored_sources = []
        total_confidence = 0.0
        total_match = 0.0
        total_evidence = 0.0
        
        for source in sources:
            # Calculate source_confidence_score
            source_confidence = source.get("score", 0.5)
            
            # Calculate match_score (term overlap)
            source_text = ""
            if "query" in source:
                source_text += source["query"].lower()
            if "solution_summary" in source:
                source_text += " " + source["solution_summary"].lower()
            
            source_terms = set(source_text.split())
            match_score = len(query_terms & source_terms) / max(len(query_terms), 1)
            
            # Calculate supporting_evidence_score
            evidence_score = 0.5
            if source.get("solution_summary"):
                evidence_score = 0.8
            if source.get("result_requirement"):
                evidence_score = 0.9
            
            scored_source = {
                **source,
                "source_confidence_score": source_confidence,
                "match_score": match_score,
                "supporting_evidence_score": evidence_score
            }
            scored_sources.append(scored_source)
            
            total_confidence += source_confidence
            total_match += match_score
            total_evidence += evidence_score
        
        count = len(sources) if sources else 1
        
        return {
            "sources": scored_sources,
            "average_source_confidence": total_confidence / count,
            "average_match_score": total_match / count,
            "average_evidence_score": total_evidence / count,
            "total_sources": len(sources)
        }

