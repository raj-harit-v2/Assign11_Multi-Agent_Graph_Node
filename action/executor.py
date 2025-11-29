
import ast
import asyncio
import time
import builtins
import textwrap
import re
from typing import Tuple, Optional, Any
from datetime import datetime
from core.control_manager import ControlManager
from core.human_in_loop import ask_user_for_tool_result
from core.plan_graph import CodeVariant, StepNode
from core.context_manager import ContextManager

# ───────────────────────────────────────────────────────────────
# CONFIG
# ───────────────────────────────────────────────────────────────
ALLOWED_MODULES = {
    "math", "cmath", "decimal", "fractions", "random", "statistics", "itertools", "functools", "operator", "string", "re", "datetime", "calendar", "time", "collections", "heapq", "bisect", "types", "copy", "enum", "uuid", "dataclasses", "typing", "pprint", "json", "base64", "hashlib", "hmac", "secrets", "struct", "zlib", "gzip", "bz2", "lzma", "io", "pathlib", "tempfile", "textwrap", "difflib", "unicodedata", "html", "html.parser", "xml", "xml.etree.ElementTree", "csv", "sqlite3", "contextlib", "traceback", "ast", "tokenize", "token", "builtins"
}
MAX_FUNCTIONS = 5
TIMEOUT_PER_FUNCTION = 500  # seconds

class KeywordStripper(ast.NodeTransformer):
    """Rewrite all function calls to remove keyword args and keep only values as positional."""
    def visit_Call(self, node):
        self.generic_visit(node)
        if node.keywords:
            # Convert all keyword arguments into positional args (discard names)
            for kw in node.keywords:
                node.args.append(kw.value)
            node.keywords = []
        return node


# ───────────────────────────────────────────────────────────────
# AST TRANSFORMER: auto-await known async MCP tools
# ───────────────────────────────────────────────────────────────
class AwaitTransformer(ast.NodeTransformer):
    def __init__(self, async_funcs):
        self.async_funcs = async_funcs

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.async_funcs:
            return ast.Await(value=node)
        return node

# ───────────────────────────────────────────────────────────────
# AST TRANSFORMER: Convert string number literals to ints in tool calls
# ───────────────────────────────────────────────────────────────
class IntLiteralTransformer(ast.NodeTransformer):
    """Convert string literals that are numbers to integers in function calls."""
    def __init__(self, tool_names):
        self.tool_names = tool_names
    
    def visit_Call(self, node):
        self.generic_visit(node)
        # Check if this is a tool call
        if isinstance(node.func, ast.Name) and node.func.id in self.tool_names:
            # Convert string number arguments to integers
            new_args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    # Try to convert string to int if it's a number
                    try:
                        int_value = int(arg.value)
                        new_args.append(ast.Constant(value=int_value))
                    except ValueError:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            node.args = new_args
        return node

# ───────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ───────────────────────────────────────────────────────────────
def count_function_calls(code: str) -> int:
    tree = ast.parse(code)
    return sum(isinstance(node, ast.Call) for node in ast.walk(tree))

def build_safe_globals(mcp_funcs: dict, multi_mcp=None) -> dict:
    safe_globals = {
        "__builtins__": {
            k: getattr(builtins, k)
            for k in ("range", "len", "int", "float", "str", "list", "dict", "print", "sum", "__import__")
        },
        **mcp_funcs,
    }

    for module in ALLOWED_MODULES:
        safe_globals[module] = __import__(module)

    # Store LLM-style result
    safe_globals["final_answer"] = lambda x: safe_globals.setdefault("result_holder", x)

    # Optional: add parallel execution
    if multi_mcp:
        async def parallel(*tool_calls):
            coros = [
                multi_mcp.function_wrapper(tool_name, *args)
                for tool_name, *args in tool_calls
            ]
            try:
                return await asyncio.gather(*coros, return_exceptions=True)
            except ExceptionGroup as eg:
                # Handle ExceptionGroup from gather - extract first error
                if eg.exceptions:
                    raise eg.exceptions[0]  # Re-raise first exception
                raise

        safe_globals["parallel"] = parallel

    return safe_globals


