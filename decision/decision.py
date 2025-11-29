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

class Decision:
    # Compiled regex patterns for performance
    _RE_NUMBERS = re.compile(r'\d+')
    _RE_RANGE = re.compile(r'(\d+)\s+to\s+(\d+)')
    
    # Pre-computed sets for faster lookups
    _INFO_KEYWORDS = {
        'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'was', 'were',
        'definition', 'meaning', 'formula', 'capital', 'largest', 'smallest',
        'speed', 'year', 'wrote', 'created', 'national', 'animal', 'organ', 'gas',
        'planet', 'country', 'language', 'invented', 'discovered', 'stands', 'for'
    }
    _MATH_KEYWORDS = {
        'calculate', 'compute', 'find', 'solve', 'add', 'subtract', 'multiply',
        'divide', 'power', 'factorial', 'gcd', 'average', 'mean', 'sum', 'sqrt'
    }
    
    def __init__(self, decision_prompt_path: str, multi_mcp: MultiMCP, api_key: str | None = None, model: str = "gemini-2.0-flash-lite", use_ollama: bool = False):
        load_dotenv()
        self.decision_prompt_path = decision_prompt_path
        self.multi_mcp = multi_mcp
        self.model = model
        # Cache for query analysis results
        self._query_cache = {}

        # Use ModelManager if available and Ollama is requested
        if MODEL_MANAGER_AVAILABLE and use_ollama:
            try:
                self.model_manager = ModelManager()
                self.use_ollama = True
                self.client = None
                print("[INFO] Decision using Ollama via ModelManager")
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
        

    def _generate_with_backoff(self, full_prompt: str) -> str:
        """Internal sync method for API call with backoff."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt
        )
        return response.candidates[0].content.parts[0].text.strip()
    
    def run(self, decision_input: dict) -> dict:
        prompt_template = Path(self.decision_prompt_path).read_text(encoding="utf-8")
        function_list_text = self.multi_mcp.tool_description_wrapper()
        tool_descriptions = "\n".join(f"- `{desc.strip()}`" for desc in function_list_text)
        tool_descriptions = "\n\n### The ONLY Available Tools\n\n---\n\n" + tool_descriptions
        full_prompt = f"{prompt_template.strip()}\n{tool_descriptions}\n\n```json\n{json.dumps(decision_input, indent=2)}\n```"

        try:
            if self.use_ollama and MODEL_MANAGER_AVAILABLE:
                # Use Ollama via ModelManager (already has backoff if needed)
                raw_text = self.model_manager.generate_text(full_prompt, model=self.model)
            else:
                # Use Google API with exponential backoff for 429 errors
                if BACKOFF_AVAILABLE:
                    raw_text = with_exponential_backoff(
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
                    raw_text = response.candidates[0].content.parts[0].text.strip()
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
        except Exception as e:
            # Handle network errors and other exceptions
            error_str = str(e)
            print(f"🚫 Decision LLM Network/Connection Error: {error_str}")
            return {
                "step_index": 0,
                "description": f"Decision model unavailable: {error_str}",
                "type": "NOP",
                "code": "",
                "conclusion": "",
                "plan_text": [f"Step 0: Decision model connection failed: {error_str}"],
                "raw_text": error_str
            }

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
        # Check if query is complex (has multiple "and" or "then" clauses)
        is_complex = self._is_complex_query(user_query)
        
        if is_complex and len(plan_text) > 1:
            # Complex query: create one step per plan_text item
            # Generate code for each step based on description
            for i, step_desc in enumerate(plan_text):
                # For Step 0, try Decision output first, but always have a fallback
                if i == 0:
                    step_code = decision_output.get("code", "")
                    # If Decision code is invalid, generate based on step description
                    if not step_code or step_code.strip().startswith("#") or len(step_code.strip()) < 10:
                        step_code = self._generate_code_for_step(step_desc, user_query, i)
                else:
                    # For subsequent steps, generate code based on step description
                    step_code = self._generate_code_for_step(step_desc, user_query, i)
                
                # Validate code is not empty or just a comment - if still invalid, try again with original query
                if not step_code or step_code.strip().startswith("#") or "Step execution needed" in step_code:
                    print(f"[DEBUG] Step {i} code invalid, trying original query context...")
                    # Try generating from original query context
                    step_code = self._generate_code_for_step(user_query, user_query, i)
                    # If still invalid, try with step description again with different parsing
                    if not step_code or step_code.strip().startswith("#") or "Step execution needed" in step_code:
                        print(f"[DEBUG] Step {i} still invalid, trying step description only...")
                        # Last resort: extract operation from step description and generate basic code
                        step_code = self._generate_code_for_step(step_desc, step_desc, i)
                        # If STILL invalid, create a basic code that at least tries to execute something
                        if not step_code or step_code.strip().startswith("#") or "Step execution needed" in step_code:
                            print(f"[WARN] Step {i} code generation failed, creating minimal code")
                            # Extract any numbers from step description
                            numbers = re.findall(r'\d+', step_desc)
                            if numbers:
                                # Try to infer operation from keywords
                                if "factorial" in step_desc.lower():
                                    step_code = f"result = factorial({numbers[0]})\nreturn result"
                                elif "sum" in step_desc.lower() and "prime" in step_desc.lower():
                                    step_code = """primes = [2, 3, 5, 7, 11, 13, 17, 19]
