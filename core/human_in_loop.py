"""
Human-In-Loop Module for Session 10
Handles user interaction when tools fail or plans need modification.
"""


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
    
    user_input = input("Your answer: ").strip()
    
    if not user_input:
        print("Warning: Empty input received. Using default: 'Tool failed, no user input provided'")
        return "Tool failed, no user input provided"
    
    print(f"Accepted user input: {user_input[:100]}...")
    return user_input


def ask_user_for_plan(context: dict, suggested_plan: list) -> list:
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
    
    Returns:
        list: User-approved/modified plan (list of step descriptions)
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
    
    print("\nSuggested new plan:")
    for i, step in enumerate(suggested_plan, 1):
        print(f"  {i}. {step}")
    
    print("\nOptions:")
    print("  1. Accept suggested plan (press Enter)")
    print("  2. Modify plan (type 'modify' then enter new plan steps, one per line)")
    print("  3. Provide custom plan (type 'custom' then enter plan steps, one per line)")
    print("-" * 60)
    
    choice = input("Your choice: ").strip().lower()
    
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
            return custom_plan
        else:
            print("No steps provided. Using suggested plan.")
            return suggested_plan
    
    # Default: accept suggested plan
    print("\nAccepted suggested plan.")
    return suggested_plan

