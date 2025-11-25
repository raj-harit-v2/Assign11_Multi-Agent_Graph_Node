"""
Retriever Agent for Session 11
Hybrid retrieval using vector search and knowledge graph.
"""

from typing import Dict, List, Any
from core.context_manager import ContextManager
from memory.memory_search import MemorySearch


class RetrieverAgent:
    """Agent for hybrid retrieval (vector + knowledge graph)."""
    
    def __init__(self, graph_agent=None):
        """
        Initialize retriever agent.
        
        Args:
            graph_agent: Optional GraphAgent instance for KG queries
        """
        self.memory_search = MemorySearch()
        self.graph_agent = graph_agent
    
    def retrieve(self, query: str, context: ContextManager) -> Dict[str, Any]:
        """
        Perform hybrid retrieval: vector search + knowledge graph.
        
        Args:
            query: Search query
            context: ContextManager for tracking
        
        Returns:
            Dict with sources, scores, and evidence
        """
        # Vector search
        vector_results = self.retrieve_vector(query)
        
        # Graph search (if available)
        graph_results = []
        if self.graph_agent:
            graph_results = self.retrieve_graph(query, self.graph_agent)
        
        # Combine results
        all_sources = vector_results + graph_results
        
        return {
            "sources": all_sources,
            "vector_count": len(vector_results),
            "graph_count": len(graph_results),
            "total_count": len(all_sources)
        }
    
    def retrieve_vector(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform vector-based retrieval using FAISS.
        
        Args:
            query: Search query
        
        Returns:
            List of retrieved documents with metadata
        """
        results = self.memory_search.search_memory(query)
        
        formatted_results = []
        for i, res in enumerate(results):
            formatted_results.append({
                "source": "vector",
                "rank": i + 1,
                "file": res.get("file", ""),
                "query": res.get("query", ""),
                "result_requirement": res.get("result_requirement", ""),
                "solution_summary": res.get("solution_summary", ""),
                "score": 1.0 - (i * 0.1)  # Simple ranking score
            })
        
        return formatted_results
    
    def retrieve_graph(self, query: str, kg_agent) -> List[Dict[str, Any]]:
        """
        Perform knowledge graph-based retrieval.
        
        Args:
            query: Search query
            kg_agent: GraphAgent instance
        
        Returns:
            List of retrieved paths/entities from KG
        """
        if not kg_agent:
            return []
        
        # Extract entities from query (simple keyword extraction)
        # In production, this would use NER
        keywords = query.lower().split()
        
        results = []
        for keyword in keywords[:5]:  # Limit to 5 keywords
            kg_results = kg_agent.query(keyword)
            for result in kg_results:
                results.append({
                    "source": "graph",
                    "entity": keyword,
                    "path": result.get("path", ""),
                    "entities": result.get("entities", []),
                    "score": result.get("confidence", 0.5)
                })
        
        return results

