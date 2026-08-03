import inspect
import json
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Metadata and JSON schema definition for registered agent tools."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]


class ToolExecutionResult(BaseModel):
    """Execution status and output payload from a tool call."""
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None


class AgentToolRegistry:
    """
    Mission 38: Autonomous Agentic Tool-Use Registry & Schema Validator.
    Manages registration, JSON argument validation, and safe dynamic tool execution.
    """

    def __init__(self):
        self._registry: Dict[str, Callable] = {}
        self._schemas: Dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        func: Callable
    ):
        """Registers a tool function alongside its JSON parameter schema validation definition."""
        self._registry[name] = func
        self._schemas[name] = ToolDefinition(
            name=name,
            description=description,
            parameters_schema=parameters_schema
        )

    def list_tools(self) -> List[ToolDefinition]:
        """Returns all registered tool schemas available for agent function calling."""
        return list(self._schemas.values())

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolExecutionResult:
        """
        Validates argument schema and safely executes the registered tool.
        """
        if tool_name not in self._registry:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=f"Tool '{tool_name}' is not registered in the tool registry."
            )

        # 1. Parameter schema validation
        schema = self._schemas[tool_name].parameters_schema
        validation_error = self._validate_arguments(arguments, schema)
        if validation_error:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=f"Schema Validation Error: {validation_error}"
            )

        # 2. Safe execution
        try:
            func = self._registry[tool_name]
            result = func(**arguments)
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                output=result,
                error=None
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=f"Tool Execution Exception: {str(e)}"
            )

    def _validate_arguments(self, args: Dict[str, Any], schema: Dict[str, Any]) -> Optional[str]:
        """Validates missing required fields and type match heuristics."""
        required = schema.get("required", [])
        for req in required:
            if req not in args:
                return f"Missing required parameter '{req}'."

        properties = schema.get("properties", {})
        for key, value in args.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "integer" and not isinstance(value, int):
                    return f"Parameter '{key}' expected type 'integer', got '{type(value).__name__}'."
                elif expected_type == "string" and not isinstance(value, str):
                    return f"Parameter '{key}' expected type 'string', got '{type(value).__name__}'."

        return None