# ───────────────────────────────────────────────────────────────
# MAIN EXECUTOR
# ───────────────────────────────────────────────────────────────
async def run_user_code(code: str, multi_mcp, step_description: str = "", query: str = "", completed_steps: list = None) -> dict:
    """
    Execute user code with retry logic and human-in-loop on failure.
    
    Args:
        code: Code to execute
        multi_mcp: MultiMCP instance
        step_description: Description of the step (for human-in-loop context)
        query: Original query (for human-in-loop context)
        completed_steps: List of completed steps with their execution results
    
    Returns:
        dict: Execution result with status, result/error, retry_count
    """
    if completed_steps is None:
        completed_steps = []
    control_manager = ControlManager()
    max_retries = control_manager.get_max_retries()
    
    start_time = time.perf_counter()
    start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    retry_count = 0
    last_error = None
    
    # Retry loop
    while retry_count < max_retries:
        try:
            func_count = count_function_calls(code)
            if func_count > MAX_FUNCTIONS:
                return {
                    "status": "error",
                    "error": f"Too many functions ({func_count} > {MAX_FUNCTIONS})",
                    "execution_time": start_timestamp,
                    "total_time": str(round(time.perf_counter() - start_time, 3)),
                    "retry_count": retry_count
                }

            tool_funcs = {
                tool.name: make_tool_proxy(tool.name, multi_mcp)
                for tool in multi_mcp.get_all_tools()
            }

            sandbox = build_safe_globals(tool_funcs, multi_mcp)
            # Add completed_steps to sandbox for code execution context
            sandbox["completed_steps"] = completed_steps
            local_vars = {}

            cleaned_code = textwrap.dedent(code.strip())
            
            # Validate code is not empty
            if not cleaned_code or not cleaned_code.strip():
                raise ValueError("Generated code is empty. Decision module may have failed to generate valid code.")
            
            tree = ast.parse(cleaned_code)
            
            # Validate tree has body
            if not tree.body:
                raise ValueError("Parsed code has no statements. Decision module generated invalid code.")

            has_return = any(isinstance(node, ast.Return) for node in tree.body)
            has_result = any(
                isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "result" for t in node.targets
                )
                for node in tree.body
            )
            if not has_return and has_result:
                tree.body.append(ast.Return(value=ast.Name(id="result", ctx=ast.Load())))

            tree = KeywordStripper().visit(tree) # strip "key" = "value" cases to only "value"
            # Convert string number literals to integers in tool calls
            tool_names = set(tool_funcs.keys())
            tree = IntLiteralTransformer(tool_names).visit(tree)
            tree = AwaitTransformer(tool_names).visit(tree)
            ast.fix_missing_locations(tree)
            
            # Double-check body is not empty after transformations
            if not tree.body:
                raise ValueError("Code body is empty after AST transformations.")

            func_def = ast.AsyncFunctionDef(
                name="__main",
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=tree.body,
                decorator_list=[]
            )
            wrapper = ast.Module(body=[func_def], type_ignores=[])
            ast.fix_missing_locations(wrapper)

            compiled = compile(wrapper, filename="<user_code>", mode="exec")
            exec(compiled, sandbox, local_vars)

            timeout = max(3, func_count * TIMEOUT_PER_FUNCTION)  # minimum 3s even for plain returns
            returned = await asyncio.wait_for(local_vars["__main"](), timeout=timeout)

            result_value = returned if returned is not None else sandbox.get("result_holder", "None")

            # If result looks like tool error text, extract
            # Handle CallToolResult errors from MCP
            if hasattr(result_value, "isError") and getattr(result_value, "isError", False):
                error_msg = None

                try:
                    error_msg = result_value.content[0].text.strip()
                except Exception:
                    error_msg = str(result_value)

                last_error = error_msg
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Tool error: {error_msg}. Retrying ({retry_count}/{max_retries})...")
                    await asyncio.sleep(1)
                    continue
                else:
                    break

            # Else: normal success
            return {
                "status": "success",
                "result": str(result_value),
                "execution_time": start_timestamp,
                "total_time": str(round(time.perf_counter() - start_time, 3)),
                "retry_count": retry_count
            }

        except asyncio.TimeoutError:
            last_error = f"Execution timed out after {func_count * TIMEOUT_PER_FUNCTION} seconds"
            retry_count += 1
            if retry_count < max_retries:
                print(f"Timeout occurred. Retrying ({retry_count}/{max_retries})...")
                await asyncio.sleep(1)  # Brief delay before retry
                continue
            else:
                break
        except ExceptionGroup as eg:
            # Handle ExceptionGroup (Python 3.11+) - extract first meaningful error
            # Note: Using regular 'except' instead of 'except*' to avoid mixing syntax
            last_error = f"ExceptionGroup: {len(eg.exceptions)} error(s)"
            if eg.exceptions:
                first_exc = eg.exceptions[0]
                last_error = f"{type(first_exc).__name__}: {str(first_exc)}"
            retry_count += 1
            if retry_count < max_retries:
                print(f"Error occurred: {last_error}. Retrying ({retry_count}/{max_retries})...")
                await asyncio.sleep(1)  # Brief delay before retry
                continue
            else:
                break
        except Exception as e:
            last_error = f"{type(e).__name__}: {str(e)}"
            retry_count += 1
            if retry_count < max_retries:
                print(f"Error occurred: {last_error}. Retrying ({retry_count}/{max_retries})...")
                await asyncio.sleep(1)  # Brief delay before retry
                continue
            else:
                break
    
    # All retries exhausted - trigger human-in-loop
    if last_error:
        print(f"\nAll {max_retries} retries exhausted. Error: {last_error}")
        context = {
            "tool_name": "code_executor",
            "error_message": last_error,
            "step_description": step_description,
            "query": query
        }
        user_result = ask_user_for_tool_result(context)
        
        return {
            "status": "success",  # Treat user input as success
            "result": user_result,
            "execution_time": start_timestamp,
            "total_time": str(round(time.perf_counter() - start_time, 3)),
            "retry_count": retry_count,
            "human_provided": True
        }
    
    # Fallback error
    return {
        "status": "error",
        "error": last_error or "Unknown error",
        "execution_time": start_timestamp,
        "total_time": str(round(time.perf_counter() - start_time, 3)),
        "retry_count": retry_count
    }

