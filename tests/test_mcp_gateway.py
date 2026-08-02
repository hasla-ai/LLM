import pytest
from src.agent.mcp_gateway import MCPProtocolGateway, MCPRequest


def dummy_calculator(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def mcp_gateway():
    gateway = MCPProtocolGateway()
    gateway.register_tool(
        name="add_numbers",
        description="Add two integers together",
        func=dummy_calculator,
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    )
    return gateway


def test_mcp_initialization(mcp_gateway):
    req = MCPRequest(id="req-1", method="initialize")
    res = mcp_gateway.handle_request(req)
    assert res.status == "success"
    assert res.content["server"] == "llm-lab-mcp-server"


def test_mcp_list_tools(mcp_gateway):
    req = MCPRequest(id="req-2", method="tools/list")
    res = mcp_gateway.handle_request(req)
    assert res.status == "success"
    assert len(res.content["tools"]) == 1
    assert res.content["tools"][0]["name"] == "add_numbers"


def test_mcp_call_tool_success(mcp_gateway):
    req = MCPRequest(
        id="req-3",
        method="tools/call",
        params={"name": "add_numbers", "arguments": {"a": 10, "b": 25}},
    )
    res = mcp_gateway.handle_request(req)
    assert res.status == "success"
    assert res.content == 35


def test_mcp_call_tool_not_found(mcp_gateway):
    req = MCPRequest(
        id="req-4",
        method="tools/call",
        params={"name": "unknown_tool", "arguments": {}},
    )
    res = mcp_gateway.handle_request(req)
    assert res.status == "error"
    assert "not registered" in res.error_message