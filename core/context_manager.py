"""
Context Manager for Session 11 - Graph-Native Agent System
Manages execution context, globals, and full execution trace.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .plan_graph import PlanGraph, StepNode, StepStatus


@dataclass
class ContextManager:
    """Manages execution context for graph-native agent."""
    plan_graph: PlanGraph = field(default_factory=PlanGraph)
    globals_schema: Dict[str, Any] = field(default_factory=dict)
    failed_nodes: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    nodes_executed: List[str] = field(default_factory=list)

    def log(self, event: str, **kwargs):
        """Log an event to the execution history."""
        log_entry = {"event": event, **kwargs}
        self.history.append(log_entry)

    def register_step_result(
        self,
        node_id: str,
        success: bool,
        result: Any,
        globals_delta: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Register the result of a step execution."""
        node = self.plan_graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found in plan graph")
        
        # Update node status
        node.status = StepStatus.COMPLETED if success else StepStatus.FAILED
        node.error = error
        
        # Log the result
        self.log(
            "step_result",
            node_id=node_id,
            success=success,
            result=str(result) if result else None,
            error=error
        )
        
        # Track node execution
        if node_id not in self.nodes_executed:
            self.nodes_executed.append(node_id)
        
        # Handle failure
        if not success:
            if node_id not in self.failed_nodes:
                self.failed_nodes.append(node_id)
        
        # Update globals
        if globals_delta:
            self.update_globals(globals_delta)
            node.globals_delta = globals_delta

    def update_globals(self, updates: Dict[str, Any]):
        """Update the global state schema."""
        self.globals_schema.update(updates)
        self.log("globals_updated", updates=updates)

    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """Get the full execution trace history."""
        return self.history.copy()

    def get_nodes_executed(self) -> List[str]:
        """Get ordered list of node IDs that were executed."""
        return self.nodes_executed.copy()

    def get_globals_schema(self) -> Dict[str, Any]:
        """Get current global state schema."""
        return self.globals_schema.copy()

    def reset(self):
        """Reset the context manager (for testing)."""
        self.plan_graph = PlanGraph()
        self.globals_schema.clear()
        self.failed_nodes.clear()
        self.history.clear()
        self.nodes_executed.clear()

