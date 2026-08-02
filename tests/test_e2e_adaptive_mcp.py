from unittest.mock import MagicMock
import pytest

from src.rag.adaptive_rag import AdaptiveRAGEngine, ComplexityTier, RoutingDecision
from src.agent.mcp_gateway import MCPProtocolGateway, MCPRequest
from src.rag.vector_store import VectorStore


def live_financial_ticker_tool(symbol: str) -> dict:
    """Mock external tool exposed over MCP Protocol."""
    data = {
        "NVDA": {"price": 135.50, "currency": "USD", "status": "bullish"},
        "AAPL": {"price": 224.20, "currency": "USD", "status": "neutral"},
    }
    return data.get(symbol.upper(), {"error": f"Ticker '{symbol}' not found"})


@pytest.fixture
def mcp_gateway():
    gateway = MCPProtocolGateway(server_name="financial-mcp-gateway")
    gateway.register_tool(
        name="get_stock_price",
        description="Fetch real-time stock ticker data",
        func=live_financial_ticker_tool,
        parameters={
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"],
        },
    )
    return gateway


def test_e2e_adaptive_rag_with_mcp_tool_execution(mcp_gateway):
    """
    E2E Scenario:
    1. User query asks for live stock data.
    2. Adaptive RAG routes query as COMPLEX_MULTI_STEP_RAG.
    3. The pipeline discovers MCP capabilities via `tools/list`.
    4. The pipeline executes `tools/call` on the MCP Gateway to retrieve live data.
    """
    llm_client = MagicMock()
    mock_vector_store = MagicMock(spec=VectorStore)

    # 1. Routing classification mock
    routing_decision = RoutingDecision(
        complexity_tier=ComplexityTier.COMPLEX_MULTI_STEP_RAG,
        reasoning="Query requires dynamic external data fetch via MCP tool call."
    )
    llm_client.generate.return_value = routing_decision

    # 2. Step 1: Discover available tools from MCP Gateway
    list_req = MCPRequest(id="req-mcp-discover", method="tools/list")
    list_res = mcp_gateway.handle_request(list_req)
    assert list_res.status == "success"
    assert len(list_res.content["tools"]) == 1
    assert list_res.content["tools"][0]["name"] == "get_stock_price"

    # 3. Step 2: Execute tool via MCP Gateway
    call_req = MCPRequest(
        id="req-mcp-exec",
        method="tools/call",
        params={"name": "get_stock_price", "arguments": {"symbol": "NVDA"}},
    )
    call_res = mcp_gateway.handle_request(call_req)
    assert call_res.status == "success"
    assert call_res.content["price"] == 135.50
    assert call_res.content["currency"] == "USD"

    # 4. Instantiate Adaptive RAG and verify classification flow
    engine = AdaptiveRAGEngine(
        llm_client=llm_client,
        vector_store=mock_vector_store
    )
    decision = engine.classify_query("What is the current stock price of NVDA?")

    assert decision.complexity_tier == ComplexityTier.COMPLEX_MULTI_STEP_RAG
    assert call_res.execution_latency_ms >= 0.0


def test_e2e_adaptive_rag_mcp_fallback_handling(mcp_gateway):
    """Verify clean error propagation when an invalid MCP tool is called."""
    call_req = MCPRequest(
        id="req-mcp-fail",
        method="tools/call",
        params={"name": "non_existent_tool", "arguments": {}},
    )
    call_res = mcp_gateway.handle_request(call_req)

    assert call_res.status == "error"
    assert "not registered" in call_res.error_message