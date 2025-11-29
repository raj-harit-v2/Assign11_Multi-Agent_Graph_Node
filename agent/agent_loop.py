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
from memory.session_log import append_session_to_store
from agent.agentSession import AgentSession, PerceptionSnapshot
from mcp_servers.multiMCP import MultiMCP
from retrieval.retriever_agent import RetrieverAgent
from retrieval.triplet_agent import TripletAgent
from retrieval.graph_agent import GraphAgent
from retrieval.critic_agent import CriticAgent
from retrieval.formatter_agent import FormatterAgent
from core.human_in_loop import ask_user_for_plan


class AgentLoop:
    """V2 Graph-native agent loop with retrieval augmentation."""
    
    def __init__(self, perception_prompt_path: str, decision_prompt_path: str, multi_mcp: MultiMCP, strategy: str = "exploratory", use_ollama: bool = False):
        """
        Initialize V2 agent loop.
        
        Args:
            perception_prompt_path: Path to perception prompt file
            decision_prompt_path: Path to decision prompt file
            multi_mcp: MultiMCP instance
            strategy: Planning strategy
            use_ollama: If True, use Ollama instead of Google API (reads from config/profiles.yaml)
        """
        # Check config for Ollama preference
        import yaml
        from pathlib import Path
        try:
            with open("config/profiles.yaml", "r") as f:
                profile = yaml.safe_load(f)
                llm_config = profile.get("llm", {})
                text_gen = llm_config.get("text_generation", "gemini")
                # Use Ollama if configured in profiles.yaml (not "gemini")
                if text_gen != "gemini" and not use_ollama:
                    use_ollama = True
                    print(f"[INFO] Using Ollama model '{text_gen}' from config/profiles.yaml")
        except Exception as e:
            print(f"[WARN] Could not read config/profiles.yaml: {e}")
        
        self.perception = Perception(perception_prompt_path, use_ollama=use_ollama)
        self.decision = Decision(decision_prompt_path, multi_mcp, use_ollama=use_ollama)
        self.strategy = strategy
        self.multi_mcp = multi_mcp
        
        # Initialize retrieval agents
        self.graph_agent = GraphAgent()
        self.retriever_agent = RetrieverAgent(graph_agent=self.graph_agent)
        self.triplet_agent = TripletAgent()
        self.critic_agent = CriticAgent()
        self.formatter_agent = FormatterAgent()
    
    async def run(self, query: str, return_execution_details: bool = False) -> str | dict:
        """
        Run the graph-native agent loop.
        
        Args:
            query: User query
            return_execution_details: If True, return dict with answer and execution details
        
        Returns:
            Final answer string, or dict with 'answer' and 'execution_details' if return_execution_details=True
        """
        print(f"\n=== V2 GRAPH-NATIVE AGENT SESSION ===")
        print(f"Query: {query}")
        
        # Initialize context manager
        ctx = ContextManager()
        
        # Store query in context for error logging
        ctx.update_globals({"query": query})
        
        # Step -1: Memory Search
        # For simple math queries, skip memory and always execute
        import re
        query_lower = query.lower()
        is_simple_math = bool(re.search(r'\d+\s*[+\-*/]\s*\d+', query))
        
        if is_simple_math:
            print(f"\n[INFO] Simple math query detected. Skipping memory search and forcing execution.")
            memory_results = []  # Force execution for simple math - don't even create searcher
        else:
            print(f"\nSearching Recent Conversation History")
            searcher = MemorySearch()
            memory_results = searcher.search_memory(query, skip_load=False)  # Explicitly allow loading
            if not memory_results:
                print("No matching memory entries found.")
            else:
                print(f"\nTop {len(memory_results)} Matches:")
                for i, res in enumerate(memory_results[:3], 1):
                    print(f"[{i}] Query: {res.get('query', '')[:60]}...")
                    print(f"    Answer: {res.get('solution_summary', '')[:60]}...")
        
        # Store memory results in context for formatter to use (but don't set final_answer yet)
        if memory_results:
            # Store memory results but DON'T set final_answer - let execution happen
            best_match = memory_results[0]
            solution_summary = best_match.get("solution_summary") or best_match.get("summary", "")
            print(f"[DEBUG] Memory found but will execute anyway: {solution_summary[:100] if solution_summary else 'None'}")
            ctx.update_globals({
                "memory_results": memory_results,
                "memory_query": best_match.get("query", query)
                # NOTE: NOT setting final_answer here - force execution
            })
        
        # Step 0: Root Perception
        print(f"\n[Perception] Analyzing root query...")
        p0 = self.perception.perceive_root(query, memory_results)
        ctx.log("root_perception", route=p0.route.value, goal_met=p0.goal_met)
        
        # For simple math queries, ALWAYS force execution (skip early return)
        if is_simple_math:
            print("[INFO] Simple math query - forcing execution regardless of perception result.")
            p0.goal_met = False  # Force execution
            p0.route = Route.DECISION  # Force decision/execution path
        
        # If goal already met AND not simple math AND we have memory, summarize immediately
        # Don't summarize if no memory - force execution instead
        if p0.route == Route.SUMMARIZE and p0.goal_met and not is_simple_math and memory_results:
            print("Goal already achieved. Summarizing...")
            final_answer = self.formatter_agent.format_report(
                ctx.get_globals_schema(),
                p0.instruction_to_summarize,
                query=query
            )
            # Store final answer in context
            ctx.update_globals({"final_answer": final_answer})
            
            # Build execution_details for early return
            if return_execution_details:
                import json
                plan_steps = []
                if ctx.plan_graph and ctx.plan_graph.nodes:
                    for node_id, node in ctx.plan_graph.nodes.items():
                        plan_steps.append(f"Step {node_id}: {node.description}")
                
                # Extract from memory
                tools_used = set()
                if memory_results:
                    tools_used.add("memory_search")
                
                llm_provider = "Google API"
                if hasattr(self.perception, 'use_ollama') and self.perception.use_ollama:
                    llm_provider = "Ollama"
                
                execution_details = {
                    "answer": final_answer,
                    "plan_steps": plan_steps,
                    "plan_step_count": len(plan_steps),
                    "tools_used": list(tools_used),
                    "tool_name": list(tools_used)[0] if tools_used else "memory_search",
                    "nodes_called": [],
                    "nodes_exe_path": "",
                    "node_execution_trace": [],
                    "completed_steps": [],
                    "step_details": json.dumps([]),
                    "nodes_called_json": json.dumps([]),
                    "final_state": {
                        "final_answer": final_answer,
                        "nodes_executed": 0,
                        "steps_completed": 0,
                        "source": "memory"
                    },
                    "llm_provider": llm_provider,
                    "api_call_type": "memory_retrieval",
                    "human_in_loop_triggered": False,
                    "hil_reason": ""
                }
                return execution_details
            
            return final_answer
        elif p0.route == Route.SUMMARIZE and p0.goal_met and not memory_results:
            # Perception incorrectly said goal_met but no memory - force execution
            print("[WARN] Perception said goal_met but no memory found. Forcing execution...")
            p0.route = Route.DECISION
            p0.goal_met = False
        
        # Step 1: Build initial plan graph
        print(f"\n[Decision] Building initial plan graph...")
        ctx.plan_graph = self.decision.build_initial_plan_graph(query)
        ctx.log("plan_graph_created", node_count=len(ctx.plan_graph.nodes))
        
        # Step 2: Execute graph
        current_node_id = ctx.plan_graph.start_node_id
        completed_steps = []
        node_execution_trace = []  # Track node_id and variant used
        max_steps = 10  # Maximum steps before triggering HIL
        consecutive_failures = 0  # Track consecutive failures
        max_consecutive_failures = 3  # Trigger HIL after 3 consecutive failures
        
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
                result_value = execution_result.get("result", "")
                # Store result in context for ALL queries (not just simple math)
                ctx.update_globals({
                    "last_result": str(result_value),
                    "last_node": current_node_id
                })
                
                completed_steps.append({
                    "node_id": current_node_id,
                    "description": node.description,
                    "result": result_value,
                    "variant_succeeded": variant_succeeded
                })
            
            # Perception on step output
            step_output = str(execution_result.get("result", ""))
            p = self.perception.perceive_step_output(current_node_id, step_output, ctx.get_globals_schema())
            ctx.log("step_perception", node_id=current_node_id, route=p.route.value, goal_met=p.goal_met)
            
            # For simple math queries, use execution result directly
            import re
            is_simple_math = bool(re.search(r'\d+\s*[+\-*/]\s*\d+', query))
            if is_simple_math and execution_result.get("status") == "success":
                # For simple math, use the execution result as final answer
                result_value = execution_result.get("result", "")
                if result_value:
                    print(f"[INFO] Simple math execution successful. Result: {result_value}")
                    ctx.update_globals({"final_answer": str(result_value), "last_result": str(result_value)})
                    final_answer = self.formatter_agent.format_report(
                        ctx.get_globals_schema(),
                        "Produce concise answer from execution results",
                        query=query
                    )
                    ctx.update_globals({"final_answer": final_answer})
                    
                    # Build execution_details for early return
                    if return_execution_details:
                        import json
                        plan_steps = []
                        if ctx.plan_graph and ctx.plan_graph.nodes:
                            for node_id, node in ctx.plan_graph.nodes.items():
                                plan_steps.append(f"Step {node_id}: {node.description}")
                        
                        # Extract tools used from execution
                        tools_used = set()
                        for step in completed_steps:
                            result_str = str(step.get("result", "")).lower()
                            desc_str = str(step.get("description", "")).lower()
                            for op in ["add", "subtract", "multiply", "divide", "power", "factorial", "gcd", "sqrt", "cbrt", "remainder"]:
                                if op in desc_str:
                                    tools_used.add(op)
                                    break
                        
                        nodes_called_list = [trace["node_id"] for trace in node_execution_trace]
                        nodes_exe_path = "->".join(nodes_called_list) if nodes_called_list else ""
                        
                        step_details_list = []
                        for step in completed_steps:
                            step_details_list.append({
                                "node_id": step.get("node_id", ""),
                                "description": step.get("description", ""),
                                "variant": step.get("variant_succeeded", ""),
                                "result_preview": str(step.get("result", ""))[:100]
                            })
                        
                        llm_provider = "Google API"
                        if hasattr(self.perception, 'use_ollama') and self.perception.use_ollama:
                            llm_provider = "Ollama"
                        elif hasattr(self.decision, 'use_ollama') and self.decision.use_ollama:
                            llm_provider = "Ollama"
                        
                        execution_details = {
                            "answer": final_answer,
                            "plan_steps": plan_steps,
                            "plan_step_count": len(plan_steps),
                            "tools_used": list(tools_used),
                            "tool_name": list(tools_used)[0] if tools_used else "agent_loop",
                            "nodes_called": nodes_called_list,
                            "nodes_exe_path": nodes_exe_path,
                            "node_execution_trace": node_execution_trace,
                            "completed_steps": completed_steps,
                            "step_details": json.dumps(step_details_list),
                            "nodes_called_json": json.dumps(nodes_called_list),
                            "final_state": {
                                "final_answer": final_answer,
                                "nodes_executed": len(nodes_called_list),
                                "steps_completed": len(completed_steps)
                            },
                            "llm_provider": llm_provider,
                            "api_call_type": "tool_execution" if tools_used else "llm_call",
                            "human_in_loop_triggered": False,
                            "hil_reason": ""
                        }
                        return execution_details
                    
                    return final_answer
            
            # For non-simple-math queries, also store result if execution succeeded
            if execution_result.get("status") == "success" and not is_simple_math:
                result_value = execution_result.get("result", "")
                if result_value and result_value != "Tool failed, no user input provided":
                    # Store as potential final answer
                    ctx.update_globals({"last_result": str(result_value)})
            
            # If goal met, summarize
            if p.route == Route.SUMMARIZE and p.goal_met:
                print(f"\nGoal achieved at step {current_node_id}. Summarizing...")
                final_answer = self.formatter_agent.format_report(
                    ctx.get_globals_schema(),
                    p.instruction_to_summarize,
                    query=query
                )
                # Store final answer in context
                ctx.update_globals({"final_answer": final_answer})
                return final_answer
            
            # Handle failure
            if node.status == StepStatus.FAILED:
                consecutive_failures += 1
                print(f"Step {current_node_id} failed. Adding fallback...")
                fallback_id = self.decision.add_fallback_node(ctx.plan_graph, current_node_id)
                
                # Check if fallback was successfully added
                if fallback_id is None:
                    # No fallback available - trigger HIL
                    print(f"\n[WARNING] Step {current_node_id} failed and no fallback available. Triggering Human-in-Loop...")
                    ctx.update_globals({"human_in_loop_triggered": True, "hil_reason": "no_fallback_available"})
                    
                    # Build context for HIL
                    current_plan = [n.description for n in ctx.plan_graph.nodes.values() if n.status != StepStatus.SKIPPED]
                    context = {
                        "reason": f"Step {current_node_id} failed and no fallback available",
                        "current_plan": current_plan,
                        "step_count": len(completed_steps),
                        "max_steps": max_steps,
                        "query": query,
                        "failed_node": current_node_id,
                        "consecutive_failures": consecutive_failures
                    }
                    
                    # Generate suggested plan
                    suggested_plan = self.decision.build_initial_plan_graph(query)
                    suggested_plan_steps = [n.description for n in suggested_plan.nodes.values()]
                    
                    # Trigger HIL
                    session_id = ctx.globals_schema.get("session_id", str(uuid.uuid4()))
                    new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan_steps, session_id)
                    
                    # If user provided a plan, use it
                    if new_plan and user_plan_dict:
                        # User provided JSON plan with final_answer
                        final_answer = user_plan_dict.get('final_answer', '')
                        if final_answer:
                            ctx.update_globals({"final_answer": final_answer})
                            return final_answer
                    elif new_plan and new_plan != suggested_plan_steps:
                        # User provided custom plan - rebuild graph with new plan
                        print(f"\n[INFO] Rebuilding plan graph with user-provided plan ({len(new_plan)} steps)...")
                        # Rebuild plan graph using the query with modified context
                        ctx.plan_graph = self.decision.build_initial_plan_graph(query)
                        current_node_id = ctx.plan_graph.start_node_id
                        consecutive_failures = 0  # Reset failure counter
                        continue
                    else:
                        # User accepted suggested plan or no input (non-interactive mode)
                        print(f"\n[INFO] Using suggested plan or default (non-interactive mode)...")
                        ctx.plan_graph = suggested_plan
                        current_node_id = ctx.plan_graph.start_node_id
                        consecutive_failures = 0
                        continue
                
                ctx.log("fallback_added", failed_node=current_node_id, fallback_node=fallback_id)
                current_node_id = fallback_id
            else:
                # Reset consecutive failures on success
                if execution_result.get("status") == "success":
                    consecutive_failures = 0
                
                # Check for consecutive failures or step limit
                if consecutive_failures >= max_consecutive_failures:
                    print(f"\n[WARNING] {consecutive_failures} consecutive failures detected. Triggering Human-in-Loop...")
                    ctx.update_globals({"human_in_loop_triggered": True, "hil_reason": "consecutive_failures"})
                    
                    current_plan = [n.description for n in ctx.plan_graph.nodes.values() if n.status != StepStatus.SKIPPED]
                    context = {
                        "reason": f"{consecutive_failures} consecutive step failures",
                        "current_plan": current_plan,
                        "step_count": len(completed_steps),
                        "max_steps": max_steps,
                        "query": query,
                        "consecutive_failures": consecutive_failures
                    }
                    
                    suggested_plan = self.decision.build_initial_plan_graph(query)
                    suggested_plan_steps = [n.description for n in suggested_plan.nodes.values()]
                    
                    session_id = ctx.globals_schema.get("session_id", str(uuid.uuid4()))
                    new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan_steps, session_id)
                    
                    if new_plan and user_plan_dict:
                        final_answer = user_plan_dict.get('final_answer', '')
                        if final_answer:
                            ctx.update_globals({"final_answer": final_answer})
                            return final_answer
                    elif new_plan and new_plan != suggested_plan_steps:
                        print(f"\n[INFO] Rebuilding plan graph with user-provided plan...")
                        ctx.plan_graph = self.decision.build_initial_plan_graph(query)
                        current_node_id = ctx.plan_graph.start_node_id
                        consecutive_failures = 0
                        continue
                
                # Check step limit
                if len(completed_steps) >= max_steps and not p.goal_met:
                    print(f"\n[WARNING] Maximum steps ({max_steps}) reached without goal achievement. Triggering Human-in-Loop...")
                    ctx.update_globals({"human_in_loop_triggered": True, "hil_reason": "max_steps_reached"})
                    
                    current_plan = [n.description for n in ctx.plan_graph.nodes.values() if n.status != StepStatus.SKIPPED]
                    context = {
                        "reason": f"Maximum steps ({max_steps}) reached without goal achievement",
                        "current_plan": current_plan,
                        "step_count": len(completed_steps),
                        "max_steps": max_steps,
                        "query": query
                    }
                    
                    suggested_plan = self.decision.build_initial_plan_graph(query)
                    suggested_plan_steps = [n.description for n in suggested_plan.nodes.values()]
                    
                    session_id = ctx.globals_schema.get("session_id", str(uuid.uuid4()))
                    new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan_steps, session_id)
                    
                    if new_plan and user_plan_dict:
                        final_answer = user_plan_dict.get('final_answer', '')
                        if final_answer:
                            ctx.update_globals({"final_answer": final_answer})
                            return final_answer
                    elif new_plan and new_plan != suggested_plan_steps:
                        print(f"\n[INFO] Rebuilding plan graph with user-provided plan...")
                        ctx.plan_graph = self.decision.build_initial_plan_graph(query)
                        current_node_id = ctx.plan_graph.start_node_id
                        consecutive_failures = 0
                        continue
                
                # Move to next node
                current_node_id = self.decision.select_next_node(
                    ctx.plan_graph,
                    current_node_id,
                    p
                )
        
        # Final summarization if loop exits without explicit summary
        print(f"\nExecution complete. Generating final summary...")
        
        # Store node execution trace and completed steps in context for CSV logging and formatter
        ctx.globals_schema["node_execution_trace"] = node_execution_trace
        ctx.globals_schema["completed_steps"] = completed_steps
        
        # For complex queries with multiple steps, aggregate all results
        # Optimized: Use list comprehension for better performance
        if len(completed_steps) > 1:
            # Build aggregated result from all completed steps
            aggregated_parts = []
            for step in completed_steps:
                if step.get("result") and str(step["result"]) != "Tool failed, no user input provided":
                    desc = step.get("description", "")
                    result_val = str(step["result"])
                    # For math results, extract just the number if it's a simple numeric result
                    if desc and any(word in desc.lower() for word in ["calculate", "find", "compute", "factorial", "sum", "gcd", "prime"]):
                        # Try to extract just the numeric result
                        import re
                        num_match = re.search(r'\b(\d+\.?\d*)\b', result_val)
                        if num_match and len(result_val) < 50:  # If result is mostly a number
                            aggregated_parts.append(f"{desc}: {num_match.group(1)}")
                        else:
                            aggregated_parts.append(f"{desc}: {result_val}")
                    else:
                        aggregated_parts.append(f"{desc}: {result_val}")
            
            if aggregated_parts:
                aggregated_result = ". ".join(aggregated_parts) + "."
                ctx.update_globals({"last_result": aggregated_result, "aggregated_results": aggregated_parts})
                print(f"[DEBUG] Aggregated results from {len(completed_steps)} steps: {aggregated_result[:200]}")
        
        # Ensure last_result is available for formatter
        if "last_result" not in ctx.globals_schema or not ctx.globals_schema["last_result"]:
            # Try to get result from completed steps
            if completed_steps:
                last_step = completed_steps[-1]
                if "result" in last_step and last_step["result"]:
                    result_value = str(last_step["result"])
                    if result_value != "Tool failed, no user input provided":
                        ctx.update_globals({"last_result": result_value})
        
        final_answer = self.formatter_agent.format_report(
            ctx.get_globals_schema(),
            "Produce final answer from execution results",
            query=query
        )
        ctx.update_globals({"final_answer": final_answer})
        
        # Save session to memory for future queries
        try:
            from memory.session_log import append_session_to_store
            from agent.agentSession import AgentSession, PerceptionSnapshot
            from dataclasses import asdict
            
            # Create a session object from context
            session_id = str(uuid.uuid4())
            session = AgentSession(session_id, query)
            
            # Add perception if available (from context or p0)
            perception_result = ctx.globals_schema.get("perception_result")
            if not perception_result and 'p0' in locals():
                perception_result = p0
            
            if perception_result:
                try:
                    # Convert PerceptionResult to PerceptionSnapshot
                    goal_met = perception_result.goal_met if hasattr(perception_result, 'goal_met') else False
                    notes = perception_result.notes if hasattr(perception_result, 'notes') else ""
                    perception_snapshot = PerceptionSnapshot(
                        entities=[],
                        result_requirement="",
                        original_goal_achieved=goal_met,
                        reasoning=notes,
                        local_goal_achieved=goal_met,
                        local_reasoning=notes,  # Added missing parameter
                        last_tooluse_summary="",
                        solution_summary=final_answer,
                        confidence="0.95"
                    )
                    session.add_perception(perception_snapshot)
                except Exception as e:
                    print(f"[WARN] Could not add perception to session: {e}")
            
            # Add final state
            session.state.update({
                "original_goal_achieved": True,
                "final_answer": final_answer,
                "confidence": 0.95,
                "solution_summary": final_answer,
                "reasoning_note": ""
            })
            
            # Save to memory
            append_session_to_store(session, enhance=True)
        except Exception as e:
            print(f"[WARN] Could not save session to memory: {e}")
            import traceback
            traceback.print_exc()
        
        # Prepare execution details for CSV logging if requested
        if return_execution_details:
            import json
            # Extract plan steps from plan graph
            plan_steps = []
            if ctx.plan_graph and ctx.plan_graph.nodes:
                for node_id, node in ctx.plan_graph.nodes.items():
                    plan_steps.append(f"Step {node_id}: {node.description}")
            
            # Extract tools used from completed steps and node execution
            tools_used = set()
            for step in completed_steps:
                result_str = str(step.get("result", "")).lower()
                desc_str = str(step.get("description", "")).lower()
                # Check for search tools
                if "duckduckgo" in result_str or "duckduckgo" in desc_str:
                    tools_used.add("duckduckgo_search_with_markdown")
                # Check for math tools
                for op in ["add", "subtract", "multiply", "divide", "power", "factorial", "gcd", "sqrt", "cbrt", "remainder"]:
                    if op in desc_str:
                        tools_used.add(op)
                        break
            
            # Extract nodes called and build execution path
            nodes_called_list = [trace["node_id"] for trace in node_execution_trace]
            nodes_exe_path = "->".join(nodes_called_list) if nodes_called_list else ""
            
            # Build step details JSON
            step_details_list = []
            for step in completed_steps:
                step_details_list.append({
                    "node_id": step.get("node_id", ""),
                    "description": step.get("description", ""),
                    "variant": step.get("variant_succeeded", ""),
                    "result_preview": str(step.get("result", ""))[:100]
                })
            
            # Determine LLM provider (check if Ollama was used)
            llm_provider = "Google API"  # Default
            if hasattr(self.perception, 'use_ollama') and self.perception.use_ollama:
                llm_provider = "Ollama"
            elif hasattr(self.decision, 'use_ollama') and self.decision.use_ollama:
                llm_provider = "Ollama"
            
            # Check if HIL was triggered during execution
            hil_triggered = ctx.globals_schema.get("human_in_loop_triggered", False)
            hil_reason = ctx.globals_schema.get("hil_reason", "")
            
            execution_details = {
                "answer": final_answer,
                "plan_steps": plan_steps,
                "plan_step_count": len(plan_steps) if plan_steps else 0,
                "tools_used": list(tools_used),
                "tool_name": list(tools_used)[0] if tools_used else "agent_loop",
                "nodes_called": nodes_called_list,
                "nodes_exe_path": nodes_exe_path,
                "node_execution_trace": node_execution_trace,
                "completed_steps": completed_steps,
                "step_details": json.dumps(step_details_list),
                "nodes_called_json": json.dumps(nodes_called_list),
                "node_count": len(nodes_called_list),
                "final_state": {
                    "final_answer": final_answer,
                    "nodes_executed": len(nodes_called_list),
                    "steps_completed": len(completed_steps)
                },
                "llm_provider": llm_provider,
                "api_call_type": "tool_execution" if tools_used else "llm_call",
                "human_in_loop_triggered": hil_triggered,
                "hil_reason": hil_reason
            }
            return execution_details
        
        return final_answer