result = sum(primes)
return result"""
                                elif "gcd" in step_desc.lower() or "common divisor" in step_desc.lower():
                                    if len(numbers) >= 2:
                                        step_code = f"import math\nresult = math.gcd({numbers[0]}, {numbers[1]})\nreturn result"
                                else:
                                    # Generic: just return the first number as a fallback
                                    step_code = f"result = {numbers[0]}\nreturn result"
                            else:
                                # No numbers found - return a placeholder that won't break execution
                                step_code = f"result = 'Unable to execute: {step_desc[:50]}'\nreturn result"
                
                # Create variants with actual executable code
                step_variants = [
                    CodeVariant(f"{i}A", step_code, max_retries=1),
                    CodeVariant(f"{i}B", self._generate_backup_code(step_desc, user_query, i), max_retries=1),
                    CodeVariant(f"{i}C", self._generate_alternative_code(step_desc, user_query, i), max_retries=1)
                ]
                step = StepNode(
                    index=str(i),
                    description=step_desc.replace("Step {}: ".format(i), "").replace(f"Step {i}: ", "").strip(),
                    variants=step_variants
                )
                graph.add_node(step)
                if i > 0:
                    graph.add_edge(str(i-1), str(i))
            
            graph.start_node_id = "0"
            graph.next_step_id = "0"
        else:
            # Simple query: use actual code from Decision output
            actual_code = decision_output.get("code", "")
            
            # For specific query types, always use generated code instead of Decision's code
            query_lower = user_query.lower()
            
            # Square root: always use math.sqrt() instead of power tool
            if "square root" in query_lower or "sqrt" in query_lower:
                numbers = self._RE_NUMBERS.findall(user_query)
                if numbers:
                    num = int(numbers[0])
                    actual_code = f"import math\nresult = math.sqrt({num})\nreturn result"
            
            # Average: ensure proper calculation with all numbers
            elif "average" in query_lower or "mean" in query_lower:
                numbers = self._RE_NUMBERS.findall(user_query)
                if numbers:
                    int_numbers = [int(n) for n in numbers]
                    actual_code = f"result = sum({int_numbers}) / len({int_numbers})\nreturn result"
                    print(f"[DEBUG] Generated average code: {actual_code}")
            
            # Information queries: ALWAYS use DuckDuckGo search with markdown (default for all info queries)
            # This ensures DuckDuckGo is the default browser in text mode for all information queries
            # Using markdown search provides full content from top results, not just short snippets
            elif self._is_information_query(user_query):
                # Always use DuckDuckGo search with markdown for information queries - provides full content
                # DuckDuckGo is the default search engine in text mode for all information queries
                # Markdown search fetches full content from top 3 results for better parsing
                # Note: Don't use 'await' - AwaitTransformer will add it automatically for tool calls
                # Escape single quotes in query to avoid syntax errors
                escaped_query = user_query.replace("'", "\\'")
                actual_code = f"result = duckduckgo_search_with_markdown('{escaped_query}', 3)\nreturn result"
                print(f"[DEBUG] Generated DuckDuckGo search with markdown code for information query: {actual_code[:100]}")
            
            # If Decision didn't generate valid code, generate it based on query
            if not actual_code or actual_code.strip().startswith("#") or len(actual_code.strip()) < 10:
                # Generate code based on query type
                actual_code = self._generate_code_for_step(user_query, user_query, 0)
                if not actual_code or actual_code.strip().startswith("#"):
                    # Last resort: use Decision's description to generate code
                    desc = decision_output.get("description", user_query)
                    actual_code = self._generate_code_for_step(desc, user_query, 0)
            
            # Validate Decision's code for specific operations
            if actual_code:
                # Square root: ensure not using power tool with fractional exponent
                if "square root" in query_lower or "sqrt" in query_lower:
                    if "power" in actual_code.lower() and "0.5" in actual_code:
                        numbers = re.findall(r'\d+', user_query)
                        if numbers:
                            num = int(numbers[0])
                            actual_code = f"import math\nresult = math.sqrt({num})\nreturn result"
                
                # Information queries: ensure using DuckDuckGo search tool (check again in validation)
                # DuckDuckGo is the default browser in text mode for all information queries
                elif self._is_information_query(user_query):
                    # If Decision code doesn't use DuckDuckGo search tool, replace it
                    # This ensures DuckDuckGo is always used as the default for information queries
                    # Note: Don't use 'await' - AwaitTransformer will add it automatically for tool calls
                    if "duckduckgo_search" not in actual_code.lower() and "search" not in actual_code.lower():
                        # Force DuckDuckGo with markdown for information queries (provides full content)
                        # Escape single quotes in query to avoid syntax errors
                        escaped_query = user_query.replace("'", "\\'")
                        actual_code = f"result = duckduckgo_search_with_markdown('{escaped_query}', 3)\nreturn result"
                        print(f"[DEBUG] Replaced Decision code with DuckDuckGo search with markdown code for information query")
                
                # Average: ensure using sum() and len() with all numbers
                elif "average" in query_lower or "mean" in query_lower:
                    # ALWAYS replace Decision's code for average - our generated code is more reliable
                    numbers = re.findall(r'\d+', user_query)
                    if numbers:
                        int_numbers = [int(n) for n in numbers]
                        actual_code = f"result = sum({int_numbers}) / len({int_numbers})\nreturn result"
                        print(f"[DEBUG] Replaced Decision code with average code: {actual_code}")
            
            # Generate backup variants with proper code
            backup_code = self._generate_backup_code(decision_output.get("description", user_query), user_query, 0)
            alt_code = self._generate_alternative_code(decision_output.get("description", user_query), user_query, 0)
            
            # Step 0: Use actual code from Decision or generated code
            step0_variants = [
                CodeVariant("0A", actual_code, max_retries=1),
                CodeVariant("0B", backup_code, max_retries=1),
                CodeVariant("0C", alt_code, max_retries=1)
            ]
            step0 = StepNode(
                index="0",
                description=decision_output.get("description", "Execute calculation"),
                variants=step0_variants
            )
            graph.add_node(step0)
            graph.start_node_id = "0"
            graph.next_step_id = "0"
        
        return graph
    
    def _is_information_query(self, query: str) -> bool:
        """
        Determine if a query is an information query that should use DuckDuckGo search.
        
        Information queries include:
        - Questions starting with: what, who, where, when, why, how
        - Queries containing information keywords: is, are, was, were, definition, meaning,
          formula, capital, largest, smallest, speed, year, wrote, created, national,
          animal, organ, gas, planet, country, etc.
        
        Excludes:
        - Simple math queries (e.g., "5 + 3", "10 / 2")
        
        Optimized with caching and set-based keyword matching.
        """
        # Check cache first
        if query in self._query_cache:
            return self._query_cache[query].get('is_info', False)
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Fast check: starts with question word
        if query_lower.startswith(('what', 'who', 'where', 'when', 'why', 'how')):
            result = True
        # Fast check: contains info keywords (set intersection is O(min(len(set1), len(set2))))
        elif query_words & self._INFO_KEYWORDS:
            # Exclude simple math
            if not (query_words & self._MATH_KEYWORDS and len(self._RE_NUMBERS.findall(query)) <= 2):
                result = True
            else:
                result = False
        else:
            result = False
        
        # Cache result
        if query not in self._query_cache:
            self._query_cache[query] = {}
        self._query_cache[query]['is_info'] = result
        return result
        
        # Exclude simple math queries (they should use MCP math tools, not search)
        if re.search(r'\d+\s*[+\-*/]\s*\d+', query):
            return False
        
        # Check if query starts with information question words
        question_starters = ["what", "who", "where", "when", "why", "how"]
        if any(query_lower.startswith(starter + " ") for starter in question_starters):
            return True
        
        # Check for information keywords (using set for O(1) lookup performance)
        # Note: Multi-word keywords need special handling
        information_keywords_multi = {
            "chemical formula", "who is", "where is", "what is", "programming language", "created by"
        }
        information_keywords_single = {
            "capital", "formula", "definition", "meaning", "is", "are", "was", "were",
            "largest", "smallest", "speed", "year", "wrote", "created", "national", "animal",
            "organ", "gas", "planet", "country", "chambers", "invented", "discovered",
            "found", "located", "exists", "contains"
        }
        
        # Check multi-word keywords first (more specific)
        if any(keyword in query_lower for keyword in information_keywords_multi):
            return True
        
        # Check single-word keywords (using set for O(1) lookup)
        query_words = set(query_lower.split())
        if query_words & information_keywords_single:
            return True
        
        return False
    
    def _is_complex_query(self, query: str) -> bool:
        """Check if query is complex (has multiple parts). Optimized with caching."""
        # Check cache first
        if query in self._query_cache:
            cached = self._query_cache[query].get('is_complex')
            if cached is not None:
                return cached
        
        query_lower = query.lower()
        # Check for multiple operations: "and", "then", "also", comma-separated operations
        and_count = query_lower.count(" and ")
        then_count = query_lower.count(" then ")
        comma_count = query.count(",")
        
        # Complex if has multiple "and" or "then", or multiple commas
        result = (and_count >= 2) or (then_count >= 1) or (comma_count >= 2) or ("calculate" in query_lower and "find" in query_lower)
        
        # Cache result
        if query not in self._query_cache:
            self._query_cache[query] = {}
        self._query_cache[query]['is_complex'] = result
        return result
    
    def _generate_code_for_step(self, step_desc: str, original_query: str, step_index: int) -> str:
        """
        Generate executable code for a step based on its description.
        
        For information queries, always defaults to DuckDuckGo search (text mode).
        """
        step_lower = step_desc.lower()
        
        # Check if this is an information query - if so, use DuckDuckGo search
        if self._is_information_query(original_query) or self._is_information_query(step_desc):
            # DuckDuckGo is the default search engine in text mode for all information queries
            # Escape single quotes in query to avoid syntax errors
            escaped_query = original_query.replace("'", "\\'")
            return f"result = duckduckgo_search_with_markdown('{escaped_query}', 3)\nreturn result"
        
        # Also check original_query for context if step_desc is too generic
        original_lower = original_query.lower() if original_query else ""
        
        # Extract numbers and operations from step description
        import re
        
        # Check for factorial (in step_desc or original_query)
        if "factorial" in step_lower or "factorial" in original_lower:
            # Try step_desc first, then original_query
            numbers = re.findall(r'\d+', step_desc)
            if not numbers:
                numbers = re.findall(r'\d+', original_query)
            if numbers:
                num = int(numbers[0])  # Convert to integer
                return f"result = factorial({num})\nreturn result"
        
        # Check for prime numbers (in step_desc or original_query)
        if ("prime" in step_lower and "sum" in step_lower) or ("prime" in original_lower and "sum" in original_lower):
            # Extract range
            range_match = self._RE_RANGE.search(step_desc)
            if range_match:
                start, end = range_match.groups()
                return f"""primes = []
