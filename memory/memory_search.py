import os
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from rapidfuzz import fuzz
import requests
import numpy as np
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARN] FAISS not available. Vector search will be disabled.")


class MemorySearch:
    """
    Enhanced Memory Search with caching, incremental loading, question word indexing,
    vector embeddings, and memory prioritization.
    """
    def __init__(
        self, 
        logs_path: str = "memory/session_logs",
        cache_ttl: int = 300,  # 5 minutes default cache TTL
        days_back: int = 30,  # Load only last 30 days by default
        enable_vector_search: bool = True,
        embedding_url: str = "http://localhost:11434/api/embeddings",
        embedding_model: str = "nomic-embed-text"
    ):
        self.logs_path = Path(logs_path)
        self.cache_ttl = cache_ttl
        self.days_back = days_back
        self.enable_vector_search = enable_vector_search and FAISS_AVAILABLE
        
        # Caching
        self._cache = None
        self._cache_timestamp = None
        self._cache_file_timestamps = {}  # Track file modification times
        
        # Question word indexing
        self._question_word_index = {
            "what": [],
            "who": [],
            "where": [],
            "when": [],
            "why": [],
            "how": []
        }
        self._indexed = False
        
        # Vector embeddings
        self.embedding_url = embedding_url
        self.embedding_model = embedding_model
        self.vector_index = None
        self.vector_entries = []  # Parallel array to vector_index
        self._vectors_built = False
        
        # Memory prioritization
        self._usage_stats = {}  # Track usage counts per memory entry

    def search_memory(
        self, 
        user_query: str, 
        top_k: int = 3, 
        skip_load: bool = False,
        use_vector_search: bool = True
    ) -> List[Dict]:
        """
        Enhanced search memory with fuzzy matching, vector search, and prioritization.
        
        Args:
            user_query: Query to search for
            top_k: Number of top results to return
            skip_load: If True, skip loading JSON files (for simple math queries)
            use_vector_search: If True, use vector embeddings for semantic search
        
        Returns:
            List of matching memory entries, prioritized by relevance and usage
        """
        if skip_load:
            return []
        
        # Load and index memory entries
        memory_entries = self._load_queries(silent=False)
        
        if not memory_entries:
            return []
        
        # Build indices if not already built
        if not self._indexed:
            self._build_question_word_index(memory_entries)
            self._indexed = True
        
        # Build vector index if enabled and not built
        if self.enable_vector_search and use_vector_search and not self._vectors_built:
            self._build_vector_index(memory_entries)
            self._vectors_built = True
        
        user_query_lower = user_query.lower().strip()
        scored_results = []
        
        # Try question word indexing first (faster lookup)
        question_word = self._detect_question_word(user_query_lower)
        candidate_entries = memory_entries
        
        if question_word and self._question_word_index.get(question_word):
            # Use indexed entries for faster search
            indexed_entries = self._question_word_index[question_word]
            candidate_entries = [e for e in memory_entries if e in indexed_entries]
            if not candidate_entries:
                candidate_entries = memory_entries  # Fallback to all entries
        
        # Hybrid search: Combine fuzzy matching with vector search
        for entry in candidate_entries:
            entry_id = self._get_entry_id(entry)
            entry_query_lower = entry["query"].lower().strip()
            
            # Fuzzy matching scores
            query_ratio = fuzz.ratio(user_query_lower, entry_query_lower)
            query_partial = fuzz.partial_ratio(user_query_lower, entry_query_lower)
            
            # Number matching for math queries
            user_numbers = set(re.findall(r'\d+', user_query))
            entry_numbers = set(re.findall(r'\d+', entry["query"]))
            number_match = len(user_numbers & entry_numbers) / max(len(user_numbers), 1) if user_numbers else 0
            
            if user_numbers and entry_numbers:
                if not user_numbers.issubset(entry_numbers) and not entry_numbers.issubset(user_numbers):
                    number_match = 0
            
            # Skip low similarity matches
            if query_ratio < 70 and query_partial < 80:
                continue
            
            summary_score = fuzz.partial_ratio(user_query_lower, entry["solution_summary"].lower())
            length_penalty = len(entry["solution_summary"]) / 100
            
            # Base fuzzy score
            fuzzy_score = (0.6 * query_ratio + 0.2 * query_partial + 0.1 * summary_score + 0.1 * number_match * 100) - 0.05 * length_penalty
            
            # Vector similarity score (if available)
            vector_score = 0.0
            if self.enable_vector_search and use_vector_search and self.vector_index is not None:
                try:
                    query_embedding = self._get_embedding(user_query)
                    if query_embedding is not None:
                        # Find entry in vector_entries - optimized with dict lookup
                        entry_idx = None
                        # Build lookup dict once if not exists
                        if not hasattr(self, '_entry_id_to_idx'):
                            self._entry_id_to_idx = {
                                self._get_entry_id(vec_entry): idx
                                for idx, vec_entry in enumerate(self.vector_entries)
                            }
                        entry_idx = self._entry_id_to_idx.get(entry_id)
                        
                        if entry_idx is not None:
                            # Get embedding from index
                            entry_embedding = self.vector_index.reconstruct(entry_idx).reshape(1, -1)
                            query_vec = query_embedding.reshape(1, -1)
                            # Calculate cosine similarity
                            similarity = np.dot(query_vec, entry_embedding.T) / (
                                np.linalg.norm(query_vec) * np.linalg.norm(entry_embedding)
                            )
                            vector_score = float(similarity[0][0]) * 100  # Scale to 0-100
                except Exception as e:
                    # Vector search failed, continue with fuzzy only
                    pass
            
            # Memory prioritization: Boost frequently used entries
            usage_boost = 0.0
            if entry_id in self._usage_stats:
                usage_count = self._usage_stats[entry_id].get("count", 0)
                usage_boost = min(usage_count * 2, 10)  # Max 10 point boost
            
            # Priority boost (if entry has priority field)
            priority_boost = 0.0
            if "memory_priority" in entry:
                priority_map = {"high": 5, "medium": 2, "low": 0}
                priority_boost = priority_map.get(entry["memory_priority"], 0)
            
            # Combined score: 60% fuzzy, 30% vector (if available), 10% usage/priority
            if vector_score > 0:
                final_score = 0.6 * fuzzy_score + 0.3 * vector_score + 0.05 * usage_boost + 0.05 * priority_boost
            else:
                final_score = fuzzy_score + 0.1 * usage_boost + 0.1 * priority_boost
            
            scored_results.append((final_score, entry))
        
        # Sort by score and return top K - optimized with heapq for large lists
        if len(scored_results) > top_k * 2:
            # Use heapq for better performance on large lists
            import heapq
            top_matches = heapq.nlargest(top_k, scored_results, key=lambda x: x[0])
        else:
            # Use sorted for small lists (more efficient for small N)
            top_matches = sorted(scored_results, key=lambda x: x[0], reverse=True)[:top_k]
        # Filter and extract matches in one pass
        filtered_matches = [match[1] for match in top_matches if match[0] > 60]
        
        # Update usage statistics
        for match in filtered_matches:
            entry_id = self._get_entry_id(match)
            if entry_id not in self._usage_stats:
                self._usage_stats[entry_id] = {"count": 0, "last_used": None}
            self._usage_stats[entry_id]["count"] += 1
            self._usage_stats[entry_id]["last_used"] = datetime.now().isoformat()
        
        return filtered_matches

    def _load_queries(self, silent: bool = False) -> List[Dict]:
        """
        Load queries from JSON files with caching and incremental loading.
        
        Args:
            silent: If True, suppress print statements (for performance)
        
        Returns:
            List of memory entries
        """
        # Check cache first
        if self._cache and self._cache_timestamp:
            cache_age = time.time() - self._cache_timestamp
            if cache_age < self.cache_ttl:
                # Check if files have changed
                files_changed = self._check_files_changed()
                if not files_changed:
                    if not silent:
                        print(f"[CACHE] Using cached memory entries (age: {cache_age:.1f}s)")
                    return self._cache
        
        # Load from files (with incremental loading)
        memory_entries = []
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        
        all_json_files = list(self.logs_path.rglob("*.json"))
        if not silent:
            print(f"[SEARCH] Found {len(all_json_files)} JSON file(s) in '{self.logs_path}'")
            print(f"[SEARCH] Loading sessions from last {self.days_back} days (since {cutoff_date.date()})")

        for file in all_json_files:
            # Incremental loading: Skip files older than days_back
            try:
                file_date = datetime.fromtimestamp(file.stat().st_mtime)
                if file_date < cutoff_date:
                    continue
            except Exception:
                pass  # If we can't get file date, include it anyway
            
            # Track file modification time for cache invalidation
            self._cache_file_timestamps[str(file)] = file.stat().st_mtime
            
            count_before = len(memory_entries)
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                if isinstance(content, list):  # FORMAT 1
                    for session in content:
                        self._extract_entry(session, file.name, memory_entries, silent)
                elif isinstance(content, dict) and "session_id" in content:  # FORMAT 2
                    self._extract_entry(content, file.name, memory_entries, silent)
                elif isinstance(content, dict) and "turns" in content:  # FORMAT 3
                    for turn in content["turns"]:
                        self._extract_entry(turn, file.name, memory_entries, silent)

            except Exception as e:
                if not silent:
                    print(f"[WARN] Skipping '{file}': {e}")
                continue

            count_after = len(memory_entries)
            if count_after > count_before and not silent:
                print(f"[OK] {file.name}: {count_after - count_before} matching entries")

        if not silent:
            print(f"[INFO] Total usable memory entries collected: {len(memory_entries)}\n")
        
        # Cache results
        self._cache = memory_entries
        self._cache_timestamp = time.time()
        
        return memory_entries
    
    def _check_files_changed(self) -> bool:
        """Check if any JSON files have been modified since cache was created."""
        for file_path_str, cached_mtime in self._cache_file_timestamps.items():
            try:
                file_path = Path(file_path_str)
                if file_path.exists():
                    current_mtime = file_path.stat().st_mtime
                    if current_mtime > cached_mtime:
                        return True
            except Exception:
                pass
        return False
    
    def _detect_question_word(self, query: str) -> Optional[str]:
        """Detect question word at start of query."""
        question_words = ["what", "who", "where", "when", "why", "how"]
        for word in question_words:
            if query.startswith(word + " "):
                return word
        return None
    
    def _build_question_word_index(self, memory_entries: List[Dict]):
        """Build index of memory entries by question word."""
        self._question_word_index = {word: [] for word in ["what", "who", "where", "when", "why", "how"]}
        
        for entry in memory_entries:
            query_lower = entry["query"].lower().strip()
            question_word = self._detect_question_word(query_lower)
            if question_word:
                self._question_word_index[question_word].append(entry)
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text using Ollama."""
        try:
            response = requests.post(
                self.embedding_url,
                json={"model": self.embedding_model, "prompt": text},
                timeout=5.0
            )
            response.raise_for_status()
            embedding = np.array(response.json()["embedding"], dtype=np.float32)
            return embedding
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ConnectionRefusedError) as e:
            # Embedding service unavailable (Ollama not running), return None gracefully
            # Don't print error for every call - only log once
            if not hasattr(self, '_embedding_warning_logged'):
                print(f"[WARN] Embedding service unavailable (Ollama may not be running). Vector search disabled.")
                self._embedding_warning_logged = True
            return None
        except Exception as e:
            # Other errors - return None gracefully
            return None
    
    def _build_vector_index(self, memory_entries: List[Dict]):
        """Build FAISS vector index for semantic search."""
        if not self.enable_vector_search:
            return
        
        try:
            embeddings = []
            self.vector_entries = []
            
            for entry in memory_entries:
                # Create text representation for embedding
                text = f"{entry['query']} {entry.get('solution_summary', '')}"
                embedding = self._get_embedding(text)
                
                if embedding is not None:
                    embeddings.append(embedding)
                    self.vector_entries.append(entry)
                # If embedding is None (service unavailable), skip this entry gracefully
                # Vector search will be disabled if no embeddings are available
            
            if embeddings:
                embeddings_array = np.stack(embeddings).astype('float32')
                dimension = embeddings_array.shape[1]
                
                # Create FAISS index
                self.vector_index = faiss.IndexFlatL2(dimension)
                self.vector_index.add(embeddings_array)
                print(f"[VECTOR] Built FAISS index with {len(embeddings)} entries (dim={dimension})")
        except Exception as e:
            print(f"[WARN] Failed to build vector index: {e}")
            self.vector_index = None
    
    def _get_entry_id(self, entry: Dict) -> str:
        """Generate unique ID for memory entry."""
        return f"{entry.get('file', '')}:{entry.get('query', '')}"

    def _extract_entry(self, obj: dict, file_name: str, memory_entries: List[Dict], silent: bool = False):
        """Extract memory entry from session log JSON."""
        try:
            # New session log format (Assign11)
            if isinstance(obj, dict):
                # Check for new format: has original_query and state_snapshot
                if "original_query" in obj and "state_snapshot" in obj:
                    query = obj.get("original_query", "")
                    state_snapshot = obj.get("state_snapshot", {})
                    final_answer = state_snapshot.get("final_answer", "")
                    
                    if query and final_answer:
                        if not silent:
                            print(f"[OK] Extracted (new format): {query[:40]} -> {final_answer[:40]}")
                        memory_entries.append({
                            "file": file_name,
                            "query": query,
                            "result_requirement": "",
                            "solution_summary": final_answer
                        })
                        return
                
                # Old format: has original_goal_achieved
                if obj.get("original_goal_achieved") is True:
                    query = obj.get("query") or obj.get("original_query", "")
                    summary = obj.get("solution_summary", "") or obj.get("final_answer", "")
                    
                    if query and summary:
                        if not silent:
                            print(f"[OK] Extracted (old format): {query[:40]} -> {summary[:40]}")
                        memory_entries.append({
                            "file": file_name,
                            "query": query,
                            "result_requirement": obj.get("result_requirement", ""),
                            "solution_summary": summary
                        })
                        return
                
                # Recursive search for nested structures
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        self._extract_entry(v, file_name, memory_entries, silent)
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        self._extract_entry(item, file_name, memory_entries, silent)
        
        except Exception as e:
            if not silent:
                print(f"[ERROR] Error parsing {file_name}: {e}")


if __name__ == "__main__":
    searcher = MemorySearch()
    query = input("Enter your query: ").strip()
    results = searcher.search_memory(query)

    if not results:
        print("[ERROR] No matching memory entries found.")
    else:
        print("\n[TOP MATCHES]:\n")
        for i, res in enumerate(results, 1):
            print(f"[{i}] File: {res['file']}\nQuery: {res['query']}\nResult Requirement: {res['result_requirement']}\nSummary: {res['solution_summary']}\n")
