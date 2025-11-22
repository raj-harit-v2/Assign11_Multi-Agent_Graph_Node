import uuid
import json
import datetime
import time
from perception.perception import Perception
from decision.decision import Decision
from action.executor import run_user_code
from agent.agentSession import AgentSession, PerceptionSnapshot, Step, ToolCode
from memory.session_log import live_update_session
from memory.memory_search import MemorySearch
from mcp_servers.multiMCP import MultiMCP
from core.control_manager import ControlManager
from core.human_in_loop import ask_user_for_plan
from core.user_plan_storage import UserPlanStorage
from utils.csv_manager import CSVManager
from utils.time_utils import get_current_datetime, calculate_elapsed_time

GLOBAL_PREVIOUS_FAILURE_STEPS = 3

class AgentLoop:
    def __init__(self, perception_prompt_path: str, decision_prompt_path: str, multi_mcp: MultiMCP, strategy: str = "exploratory"):
        self.perception = Perception(perception_prompt_path)
        self.decision = Decision(decision_prompt_path, multi_mcp)
        self.multi_mcp = multi_mcp
        self.strategy = strategy
        self.control_manager = ControlManager()
        self.csv_manager = CSVManager()

    async def run(self, query: str, test_id: int = None, query_id: int = None, query_name: str = "Test query for diagnostic"):
        """
        Run agent loop with CSV logging and step limits.
        
        Args:
            query: User query (actual query text)
            test_id: Optional test ID for CSV logging
            query_id: Optional query ID (Bigint, will be generated if not provided)
            query_name: Query name/description (default: "Test query for diagnostic")
        
        Returns:
            AgentSession: Completed session
        """
        session_start_time = time.perf_counter()
        start_datetime = get_current_datetime()
        
        # Generate or use provided query_id
        if query_id is None:
            query_id = self.csv_manager.add_query(query_text=query, query_name=query_name)
        else:
            self.csv_manager.add_query(query_text=query, query_name=query_name, query_id=query_id)
        
        session = AgentSession(session_id=str(uuid.uuid4()), original_query=query)
        session_memory= []
        self.log_session_start(session, query)

        memory_results = self.search_memory(query)
        perception_result = self.run_perception(query, memory_results, memory_results)
        session.add_perception(PerceptionSnapshot(**perception_result))

        if perception_result.get("original_goal_achieved"):
            self.handle_perception_completion(session, perception_result)
            return session

        decision_output = self.make_initial_decision(query, perception_result)
        step = session.add_plan_version(decision_output["plan_text"], [self.create_step(decision_output)])
        live_update_session(session)
        print(f"\n[Decision Plan Text: V{len(session.plan_versions)}]:")
        for line in session.plan_versions[-1]["plan_text"]:
            print(f"  {line}")

        # Main execution loop with step limit enforcement
        while step:
            # Check step limit
            current_step_index = session.get_next_step_index()
            is_limit_reached, limit_message = self.control_manager.check_step_limit(current_step_index)
            
            if is_limit_reached:
                print(f"\n{limit_message}")
                # Trigger human-in-loop for plan modification
                context = {
                    "reason": limit_message,
                    "current_plan": session.plan_versions[-1]["plan_text"] if session.plan_versions else [],
                    "step_count": current_step_index,
                    "max_steps": self.control_manager.get_max_steps(),
                    "query": query
                }
                # Check if we have a stored user plan from previous lifeline
                stored_user_plan = UserPlanStorage.get_user_plan(session.session_id)
                if stored_user_plan:
                    print("\n[USING STORED PLAN] Using user-provided plan from previous lifeline...")
                    user_plan_dict = stored_user_plan
                    conclude_text = user_plan_dict.get('final_answer', 'User-provided answer')
                    goal_achieved = user_plan_dict.get('original_goal_achieved', False)
                else:
                    # Suggest continuing with conclusion or new plan
                    suggested_plan = ["Conclude with current results", "Provide final answer"]
                    new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan, session.session_id)
                    
                    # If user provided JSON plan, use it
                    if user_plan_dict:
                        conclude_text = user_plan_dict.get('final_answer', new_plan[0] if new_plan else "User-provided answer")
                        goal_achieved = user_plan_dict.get('original_goal_achieved', False)
                    else:
                        conclude_text = new_plan[0] if new_plan else "User-provided answer"
                        # Check if we're concluding due to failure
                        is_conclusion_due_to_failure = (
                            "conclude with current results" in conclude_text.lower() or
                            "conclude" in conclude_text.lower() and "current results" in conclude_text.lower()
                        )
                        goal_achieved = not is_conclusion_due_to_failure
                
                # Create a CONCLUDE step from user plan
                if conclude_text:
                    conclude_step = Step(
                        index=current_step_index,
                        description=conclude_text,
                        type="CONCLUDE",
                        conclusion=conclude_text,
                        status="completed"
                    )
                    plan_list = [conclude_text]
                    session.add_plan_version(plan_list, [conclude_step])
                    
                    # When user provides answer, mark as FAILED (not success)
                    # User-provided answers indicate the agent couldn't solve it
                    if user_plan_dict or stored_user_plan:
                        goal_achieved = False  # Always mark as failed when user provides answer
                        print("\n[STATUS] User-provided answer detected - marking as FAILED")
                    
                    session.mark_complete(
                        PerceptionSnapshot(
                            entities=[],
                            result_requirement="User-provided answer",
                            original_goal_achieved=goal_achieved,
                            reasoning=user_plan_dict.get('reasoning_note', 'User provided answer') if user_plan_dict else "Plan limit reached, user provided answer",
                            local_goal_achieved=True,
                            local_reasoning="User intervention",
                            last_tooluse_summary="",
                            solution_summary=user_plan_dict.get('solution_summary', conclude_text) if user_plan_dict else conclude_text,
                            confidence=user_plan_dict.get('confidence', '0.5') if user_plan_dict else "0.5"
                        ),
                        final_answer=conclude_text
                    )
                break
            
            step_result = await self.execute_step(step, session, session_memory, query)
            if step_result is None:
                break  # 🔐 protect against CONCLUDE/NOP cases
            step = self.evaluate_step(step_result, session, query)

        # Log to CSV
        session_end_time = time.perf_counter()
        end_datetime = get_current_datetime()
        elapsed_time = calculate_elapsed_time(session_start_time, session_end_time)
        
        # Determine result status
        # Check if goal was actually achieved (not just concluded due to failure)
        original_goal_achieved = session.state.get("original_goal_achieved", False)
        final_answer = session.state.get("final_answer") or session.state.get("solution_summary") or ""
        
        # Check if user provided answer (stored in UserPlanStorage)
        user_provided_answer = UserPlanStorage.has_user_plan(session.session_id)
        
        # If user provided answer, always mark as FAILED
        if user_provided_answer:
            result_status = "failure"
            print("\n[CSV LOG] User-provided answer detected - Result_Status will be 'failure'")
        # If final answer indicates we're concluding due to failure, mark as failure
        elif "conclude with current results" in final_answer.lower() or \
             ("conclude" in final_answer.lower() and "current results" in final_answer.lower()):
            result_status = "failure"
        # Result is success only if goal was achieved AND we're not concluding due to failure
        elif original_goal_achieved:
            result_status = "success"
        else:
            result_status = "failure"
        
        # Get plan used
        plan_used = []
        if session.plan_versions:
            plan_used = session.plan_versions[-1]["plan_text"]
        
        # Get tool name from last step
        tool_name = ""
        if session.plan_versions and session.plan_versions[-1]["steps"]:
            last_step = session.plan_versions[-1]["steps"][-1]
            if last_step.code:
                tool_name = last_step.code.tool_name
        
        # Get retry count from last step
        retry_count = 0
        if session.plan_versions and session.plan_versions[-1]["steps"]:
            last_step = session.plan_versions[-1]["steps"][-1]
            if hasattr(last_step, 'execution_result') and isinstance(last_step.execution_result, dict):
                retry_count = last_step.execution_result.get("retry_count", 0)
        
        # Get error message if any
        error_message = ""
        if not session.state.get("original_goal_achieved", False):
            error_message = session.state.get("reasoning_note", "Execution failed")
        
        # Get final answer
        query_answer = session.state.get("final_answer") or session.state.get("solution_summary") or ""
        
        # Log to CSV (after user input, if any)
        if test_id is not None:
            # Check if user provided plan and include it in final_state
            user_plan = UserPlanStorage.get_user_plan(session.session_id)
            if user_plan:
                # Add user plan info to final_state
                session.state["user_provided_plan"] = user_plan
                print("\n[CSV LOG] User-provided plan included in CSV log")
            
            self.csv_manager.log_tool_performance(
                test_id=test_id,
                query_id=query_id,
                query_name=query_name,
                query_text=query,
                query_answer=query_answer,
                plan_used=plan_used,
                result_status=result_status,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                elapsed_time=elapsed_time,
                plan_step_count=len(plan_used),
                tool_name=tool_name,
                retry_count=retry_count,
                error_message=error_message,
                final_state=session.state
            )
        
        # Clean up: Remove stored user plan from memory after session finishes
        UserPlanStorage.clear_user_plan(session.session_id)

        return session

    def log_session_start(self, session, query):
        print("\n=== LIVE AGENT SESSION TRACE ===")
        print(f"Session ID: {session.session_id}")
        print(f"Query: {query}")

    def search_memory(self, query):
        print("Searching Recent Conversation History")
        searcher = MemorySearch()
        results = searcher.search_memory(query)
        if not results:
            print("[ERROR] No matching memory entries found.\n")
        else:
            print("\n[TOP MATCHES]:\n")
            for i, res in enumerate(results, 1):
                print(f"[{i}] File: {res['file']}\nQuery: {res['query']}\nResult Requirement: {res['result_requirement']}\nSummary: {res['solution_summary']}\n")
        return results

    def run_perception(self, query, memory_results, session_memory=None, snapshot_type="user_query", current_plan=None):
        combined_memory = (memory_results or []) + (session_memory or [])
        perception_input = self.perception.build_perception_input(
            raw_input=query, 
            memory=combined_memory, 
            current_plan=current_plan, 
            snapshot_type=snapshot_type
        )
        perception_result = self.perception.run(perception_input)
        print("\n[Perception Result]:")
        print(json.dumps(perception_result, indent=2, ensure_ascii=False))
        return perception_result

    def handle_perception_completion(self, session, perception_result):
        print("\n[OK] Perception fully answered the query.")
        session.state.update({
            "original_goal_achieved": True,
            "final_answer": perception_result.get("solution_summary", "Answer ready."),
            "confidence": perception_result.get("confidence", 0.95),
            "reasoning_note": perception_result.get("reasoning", "Handled by perception."),
            "solution_summary": perception_result.get("solution_summary", "Answer ready.")
        })
        live_update_session(session)

    def make_initial_decision(self, query, perception_result):
        decision_input = {
            "plan_mode": "initial",
            "planning_strategy": self.strategy,
            "original_query": query,
            "perception": perception_result
        }
        decision_output = self.decision.run(decision_input)
        return decision_output

    def create_step(self, decision_output):
        return Step(
            index=decision_output["step_index"],
            description=decision_output["description"],
            type=decision_output["type"],
            code=ToolCode(tool_name="raw_code_block", tool_arguments={"code": decision_output["code"]}) if decision_output["type"] == "CODE" else None,
            conclusion=decision_output.get("conclusion"),
        )

    async def execute_step(self, step, session, session_memory, query: str = ""):
        print(f"\n[Step {step.index}] {step.description}")

        if step.type == "CODE":
            print("-" * 50, "\n[EXECUTING CODE]\n", step.code.tool_arguments["code"])
            
            # Build completed_steps list from session for code execution context
            completed_steps = []
            if session.plan_versions:
                for plan_version in session.plan_versions:
                    for s in plan_version.get("steps", []):
                        if s.status == "completed" and hasattr(s, 'execution_result'):
                            completed_steps.append({
                                "index": s.index,
                                "description": s.description,
                                "execution_result": s.execution_result if isinstance(s.execution_result, dict) else {"result": str(s.execution_result)},
                                "status": s.status
                            })
            
            executor_response = await run_user_code(
                step.code.tool_arguments["code"], 
                self.multi_mcp,
                step_description=step.description,
                query=query,
                completed_steps=completed_steps
            )
            step.execution_result = executor_response
            
            # Check if tool failed and handle accordingly
            if executor_response.get("status") != "success":
                step.status = "failed"
                step.error = executor_response.get("error", "Unknown error")
            else:
                step.status = "completed"

            perception_result = self.run_perception(
                query=executor_response.get('result', 'Tool Failed'),
                memory_results=session_memory,
                current_plan=session.plan_versions[-1]["plan_text"],
                snapshot_type="step_result"
            )
            step.perception = PerceptionSnapshot(**perception_result)

            if not step.perception or not step.perception.local_goal_achieved:
                failure_memory = {
                    "query": step.description,
                    "result_requirement": "Tool failed",
                    "solution_summary": str(step.execution_result)[:300]
                }
                session_memory.append(failure_memory)

                if len(session_memory) > GLOBAL_PREVIOUS_FAILURE_STEPS:
                    session_memory.pop(0)

            live_update_session(session)
            return step

        elif step.type == "CONCLUDE":
            print(f"\n[CONCLUSION] {step.conclusion}")
            step.execution_result = step.conclusion
            step.status = "completed"

            perception_result = self.run_perception(
                query=step.conclusion,
                memory_results=session_memory,
                current_plan=session.plan_versions[-1]["plan_text"],
                snapshot_type="step_result"
            )
            step.perception = PerceptionSnapshot(**perception_result)
            session.mark_complete(step.perception, final_answer=step.conclusion)
            live_update_session(session)
            return None

        elif step.type == "NOP":
            print(f"\n❓ Clarification needed: {step.description}")
            step.status = "clarification_needed"
            live_update_session(session)
            return None

    def evaluate_step(self, step, session, query):
        if step.perception and step.perception.original_goal_achieved:
            print("\n[OK] Goal achieved.")
            session.mark_complete(step.perception)
            live_update_session(session)
            return None
        elif step.perception and step.perception.local_goal_achieved:
            # Check step limit before getting next step
            next_index = session.get_next_step_index()
            is_limit_reached, limit_message = self.control_manager.check_step_limit(next_index)
            if is_limit_reached:
                print(f"\n{limit_message}")
                # Trigger human-in-loop
                context = {
                    "reason": "Step limit will be reached",
                    "current_plan": session.plan_versions[-1]["plan_text"] if session.plan_versions else [],
                    "step_count": next_index,
                    "max_steps": self.control_manager.get_max_steps(),
                    "query": query
                }
                # Check if we have a stored user plan from previous lifeline
                stored_user_plan = UserPlanStorage.get_user_plan(session.session_id)
                if stored_user_plan:
                    print("\n[USING STORED PLAN] Using user-provided plan from previous lifeline...")
                    user_plan_dict = stored_user_plan
                    new_plan = [user_plan_dict.get('final_answer', 'User-provided answer')]
                else:
                    suggested_plan = ["Conclude with current results"]
                    new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan, session.session_id)
                if new_plan:
                    conclude_text = new_plan[0]
                    conclude_step = Step(
                        index=next_index,
                        description=conclude_text,
                        type="CONCLUDE",
                        conclusion=conclude_text,
                        status="completed"
                    )
                    session.add_plan_version(new_plan, [conclude_step])
                    
                # When user provides answer, mark as FAILED (not success)
                if stored_user_plan:
                    user_plan_dict = stored_user_plan
                    goal_achieved = False  # Always mark as failed when user provides answer
                    print("\n[STATUS] User-provided answer detected - marking as FAILED")
                    session.mark_complete(
                        PerceptionSnapshot(
                            entities=[],
                            result_requirement="Step limit reached",
                            original_goal_achieved=goal_achieved,
                            reasoning=user_plan_dict.get('reasoning_note', 'User provided answer'),
                            local_goal_achieved=True,
                            local_reasoning="User intervention due to step limit",
                            last_tooluse_summary="",
                            solution_summary=user_plan_dict.get('solution_summary', conclude_text),
                            confidence=user_plan_dict.get('confidence', '0.5')
                        ),
                        final_answer=conclude_text
                    )
                else:
                    # Check if we're concluding due to failure
                    is_conclusion_due_to_failure = (
                        "conclude with current results" in conclude_text.lower() or
                        ("conclude" in conclude_text.lower() and "current results" in conclude_text.lower())
                    )
                    
                    # Mark session complete with proper goal achievement status
                    goal_achieved = not is_conclusion_due_to_failure
                    session.mark_complete(
                        PerceptionSnapshot(
                            entities=[],
                            result_requirement="Step limit reached",
                            original_goal_achieved=goal_achieved,
                            reasoning="Step limit reached, concluding with current results" if is_conclusion_due_to_failure else "Step limit reached, goal achieved",
                            local_goal_achieved=True,
                            local_reasoning="User intervention due to step limit",
                            last_tooluse_summary="",
                            solution_summary=conclude_text,
                            confidence="0.5" if is_conclusion_due_to_failure else "0.8"
                        ),
                        final_answer=conclude_text
                    )
                return None
            return self.get_next_step(session, query, step)
        else:
            print("\n[REPLAN] Step unhelpful. Plan failed. Requesting human guidance...")
            # Always trigger human-in-loop when plan fails to show agent listens
            current_step_index = session.get_next_step_index()
            is_limit_reached, limit_message = self.control_manager.check_step_limit(current_step_index)
            
            # Build context for human-in-loop
            context = {
                "reason": "Plan failed - step was unhelpful" + (f" and {limit_message}" if is_limit_reached else ""),
                "current_plan": session.plan_versions[-1]["plan_text"] if session.plan_versions else [],
                "step_count": current_step_index,
                "max_steps": self.control_manager.get_max_steps(),
                "query": query
            }
            
            # Get suggested plan from decision module
            decision_output = self.decision.run({
                "plan_mode": "mid_session",
                "planning_strategy": self.strategy,
                "original_query": query,
                "current_plan_version": len(session.plan_versions),
                "current_plan": session.plan_versions[-1]["plan_text"],
                "completed_steps": [s.to_dict() for s in session.plan_versions[-1]["steps"] if s.status == "completed"],
                "current_step": step.to_dict()
            })
            suggested_plan = decision_output.get("plan_text", ["Conclude"])
            
            # Check if we have a stored user plan from previous lifeline
            stored_user_plan = UserPlanStorage.get_user_plan(session.session_id)
            if stored_user_plan:
                print("\n[USING STORED PLAN] Using user-provided plan from previous lifeline...")
                user_plan_dict = stored_user_plan
                new_plan = [user_plan_dict.get('final_answer', 'User-provided answer')]
            else:
                # Show agent is listening - trigger human-in-loop
                print("\n[LISTENING] Agent is listening for your guidance...")
                new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan, session.session_id)
            
            # Agent uses the plan provided by user (shows agent listens)
            if new_plan:
                print("\n[OK] Agent received your plan. Implementing...")
                step = session.add_plan_version(new_plan, [self.create_step(decision_output)])
                print(f"\n[Decision Plan Text: V{len(session.plan_versions)}] (User-guided):")
                for line in session.plan_versions[-1]["plan_text"]:
                    print(f"  {line}")
                return step
            else:
                print("\n[WARN] No plan provided. Agent will conclude.")
                return None

    def get_next_step(self, session, query, step):
        next_index = step.index + 1
        total_steps = len(session.plan_versions[-1]["plan_text"])
        if next_index < total_steps:
            decision_output = self.decision.run({
                "plan_mode": "mid_session",
                "planning_strategy": self.strategy,
                "original_query": query,
                "current_plan_version": len(session.plan_versions),
                "current_plan": session.plan_versions[-1]["plan_text"],
                "completed_steps": [s.to_dict() for s in session.plan_versions[-1]["steps"] if s.status == "completed"],
                "current_step": step.to_dict()
            })
            step = session.add_plan_version(decision_output["plan_text"], [self.create_step(decision_output)])

            print(f"\n[Decision Plan Text: V{len(session.plan_versions)}]:")
            for line in session.plan_versions[-1]["plan_text"]:
                print(f"  {line}")

            return step

        else:
            print("\n[OK] No more steps.")
            return None