"""
Agent Loop V2 for Session 11 - Graph-Native Agent System
Implements graph-based execution with code variants, fallbacks, and retrieval agents.
"""

import uuid
from typing import Optional
from perception.perception import Perception, PerceptionResult
from decision.decision import Decision
from action.executor import execute_step
from core.context_manager import ContextManager
from core.plan_graph import PlanGraph, Route, StepStatus
from memory.memory_search import MemorySearch
from mcp_servers.multiMCP import MultiMCP
from retrieval.retriever_agent import RetrieverAgent
from retrieval.triplet_agent import TripletAgent
from retrieval.graph_agent import GraphAgent
from retrieval.critic_agent import CriticAgent
from retrieval.formatter_agent import FormatterAgent


class AgentLoop:
    """V2 Graph-native agent loop with retrieval augmentation."""
    
    def __init__(self, perception_prompt_path: str, decision_prompt_path: str, multi_mcp: MultiMCP, strategy: str = "exploratory"):
        """
        Initialize V2 agent loop.
        
        Args:
            perception_prompt_path: Path to perception prompt file
            decision_prompt_path: Path to decision prompt file
            multi_mcp: MultiMCP instance
            strategy: Planning strategy
        """
        self.perception = Perception(perception_prompt_path)
        self.decision = Decision(decision_prompt_path, multi_mcp)
        self.strategy = strategy
        self.multi_mcp = multi_mcp
        
        # Initialize retrieval agents
        self.graph_agent = GraphAgent()
        self.retriever_agent = RetrieverAgent(graph_agent=self.graph_agent)
        self.triplet_agent = TripletAgent()
        self.critic_agent = CriticAgent()
        self.formatter_agent = FormatterAgent()
    
    async def run(self, query: str) -> str:
        """
        Run the graph-native agent loop.
        
        Args:
            query: User query
        
        Returns:
            Final answer string
        """
        print(f"\n=== V2 GRAPH-NATIVE AGENT SESSION ===")
        print(f"Query: {query}")
        
        # Initialize context manager
        ctx = ContextManager()
        
        # Step -1: Memory Search
        print(f"\nSearching Recent Conversation History")
        searcher = MemorySearch()
        memory_results = searcher.search_memory(query)
        if not memory_results:
            print("No matching memory entries found.")
        else:
            print(f"\nTop {len(memory_results)} Matches:")
            for i, res in enumerate(memory_results[:3], 1):
                print(f"[{i}] {res.get('query', '')[:50]}...")
        
        # Step 0: Root Perception
        print(f"\n[Perception] Analyzing root query...")
        p0 = self.perception.perceive_root(query, memory_results)
        ctx.log("root_perception", route=p0.route.value, goal_met=p0.goal_met)
        
        # If goal already met, summarize immediately
        if p0.route == Route.SUMMARIZE and p0.goal_met:
            print("Goal already achieved. Summarizing...")
            return self.formatter_agent.format_report(
                ctx.get_globals_schema(),
                p0.instruction_to_summarize
            )
        
        # Step 1: Build initial plan graph
        print(f"\n[Decision] Building initial plan graph...")
        ctx.plan_graph = self.decision.build_initial_plan_graph(query)
        ctx.log("plan_graph_created", node_count=len(ctx.plan_graph.nodes))
        
        # Step 2: Execute graph
        current_node_id = ctx.plan_graph.start_node_id
        completed_steps = []
        node_execution_trace = []  # Track node_id and variant used
        
        while current_node_id is not None:
            node = ctx.plan_graph.get_node(current_node_id)
            if not node:
                print(f"Node {current_node_id} not found. Stopping.")
                break
            
            # Skip if already completed or skipped
            if node.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                print(f"Node {current_node_id} already {node.status.name}. Moving to next...")
                current_node_id = self.decision.select_next_node(
                    ctx.plan_graph,
                    current_node_id,
                    PerceptionResult(Route.DECISION, False)
                )
                continue
            
            # Execute step
            print(f"\n[Step {current_node_id}] {node.description}")
            print(f"Trying {len(node.variants)} variants...")
            
            execution_result = await execute_step(
                node,
                ctx,
                self.multi_mcp,
                step_description=node.description,
                query=query,
                completed_steps=completed_steps
            )
            
            # Track completed step and node execution
            variant_succeeded = execution_result.get("variant_succeeded", f"{current_node_id}A")
            node_execution_trace.append({
                "node_id": current_node_id,
                "variant": variant_succeeded
            })
            
            if execution_result.get("status") == "success":
                completed_steps.append({
                    "node_id": current_node_id,
                    "description": node.description,
                    "result": execution_result.get("result"),
                    "variant_succeeded": variant_succeeded
                })
            
            # Perception on step output
            step_output = str(execution_result.get("result", ""))
            p = self.perception.perceive_step_output(current_node_id, step_output, ctx.get_globals_schema())
            ctx.log("step_perception", node_id=current_node_id, route=p.route.value, goal_met=p.goal_met)
            
            # If goal met, summarize
            if p.route == Route.SUMMARIZE and p.goal_met:
                print(f"\nGoal achieved at step {current_node_id}. Summarizing...")
                return self.formatter_agent.format_report(
                    ctx.get_globals_schema(),
                    p.instruction_to_summarize
                )
            
            # Handle failure
            if node.status == StepStatus.FAILED:
                print(f"Step {current_node_id} failed. Adding fallback...")
                fallback_id = self.decision.add_fallback_node(ctx.plan_graph, current_node_id)
                ctx.log("fallback_added", failed_node=current_node_id, fallback_node=fallback_id)
                current_node_id = fallback_id
            else:
                # Move to next node
                current_node_id = self.decision.select_next_node(
                    ctx.plan_graph,
                    current_node_id,
                    p
                )
        
        # Final summarization if loop exits without explicit summary
        print(f"\nExecution complete. Generating final summary...")
        
        # Store node execution trace in context for CSV logging
        ctx.globals_schema["node_execution_trace"] = node_execution_trace
        
        return self.formatter_agent.format_report(
            ctx.get_globals_schema(),
            "Produce final answer from execution results"
        )
