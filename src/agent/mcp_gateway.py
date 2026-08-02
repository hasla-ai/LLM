import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPCapability(str, Enum):
    RESOURCES = "resources"
    TOOLS = "tools"
    PROMPTS = "prompts"


class MCPToolSchema(BaseModel):
    """Schema defining an MCP-compliant tool exposure."""
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Description of the tool function")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for parameters")


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 compliant MCP Protocol Request."""
    jsonrpc: str = Field(default="2.0")
    id: str = Field(..., description="Unique request ID")
    method: str = Field(..., description="MCP Protocol method (e.g. tools/list, tools/call)")
    params: Dict[str, Any] = Field(default_factory=dict)


class MCPExecutionResult(BaseModel):
    """Structured response payload for MCP executions."""
    request_id: str
    status: str = Field(..., description="'success', 'error', or 'denied'")
    content: Optional[Any] = None
    error_message: Optional[str] = None
    execution_latency_ms: float


class MCPProtocolGateway:
    """Enterprise Model Context Protocol (MCP) Server & Tool Integration Gateway."""

    def __init__(self, server_name: str = "llm-lab-mcp-server", version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version
        self._registered_tools: Dict[str, Dict[str, Any]] = {}
        self._capabilities: List[MCPCapability] = [
            MCPCapability.TOOLS,
            MCPCapability.RESOURCES,
        ]

    def register_tool(self, name: str, description: str, func: Callable, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Register a Python function as an MCP Tool."""
        self._registered_tools[name] = {
            "schema": MCPToolSchema(
                name=name,
                description=description,
                parameters=parameters or {},
            ),
            "func": func,
        }

    def list_tools(self) -> List[MCPToolSchema]:
        """List all exposed MCP tool schemas."""
        return [item["schema"] for item in self._registered_tools.values()]

    def handle_request(self, request: MCPRequest) -> MCPExecutionResult:
        """Process incoming MCP JSON-RPC requests."""
        start_time = time.time()

        if request.method == "initialize":
            latency = (time.time() - start_time) * 1000
            return MCPExecutionResult(
                request_id=request.id,
                status="success",
                content={
                    "server": self.server_name,
                    "version": self.version,
                    "capabilities": [cap.value for cap in self._capabilities],
                },
                execution_latency_ms=round(latency, 2),
            )

        elif request.method == "tools/list":
            latency = (time.time() - start_time) * 1000
            return MCPExecutionResult(
                request_id=request.id,
                status="success",
                content={"tools": [t.model_dump() for t in self.list_tools()]},
                execution_latency_ms=round(latency, 2),
            )

        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name or tool_name not in self._registered_tools:
                latency = (time.time() - start_time) * 1000
                return MCPExecutionResult(
                    request_id=request.id,
                    status="error",
                    error_message=f"Tool '{tool_name}' not registered on MCP Server.",
                    execution_latency_ms=round(latency, 2),
                )

            try:
                target_func = self._registered_tools[tool_name]["func"]
                res = target_func(**arguments)
                latency = (time.time() - start_time) * 1000
                return MCPExecutionResult(
                    request_id=request.id,
                    status="success",
                    content=res,
                    execution_latency_ms=round(latency, 2),
                )
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                return MCPExecutionResult(
                    request_id=request.id,
                    status="error",
                    error_message=str(e),
                    execution_latency_ms=round(latency, 2),
                )

        latency = (time.time() - start_time) * 1000
        return MCPExecutionResult(
            request_id=request.id,
            status="error",
            error_message=f"Unsupported MCP method '{request.method}'.",
            execution_latency_ms=round(latency, 2),
        )