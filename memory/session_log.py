import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


def _detect_question_type(query: str) -> str:
    """Detect question type from query."""
    query_lower = query.lower().strip()
    question_words = ["what", "who", "where", "when", "why", "how"]
    for word in question_words:
        if query_lower.startswith(word + " "):
            return word
    return "unknown"


def _detect_question_category(query: str) -> str:
    """Detect question category (geography, science, math, etc.)."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["capital", "country", "city", "continent", "ocean", "mountain"]):
        return "geography"
    elif any(word in query_lower for word in ["formula", "chemical", "element", "molecule", "atom"]):
        return "science"
    elif any(word in query_lower for word in ["calculate", "sum", "average", "multiply", "divide", "factorial"]):
        return "math"
    elif any(word in query_lower for word in ["wrote", "author", "book", "poem", "novel"]):
        return "literature"
    elif any(word in query_lower for word in ["year", "date", "when", "history", "war", "battle"]):
        return "history"
    elif any(word in query_lower for word in ["animal", "plant", "organ", "cell", "species"]):
        return "biology"
    else:
        return "general"


def _extract_entities(query: str) -> List[str]:
    """Extract entities from query (simplified)."""
    # Simple entity extraction - can be enhanced with NER
    entities = []
    # Look for capitalized words (potential entities)
    words = query.split()
    for word in words:
        if word[0].isupper() and len(word) > 1:
            entities.append(word.strip('.,!?'))
    return entities[:5]  # Limit to 5 entities


def _detect_intent(query: str) -> str:
    """Detect user intent."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["what is", "what are", "definition", "meaning"]):
        return "factual_inquiry"
    elif any(word in query_lower for word in ["calculate", "compute", "find", "solve"]):
        return "calculation"
    elif any(word in query_lower for word in ["who", "wrote", "created", "invented"]):
        return "attribution"
    elif any(word in query_lower for word in ["where", "located", "found"]):
        return "location"
    elif any(word in query_lower for word in ["when", "year", "date"]):
        return "temporal"
    else:
        return "general_query"


def get_store_path(session_id: str, base_dir: str = "memory/session_logs") -> Path:
    """
    Construct the full path to the session file based on current date and session ID.
    Format: memory/session_logs/YYYY/MM/DD/<session_id>.json
    """
    now = datetime.now()
    day_dir = Path(base_dir) / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{session_id}.json"
    return day_dir / filename


def simplify_session_id(session_id: str) -> str:
    """
    Return the simplified (short) version of the session ID for display/logging.
    """
    return session_id.split("-")[0]


def _enhance_session_data(session_data: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhance session data with metadata for better searchability.
    
    Adds:
    - metadata: question_type, question_category, entities, intent
    - memory_used: search statistics
    - decision_factors: question words, tool selection
    - result: final answer metadata
    """
    # Extract query if not provided
    if not query:
        query = session_data.get("query") or session_data.get("original_query", "")
    
    # Add metadata
    session_data["metadata"] = {
        "question_type": _detect_question_type(query),
        "question_category": _detect_question_category(query),
        "entities": _extract_entities(query),
        "intent": _detect_intent(query),
        "timestamp": datetime.now().isoformat() + "Z"
    }
    
    # Add memory_used if available
    if "memory_results" in session_data or "memory_search" in session_data:
        memory_info = session_data.get("memory_search", {})
        session_data["memory_used"] = {
            "searched": True,
            "matches_found": memory_info.get("results_count", 0),
            "top_match_score": memory_info.get("top_match_score", 0.0)
        }
    else:
        session_data["memory_used"] = {
            "searched": False,
            "matches_found": 0,
            "top_match_score": 0.0
        }
    
    # Add decision_factors
    question_type = session_data["metadata"]["question_type"]
    tools_used = []
    
    # Extract tools from plan_versions or execution
    if "plan_versions" in session_data:
        for plan in session_data["plan_versions"]:
            for step in plan.get("steps", []):
                if step.get("code") and isinstance(step["code"], dict):
                    tool_name = step["code"].get("tool_name")
                    if tool_name:
                        tools_used.append(tool_name)
    
    session_data["decision_factors"] = {
        "used_question_words": [question_type] if question_type != "unknown" else [],
        "tool_selected": tools_used[0] if tools_used else "none",
        "reason": "information_query_detected" if question_type != "unknown" else "general_query"
    }
    
    # Add result metadata
    final_answer = session_data.get("state_snapshot", {}).get("final_answer") or session_data.get("final_answer")
    confidence = session_data.get("state_snapshot", {}).get("confidence") or session_data.get("confidence", "0.0")
    
    session_data["result"] = {
        "final_answer": final_answer,
        "confidence": float(confidence) if isinstance(confidence, (str, float)) else 0.0,
        "source": "web_search" if "duckduckgo" in str(tools_used).lower() else "computation" if any("add" in t or "multiply" in t for t in tools_used) else "memory" if session_data["memory_used"]["searched"] else "unknown"
    }
    
    # Add memory prioritization fields
    session_data["memory_priority"] = "high" if session_data["result"]["confidence"] > 0.9 else "medium" if session_data["result"]["confidence"] > 0.7 else "low"
    session_data["relevance_score"] = session_data["result"]["confidence"]
    session_data["usage_count"] = 0  # Will be updated by MemorySearch
    session_data["last_used"] = None  # Will be updated by MemorySearch
    
    return session_data


def append_session_to_store(session_obj, base_dir: str = "memory/session_logs", enhance: bool = True) -> None:
    """
    Save the session object as a standalone file with enhanced metadata.
    If a file already exists and is corrupt, it will be overwritten with fresh data.
    
    Args:
        session_obj: Session object with to_json() method
        base_dir: Base directory for session logs
        enhance: If True, add enhanced metadata (default: True)
    """
    session_data = session_obj.to_json()
    session_data["_session_id_short"] = simplify_session_id(session_data["session_id"])

    # Enhance with metadata
    if enhance:
        query = session_data.get("query") or session_data.get("original_query", "")
        session_data = _enhance_session_data(session_data, query)

    store_path = get_store_path(session_data["session_id"], base_dir)

    if store_path.exists():
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                existing = f.read().strip()
                if existing:
                    json.loads(existing)  # verify valid JSON
        except json.JSONDecodeError:
            print(f"[WARN] Warning: Corrupt JSON detected in {store_path}. Overwriting.")

    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    print(f"[OK] Session stored: {store_path}")


def live_update_session(session_obj, base_dir: str = "memory/session_logs") -> None:
    """
    Update (or overwrite) the session file with latest data.
    In per-file format, this is identical to append.
    """
    try:
        append_session_to_store(session_obj, base_dir)
        print("[OK] Session live-updated.")
    except Exception as e:
        print(f"[ERROR] Failed to update session: {e}")
