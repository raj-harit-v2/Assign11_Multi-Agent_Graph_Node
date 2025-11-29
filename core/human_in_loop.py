"""
Human-In-Loop Module for Session 10
Handles user interaction when tools fail or plans need modification.
"""

import json
from typing import Optional
from core.user_plan_storage import UserPlanStorage


def ask_user_for_tool_result(context: dict) -> str:
    """
    Ask user to provide result when a tool fails.
    
    Args:
        context: Dictionary containing:
            - tool_name: Name of the failed tool
            - error_message: Error that occurred
            - step_description: Description of the step
            - query: Original user query
    
    Returns:
        str: User-provided result/answer
    """
    print("\n" + "=" * 60)
    print("HUMAN-IN-LOOP: Tool Failure")
    print("=" * 60)
    print(f"Tool: {context.get('tool_name', 'Unknown')}")
    print(f"Error: {context.get('error_message', 'Unknown error')}")
    print(f"Step: {context.get('step_description', 'Unknown step')}")
    print(f"Query: {context.get('query', 'Unknown query')}")
    print("\nThe tool failed. Please provide the result/answer manually:")
    print("-" * 60)
    
    # Handle non-interactive mode (e.g., during automated tests)
    try:
        user_input = input("Your answer: ").strip()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode - return default error message
        error_msg = context.get('error_message', 'Unknown error')
        step_desc = context.get('step_description', 'Unknown step')
        default_result = f"Tool execution failed: {error_msg}. Step: {step_desc}. No user input available (non-interactive mode)."
        print(f"\n[WARNING] Non-interactive mode detected. Using default result.")
        print(f"Default result: {default_result[:100]}...")
        return default_result
    
    if not user_input:
        print("Warning: Empty input received. Using default: 'Tool failed, no user input provided'")
        return "Tool failed, no user input provided"
    
    print(f"Accepted user input: {user_input[:100]}...")
    return user_input


def ask_user_for_plan(context: dict, suggested_plan: list, session_id: str = None) -> tuple[list, Optional[dict]]:
    """
    Ask user to modify or approve a plan when plan fails.
    
    Args:
        context: Dictionary containing:
            - reason: Why the plan failed
            - current_plan: Current plan that failed
            - step_count: Number of steps executed
            - max_steps: Maximum allowed steps
            - query: Original user query
        suggested_plan: List of plan steps suggested by the agent
        session_id: Session identifier for storing user plan
    
    Returns:
        tuple: (plan_list, user_plan_dict)
            - plan_list: User-approved/modified plan (list of step descriptions)
            - user_plan_dict: Parsed JSON plan if provided, None otherwise
    """
    print("\n" + "=" * 60)
    print("HUMAN-IN-LOOP: Plan Failure")
    print("=" * 60)
    print(f"Reason: {context.get('reason', 'Plan execution failed')}")
    print(f"Steps executed: {context.get('step_count', 0)}")
    print(f"Max steps allowed: {context.get('max_steps', 3)}")
    print(f"Query: {context.get('query', 'Unknown query')}")
    print("\nCurrent plan that failed:")
    if context.get('current_plan'):
        for i, step in enumerate(context.get('current_plan', []), 1):
            print(f"  {i}. {step}")
    else:
        print("  (No previous plan)")
    
    print("\n[AGENT] Agent's suggested new plan:")
    for i, step in enumerate(suggested_plan, 1):
        print(f"  {i}. {step}")
    print("\n[LISTENING] Agent is listening for your input...")
    
    print("\nOptions:")
    print("  1. Accept suggested plan (press Enter)")
    print("  2. Modify plan (type 'modify' then enter new plan steps, one per line)")
    print("  3. Provide custom plan (type 'custom' then enter plan steps, one per line)")
    print("  4. Provide JSON plan (type 'json' then paste JSON with final_answer, etc.)")
    print("-" * 60)
    
    # Handle non-interactive mode (e.g., during automated tests)
    try:
        choice = input("Your choice: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode - accept suggested plan
        print("\n[WARNING] Non-interactive mode detected. Accepting suggested plan.")
        return suggested_plan, None
    
    if choice == "json":
        print("\nEnter JSON plan (with final_answer, original_goal_achieved, etc.):")
        print("Example: {\"original_goal_achieved\": true, \"final_answer\": \"...\", ...}")
        json_input = input("  > ").strip()
        
        # Try to parse JSON
        user_plan_dict = UserPlanStorage.parse_user_input(json_input)
        if user_plan_dict:
            print("\n[PARSED] JSON plan parsed successfully:")
            print(f"  Final Answer: {user_plan_dict.get('final_answer', 'N/A')[:100]}")
            print(f"  Goal Achieved: {user_plan_dict.get('original_goal_achieved', False)}")
            
            # Store user plan for this session (will be used in next lifeline)
            if session_id:
                UserPlanStorage.store_user_plan(session_id, user_plan_dict)
            
            # Convert to plan list format
            final_answer = user_plan_dict.get('final_answer', '')
            plan_list = [final_answer] if final_answer else suggested_plan
            
            return plan_list, user_plan_dict
        else:
            print("[WARNING] Could not parse JSON. Using suggested plan.")
            return suggested_plan, None
    
    if choice == "modify" or choice == "custom":
        print("\nEnter your plan steps (one per line). Type 'END' on a new line to finish:")
        custom_plan = []
        while True:
            line = input("  > ").strip()
            if line.upper() == "END":
                break
            if line:
                custom_plan.append(line)
        
        if custom_plan:
            print(f"\nAccepted custom plan with {len(custom_plan)} steps:")
            for i, step in enumerate(custom_plan, 1):
                print(f"  {i}. {step}")
            return custom_plan, None
        else:
            print("No steps provided. Using suggested plan.")
            return suggested_plan, None
    
    # Default: accept suggested plan
    print("\nAccepted suggested plan.")
    return suggested_plan, None