# ───────────────────────────────────────────────────────────────
# TOOL WRAPPER
# ───────────────────────────────────────────────────────────────
def make_tool_proxy(tool_name: str, mcp):
    async def _tool_fn(*args):
        return await mcp.function_wrapper(tool_name, *args)
    return _tool_fn


# ───────────────────────────────────────────────────────────────
# CODE VARIANT EXECUTION (V2)
# ───────────────────────────────────────────────────────────────
async def run_code_variant(
    variant: CodeVariant, 
    context: ContextManager,
    multi_mcp,
    step_description: str = "",
    query: str = "",
    completed_steps: list = None
) -> Tuple[bool, Any, Optional[str]]:
    """
    Execute a single code variant.
    
    Args:
        variant: CodeVariant to execute
        context: ContextManager for tracking
        multi_mcp: MultiMCP instance
        step_description: Description of the step
        query: Original query
        completed_steps: List of completed steps
    
    Returns:
        Tuple of (success: bool, result: Any, error: Optional[str])
    """
    if completed_steps is None:
        completed_steps = []
    
    # Increment retry count
    variant.retries += 1
    
    # Execute the code
    result = await run_user_code(
        variant.source,
        multi_mcp,
        step_description=step_description,
        query=query,
        completed_steps=completed_steps
    )
    
    if result.get("status") == "success":
        return True, result.get("result"), None
    else:
        error = result.get("error", "Unknown error")
        return False, None, error


async def execute_step(
    node: StepNode,
    context: ContextManager,
    multi_mcp,
    step_description: str = "",
    query: str = "",
    completed_steps: list = None
) -> dict:
    """
    Execute a step node with code variants (A/B/C retry logic).
    
    Args:
        node: StepNode to execute
        context: ContextManager for tracking
        multi_mcp: MultiMCP instance
        step_description: Description of the step
        query: Original query
        completed_steps: List of completed steps
    
    Returns:
        dict: Execution result with variant tracking
    """
    if completed_steps is None:
        completed_steps = []
    
    variants_tried = []
    last_error = None
    
    # Try each variant in order
    for variant in node.variants:
        variants_tried.append(variant.name)
        
        success, result, error = await run_code_variant(
            variant,
            context,
            multi_mcp,
            step_description=node.description,
            query=query,
            completed_steps=completed_steps
        )
        
        if success:
            # Success - register result and update globals
            globals_delta = {"last_result": result, "last_node": node.index}
            context.register_step_result(
                node.index,
                True,
                result,
                globals_delta=globals_delta,
                error=None
            )
            
            return {
                "status": "success",
                "result": result,
                "variants_tried": variants_tried,
                "variant_succeeded": variant.name,
                "node_id": node.index
            }
        
        last_error = error
    
    # All variants failed
    context.register_step_result(
        node.index,
        False,
        None,
        error=last_error
    )
    
    return {
        "status": "error",
        "error": last_error or "All variants failed",
        "variants_tried": variants_tried,
        "node_id": node.index
    }