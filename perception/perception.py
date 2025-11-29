import os
import json
import uuid
import datetime
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from core.plan_graph import Route
import sys
from pathlib import Path as PathLib

# Add utils to path for ModelManager and backoff
project_root = PathLib(__file__).parent.parent
sys.path.insert(0, str(project_root))
try:
    from utils.model_manager import ModelManager
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False

try:
    from utils.backoff import with_exponential_backoff
    BACKOFF_AVAILABLE = True
except ImportError:
    BACKOFF_AVAILABLE = False

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


@dataclass
class PerceptionResult:
    """Result from perception layer with routing decision."""
    route: Route
    goal_met: bool
    instruction_to_summarize: Optional[str] = None
    notes: str = ""

class Perception:
    def __init__(self, perception_prompt_path: str, api_key: str | None = None, model: str = "gemini-2.0-flash-lite", use_ollama: bool = False):
        load_dotenv()
        self.perception_prompt_path = perception_prompt_path
        self.model = model
        
        # Use ModelManager if available and Ollama is requested
        if MODEL_MANAGER_AVAILABLE and use_ollama:
            try:
                self.model_manager = ModelManager()
                self.use_ollama = True
                self.client = None
                print("[INFO] Perception using Ollama via ModelManager")
            except Exception as e:
                print(f"[WARN] Failed to initialize Ollama, falling back to Google API: {e}")
                self.use_ollama = False
                self.api_key = api_key or os.getenv("GEMINI_API_KEY")
                if not self.api_key:
                    raise ValueError("GEMINI_API_KEY not found and Ollama unavailable.")
                self.client = genai.Client(api_key=self.api_key)
        else:
            self.use_ollama = False
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment or explicitly provided.")
            self.client = genai.Client(api_key=self.api_key)

    def build_perception_input(self, raw_input: str, memory: list, current_plan = "", snapshot_type: str = "user_query") -> dict:
        if memory:
            memory_excerpt = {
                f"memory_{i+1}": {
                    "query": res["query"],
                    "result_requirement": res["result_requirement"],
                    "solution_summary": res["solution_summary"]
                }
                for i, res in enumerate(memory)}
        else:
            memory_excerpt = {}

        return {
            "run_id": str(uuid.uuid4()),
            "snapshot_type": snapshot_type,
            "raw_input": raw_input,
            "memory_excerpt": memory_excerpt,
            "prev_objective": "",
            "prev_confidence": None,
            "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "schema_version": 1,
            "current_plan" : current_plan or "Inain Query Mode, plan not created"
        }
    
    def _generate_with_backoff(self, full_prompt: str):
        """Internal sync method for API call with backoff."""
        return self.client.models.generate_content(
            model=self.model,
            contents=full_prompt
        )
    
    def run(self, perception_input: dict) -> dict:
        """Run perception on given input using the specified prompt file."""
        prompt_template = Path(self.perception_prompt_path).read_text(encoding="utf-8")
        full_prompt = f"{prompt_template.strip()}\n\n```json\n{json.dumps(perception_input, indent=2)}\n```"

        try:
            if self.use_ollama and MODEL_MANAGER_AVAILABLE:
                # Use Ollama via ModelManager (already has backoff if needed)
                response_text = self.model_manager.generate_text(full_prompt)
                # Create a mock response object for compatibility
                class MockResponse:
                    def __init__(self, text):
                        self.text = text
                response = MockResponse(response_text)
            else:
                # Use Google API with exponential backoff for 429 errors
                if BACKOFF_AVAILABLE:
                    response = with_exponential_backoff(
                        self._generate_with_backoff,
                        full_prompt,
                        max_retries=3,
                        initial_delay=1.0,
                        max_delay=60.0,
                        backoff_multiplier=2.0
                    )
                else:
                    # Fallback without backoff
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=full_prompt
                    )
        except ServerError as e:
            print(f"🚫 Perception LLM ServerError: {e}")
            return {
                "step_index": 0,
                "description": "Perception model unavailable: server overload.",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": ["Step 0: Perception model returned a 503. Exiting to avoid loop."],
                "raw_text": str(e),
                "entities": [],
                "result_requirement": "N/A",
                "original_goal_achieved": False,
                "reasoning": f"Perception API error: {str(e)}",
                "local_goal_achieved": False,
                "local_reasoning": "Could not connect to perception service.",
                "solution_summary": "Not ready yet",
                "confidence": "0.0"
            }
        except Exception as e:
            # Catch network errors (getaddrinfo failed, connection errors, etc.)
            error_str = str(e)
            print(f"🚫 Perception LLM Network/Connection Error: {error_str}")
            return {
                "step_index": 0,
                "description": f"Perception model unavailable: {error_str}",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": [f"Step 0: Perception model connection failed: {error_str}"],
                "raw_text": error_str,
                "entities": [],
                "result_requirement": "N/A",
                "original_goal_achieved": False,
                "reasoning": f"Network/Connection error: {error_str}",
                "local_goal_achieved": False,
                "local_reasoning": f"Could not connect to perception service: {error_str}",
                "solution_summary": "Not ready yet",
                "confidence": "0.0"
            }

        raw_text = response.text.strip()

        try:
            # Try to extract JSON block
            if "```json" in raw_text:
                json_block = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                # Try without json marker
                json_block = raw_text.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON object in the text - use compiled pattern
                if not hasattr(Perception, '_RE_JSON_OBJECT'):
                    import re
                    Perception._RE_JSON_OBJECT = re.compile(r'\{.*\}', re.DOTALL)
                json_match = Perception._RE_JSON_OBJECT.search(raw_text)
                if json_match:
                    json_block = json_match.group(0).strip()
                else:
                    raise ValueError("No JSON block found in response")

            # Try to parse JSON with error handling and fallback strategies
            output = None
            try:
                output = json.loads(json_block)
            except json.JSONDecodeError as e:
                print(f"❌ EXCEPTION IN PERCEPTION: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback 1: Try to fix common JSON issues
                try:
                    # Remove trailing commas before closing braces/brackets
                    fixed_json = re.sub(r',(\s*[}\]])', r'\1', json_block)
                    output = json.loads(fixed_json)
                    print("✅ Fixed JSON by removing trailing commas")
                except:
                    # Fallback 2: Try to extract just the essential fields
                    try:
                        # Extract key-value pairs manually
                        import re
                        # Try to find route
                        route_match = re.search(r'"route"\s*:\s*"([^"]+)"', json_block, re.IGNORECASE)
                        route = route_match.group(1) if route_match else "DECISION"
                        
                        # Try to find goal_met
                        goal_match = re.search(r'"original_goal_achieved"\s*:\s*(true|false)', json_block, re.IGNORECASE)
                        goal_met = goal_match.group(1).lower() == "true" if goal_match else False
                        
                        # Try to find reasoning
                        reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]+)"', json_block, re.IGNORECASE)
                        reasoning = reasoning_match.group(1) if reasoning_match else "JSON parsing failed, using fallback"
                        
                        # Create minimal output
                        output = {
                            "route": route,
                            "original_goal_achieved": goal_met,
                            "reasoning": reasoning,
                            "entities": [],
                            "result_requirement": "N/A",
                            "local_goal_achieved": goal_met,
                            "local_reasoning": reasoning,
                            "last_tooluse_summary": "None",
                            "solution_summary": "JSON parsing failed",
                            "confidence": "0.5"
                        }
                        print("✅ Created fallback JSON from regex extraction")
                    except Exception as fallback_error:
                        print(f"❌ Fallback extraction also failed: {fallback_error}")
                        # Last resort: return default structure
                        output = {
                            "route": "DECISION",
                            "original_goal_achieved": False,
                            "reasoning": f"JSON parsing failed: {str(e)}",
                            "entities": [],
                            "result_requirement": "N/A",
                            "local_goal_achieved": False,
                            "local_reasoning": "JSON parsing failed",
                            "last_tooluse_summary": "None",
                            "solution_summary": "Not ready yet",
                            "confidence": "0.0"
                        }
                        print("✅ Using default fallback structure")

            # ✅ Patch missing fields for PerceptionSnapshot
            required_fields = {
                "entities": [],
                "result_requirement": "No requirement specified.",
                "original_goal_achieved": False,
                "reasoning": "No reasoning given.",
                "local_goal_achieved": False,
                "local_reasoning": "No local reasoning given.",
                "last_tooluse_summary": "None",
                "solution_summary": "No summary.",
                "confidence": "0.0"
            }

            for key, default in required_fields.items():
                output.setdefault(key, default)

            return output

        except Exception as e:
            # Log error without breaking execution
            print("❌ EXCEPTION IN PERCEPTION:", e)
            import traceback
            traceback.print_exc()
            return {
                "entities": [],
                "result_requirement": "N/A",
                "original_goal_achieved": False,
                "reasoning": "Perception failed to parse model output as JSON.",
                "local_goal_achieved": False,
                "local_reasoning": "Could not extract structured information.",
                "solution_summary": "Not ready yet",
                "confidence": "0.0"
            }

    def perceive_root(self, user_query: str, memory: list = None) -> PerceptionResult:
        """
        Analyze root user query and determine routing.
        
        Args:
            user_query: The user's query
            memory: Optional memory results from search
        
        Returns:
            PerceptionResult with route decision
        """
        if memory is None:
            memory = []
        
        # Build perception input
        perception_input = self.build_perception_input(
            raw_input=user_query,
            memory=memory,
            snapshot_type="user_query"
        )
        
        # Run perception
        result = self.run(perception_input)
        
        # Determine route based on goal achievement
        goal_met = result.get("original_goal_achieved", False)
        
        # Only mark as goal_met if we have actual memory with a good match
        # If no memory, force execution even if LLM says goal is met
        if goal_met and memory and len(memory) > 0:
            # Check if memory has a good match (has solution_summary)
            has_good_memory = any(
                match.get("solution_summary") or match.get("summary")
                for match in memory
            )
            if has_good_memory:
                return PerceptionResult(
                    route=Route.SUMMARIZE,
                    goal_met=True,
                    instruction_to_summarize="Produce concise answer from available information",
                    notes=result.get("reasoning", "Goal already achieved")
                )
        
        # If no memory or LLM says goal not met, force execution
        goal_met = False
        
        # Otherwise route to decision for planning
        return PerceptionResult(
            route=Route.DECISION,
            goal_met=False,
            notes=result.get("reasoning", "Initial perception completed")
        )

    def perceive_step_output(
        self, 
        step_id: str, 
        output: str, 
        context: dict = None
    ) -> PerceptionResult:
        """
        Analyze step execution output and determine routing.
        
        Args:
            step_id: ID of the step that was executed
            output: Output from step execution
            context: Optional context information
        
        Returns:
            PerceptionResult with route decision
        """
        if context is None:
            context = {}
        
        # Build perception input for step output
        perception_input = self.build_perception_input(
            raw_input=f"Step {step_id} output: {output}",
            memory=[],
            snapshot_type="step_output"
        )
        
        # Run perception
        result = self.run(perception_input)
        
        # Determine route based on goal achievement
        goal_met = result.get("original_goal_achieved", False)
        
        # If goal is met, route to summarize
        if goal_met:
            return PerceptionResult(
                route=Route.SUMMARIZE,
                goal_met=True,
                instruction_to_summarize=result.get("solution_summary", "Produce final answer"),
                notes=result.get("reasoning", "Goal achieved after step execution")
            )
        
        # Otherwise continue with decision/execution
        return PerceptionResult(
            route=Route.DECISION,
            goal_met=False,
            notes=result.get("reasoning", "Continue execution")
        )