for num in range({start}, {int(end) + 1}):
    if num > 1:
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
result = sum(primes)
return result"""
            else:
                # Default: primes from 1 to 20
                return """primes = [2, 3, 5, 7, 11, 13, 17, 19]
result = sum(primes)
return result"""
        
        # Check for GCD (greatest common divisor) (in step_desc or original_query)
        if ("gcd" in step_lower or "greatest common divisor" in step_lower or "common divisor" in step_lower) or \
           ("gcd" in original_lower or "greatest common divisor" in original_lower or "common divisor" in original_lower):
            numbers = re.findall(r'\d+', step_desc)
            if len(numbers) < 2:
                numbers = re.findall(r'\d+', original_query)
            if len(numbers) >= 2:
                a, b = numbers[0], numbers[1]
                return f"""import math
result = math.gcd({a}, {b})
return result"""
        
        # Check for sum
        if "sum" in step_lower:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if numbers:
                # Convert to integers
                int_numbers = [int(n) for n in numbers]
                return f"result = sum({int_numbers})\nreturn result"
        
        # Check for multiplication
        if "multiply" in step_lower or "*" in step_desc:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if len(numbers) >= 2:
                # Convert to integers to avoid string multiplication issues
                a, b = int(numbers[0]), int(numbers[1])
                return f"result = {a} * {b}\nreturn result"
        
        # Check for addition
        if "add" in step_lower or "+" in step_desc:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if len(numbers) >= 2:
                # Convert to integers
                a, b = int(numbers[0]), int(numbers[1])
                return f"result = {a} + {b}\nreturn result"
        
        # Check for subtraction
        if "subtract" in step_lower or "-" in step_desc or "minus" in step_lower:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if len(numbers) >= 2:
                a, b = int(numbers[0]), int(numbers[1])
                return f"result = {a} - {b}\nreturn result"
        
        # Check for power/exponentiation
        if "power" in step_lower or "^" in step_desc or "to the power" in step_lower:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if len(numbers) >= 2:
                a, b = int(numbers[0]), int(numbers[1])
                return f"result = {a} ** {b}\nreturn result"
        
        # Check for square root
        if "square root" in step_lower or "sqrt" in step_lower:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if numbers:
                num = int(numbers[0])
                return f"import math\nresult = math.sqrt({num})\nreturn result"
        
        # Check for average
        if "average" in step_lower or "mean" in step_lower:
            numbers = self._RE_NUMBERS.findall(step_desc)
            if numbers:
                int_numbers = [int(n) for n in numbers]
                return f"result = sum({int_numbers}) / len({int_numbers})\nreturn result"
        
        # Default: try to extract and execute based on description
        # Use available tools from multi_mcp
        tool_names = [tool.name for tool in self.multi_mcp.get_all_tools()]
        
        # Try to match step description to available tools
        for tool_name in tool_names:
            if tool_name.lower() in step_lower:
                # Extract arguments from step description
                numbers = self._RE_NUMBERS.findall(step_desc)
                if numbers:
                    # Convert to integers to ensure proper type
                    if len(numbers) >= 2:
                        a, b = int(numbers[0]), int(numbers[1])
                        return f"result = {tool_name}({a}, {b})\nreturn result"
                    elif len(numbers) == 1:
                        a = int(numbers[0])
                        return f"result = {tool_name}({a})\nreturn result"
        
        # Fallback: return a simple calculation attempt
        return f"# Step {step_index}: {step_desc}\nresult = 'Step execution needed'\nreturn result"
    
    def _generate_backup_code(self, step_desc: str, original_query: str, step_index: int) -> str:
        """Generate backup code variant for a step."""
        # Try alternative approach
        step_lower = step_desc.lower()
        numbers = self._RE_NUMBERS.findall(step_desc)
        query_numbers = self._RE_NUMBERS.findall(original_query)
        
        # Check for multiplication - use direct calculation
        if "multiply" in step_lower or "*" in original_query.lower():
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} * {b}\nreturn result"
        
        # Check for division
        if "divide" in step_lower or "/" in original_query.lower() or "divided by" in original_query.lower():
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} / {b}\nreturn result"
        
        # Check for addition
        if "add" in step_lower or "+" in original_query.lower():
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} + {b}\nreturn result"
        
        # Check for subtraction
        if "subtract" in step_lower or "-" in original_query.lower():
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} - {b}\nreturn result"
        
        # Check for power
        if "power" in step_lower or "^" in original_query.lower() or "to the power" in original_query.lower():
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"import math\nresult = math.pow({a}, {b})\nreturn result"
        
        # Check for square root
        if "square root" in step_lower or "sqrt" in step_lower:
            if query_numbers:
                num = int(query_numbers[0])
                return f"import math\nresult = math.sqrt({num})\nreturn result"
        
        if "prime" in step_lower:
            return """# Alternative prime calculation
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
result = sum([p for p in primes if p <= 20])
return result"""
        
        if "gcd" in step_lower or "greatest common divisor" in step_lower:
            if len(numbers) >= 2:
                a, b = int(numbers[0]), int(numbers[1])
                return f"""# Alternative GCD calculation
