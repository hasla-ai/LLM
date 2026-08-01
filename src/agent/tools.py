import math
from typing import Dict, Any, Callable

def calculate_math_expression(expression: str) -> str:
    """Safely evaluates basic mathematical expressions."""
    try:
        # Simple arithmetic evaluator
        allowed_names = {"sqrt": math.sqrt, "pow": pow, "abs": abs}
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of '{name}' is not allowed.")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Math Evaluation Error: {str(e)}"

# Registry of tools available to the Agent
TOOL_REGISTRY: Dict[str, Callable[[str], str]] = {
    "calculator": calculate_math_expression,
}