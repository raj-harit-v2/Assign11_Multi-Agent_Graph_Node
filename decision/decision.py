import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
import re
from mcp_servers.multiMCP import MultiMCP
import ast
from core.plan_graph import PlanGraph, StepNode, CodeVariant, StepStatus
from perception.perception import PerceptionResult


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class Decision:
    def __init__(self, decision_prompt_path: str, multi_mcp: MultiMCP, api_key: str | None = None, model: str = "gemini-2.0-flash",  ):
        load_dotenv()
        self.decision_prompt_path = decision_prompt_path
        self.multi_mcp = multi_mcp

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or explicitly provided.")
        self.client = genai.Client(api_key=self.api_key)
        

    def run(self, decision_input: dict) -> dict:
        prompt_template = Path(self.decision_prompt_path).read_text(encoding="utf-8")
        function_list_text = self.multi_mcp.tool_description_wrapper()
        tool_descriptions = "\n".join(f"- `{desc.strip()}`" for desc in function_list_text)
        tool_descriptions = "\n\n### The ONLY Available Tools\n\n---\n\n" + tool_descriptions
        full_prompt = f"{prompt_template.strip()}\n{tool_descriptions}\n\n```json\n{json.dumps(decision_input, indent=2)}\n```"

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
        except ServerError as e:
            print(f"🚫 Decision LLM ServerError: {e}")
            return {
                "step_index": 0,
                "description": "Decision model unavailable: server overload.",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": ["Step 0: Decision model returned a 503. Exiting to avoid loop."],
                "raw_text": str(e)
            }

        raw_text = response.candidates[0].content.parts[0].text.strip()

        try:
            match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found")

            json_block = match.group(1)
            try:
                output = json.loads(json_block)
            except json.JSONDecodeError as e:
                print("[WARN] JSON decode failed, attempting salvage via regex...")

                # Attempt to extract a 'code' block manually
                code_match = re.search(r'code\s*:\s*"(.*?)"', json_block, re.DOTALL)
                code_value = bytes(code_match.group(1), "utf-8").decode("unicode_escape") if code_match else ""
                import pdb; pdb.set_trace()


                output = {
                    "step_index": 0,
                    "description": "Recovered partial JSON from LLM.",
                    "type": "CODE" if code_value else "NOP",
                    "code": code_value,
                    "conclusion": "",
                    "plan_text": ["Step 0: Partial plan recovered due to JSON decode error."],
                    "raw_text": raw_text[:1000]
                }

            # Handle flattened or nested format
            if "next_step" in output:
                output.update(output.pop("next_step"))

            defaults = {
                "step_index": 0,
                "description": "Missing from LLM response",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": ["Step 0: No valid plan returned by LLM."]
            }
            for key, default in defaults.items():
                output.setdefault(key, default)

            return output

        except Exception as e:
            import pdb; pdb.set_trace()
            print("❌ Unrecoverable exception while parsing LLM response:", str(e))
            return {
                "step_index": 0,
                "description": f"Exception while parsing LLM output: {str(e)}",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": ["Step 0: Exception occurred while processing LLM response."],
                "raw_text": raw_text[:1000]
            }

    def build_initial_plan_graph(self, user_query: str) -> PlanGraph:
        """
        Build initial plan graph with steps and code variants.
        
        Args:
            user_query: The user's query
        
        Returns:
            PlanGraph with initial steps
        """
        graph = PlanGraph()
        
        # Use decision module to generate plan
        decision_input = {
            "plan_mode": "initial",
            "original_query": user_query,
            "current_plan_version": 0,
            "current_plan": [],
            "completed_steps": [],
            "current_step": None
        }
        
        decision_output = self.run(decision_input)
        plan_text = decision_output.get("plan_text", [])
        
        # Parse plan_text to create steps
        # For now, create a simple 3-step plan with variants
        # In production, this would parse the plan_text more intelligently
        
        # Step 0: Initial data fetch
        step0_variants = [
            CodeVariant("0A", decision_output.get("code", "# Primary fetch method"), max_retries=1),
            CodeVariant("0B", "# Backup fetch method", max_retries=1),
            CodeVariant("0C", "# Alternative fetch method", max_retries=1)
        ]
        step0 = StepNode(
            index="0",
            description=decision_output.get("description", "Fetch initial data"),
            variants=step0_variants
        )
        graph.add_node(step0)
        graph.start_node_id = "0"
        graph.next_step_id = "0"
        
        # Step 1: Process data
        step1_variants = [
            CodeVariant("1A", "# Primary processing method", max_retries=1),
            CodeVariant("1B", "# Backup processing method", max_retries=1),
            CodeVariant("1C", "# Alternative processing method", max_retries=1)
        ]
        step1 = StepNode(
            index="1",
            description="Process retrieved data",
            variants=step1_variants
        )
        graph.add_node(step1)
        graph.add_edge("0", "1")
        
        # Step 2: Generate answer
        step2_variants = [
            CodeVariant("2A", "# Primary answer generation", max_retries=1),
            CodeVariant("2B", "# Backup answer generation", max_retries=1),
            CodeVariant("2C", "# Alternative answer generation", max_retries=1)
        ]
        step2 = StepNode(
            index="2",
            description="Generate final answer",
            variants=step2_variants
        )
        graph.add_node(step2)
        graph.add_edge("1", "2")
        
        return graph

    def add_fallback_node(self, graph: PlanGraph, failed_step_id: str) -> str:
        """
        Add a fallback node for a failed step.
        
        Args:
            graph: The plan graph
            failed_step_id: ID of the failed step
        
        Returns:
            ID of the created fallback node
        """
        # Generate fallback node ID
        fallback_id = f"{failed_step_id}F1"
        
        # Check if fallback already exists
        if graph.has_node(fallback_id):
            # If it exists, try F2, F3, etc.
            counter = 2
            while graph.has_node(f"{failed_step_id}F{counter}"):
                counter += 1
            fallback_id = f"{failed_step_id}F{counter}"
        
        # Create fallback node with single variant
        fallback_variant = CodeVariant(
            f"{fallback_id}A",
            "# Fallback execution method",
            max_retries=1
        )
        fallback_node = StepNode(
            index=fallback_id,
            description=f"Fallback for step {failed_step_id}",
            variants=[fallback_variant],
            is_fallback=True
        )
        
        graph.add_node(fallback_node)
        graph.add_edge(failed_step_id, fallback_id)
        
        return fallback_id

    def select_next_node(
        self, 
        graph: PlanGraph, 
        current_node_id: str, 
        perception: PerceptionResult
    ) -> Optional[str]:
        """
        Select the next node to execute based on graph topology and perception.
        
        Args:
            graph: The plan graph
            current_node_id: Current node ID
            perception: Perception result
        
        Returns:
            Next node ID or None if execution should stop
        """
        current_node = graph.get_node(current_node_id)
        if not current_node:
            return None
        
        # If current node failed, check for fallback
        if current_node.status == StepStatus.FAILED:
            children = graph.get_children(current_node_id)
            # Look for fallback nodes (those starting with current_node_id + "F")
            for child_id in children:
                child_node = graph.get_node(child_id)
                if child_node and child_node.is_fallback:
                    return child_id
        
        # Otherwise, get first child
        children = graph.get_children(current_node_id)
        if children:
            return children[0]
        
        # No children, execution complete
        return None