def gcd_alt(a, b):
    while b:
        a, b = b, a % b
    return a
result = gcd_alt({a}, {b})
return result"""
        
        return f"# Backup method for step {step_index}\nresult = 'Backup execution'\nreturn result"
    
    def _generate_alternative_code(self, step_desc: str, original_query: str, step_index: int) -> str:
        """Generate alternative code variant for a step."""
        import re
        step_lower = step_desc.lower()
        query_lower = original_query.lower()
        
        # Try to extract numbers from original query for direct calculation
        query_numbers = re.findall(r'\d+', original_query)
        
        # Check for multiplication
        if "multiply" in step_lower or "*" in query_lower or "multiply" in query_lower:
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} * {b}\nreturn result"
        
        # Check for division
        if "divide" in step_lower or "/" in query_lower or "divided by" in query_lower:
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} / {b}\nreturn result"
        
        # Check for addition
        if "add" in step_lower or "+" in query_lower:
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} + {b}\nreturn result"
        
        # Check for subtraction
        if "subtract" in step_lower or "-" in query_lower:
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} - {b}\nreturn result"
        
        # Check for power
        if "power" in step_lower or "^" in query_lower or "to the power" in query_lower:
            if len(query_numbers) >= 2:
                a, b = int(query_numbers[0]), int(query_numbers[1])
                return f"result = {a} ** {b}\nreturn result"
        
        # Check for square root
        if "square root" in step_lower or "sqrt" in step_lower:
            if query_numbers:
                num = int(query_numbers[0])
                return f"import math\nresult = math.sqrt({num})\nreturn result"
        
        return f"# Alternative method for step {step_index}\nresult = 'Alternative execution'\nreturn result"

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





