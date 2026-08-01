from unittest.mock import MagicMock
from src.agent.agent_engine import AgentEngine, AgentAction
from src.agent.tools import calculate_math_expression

def test_math_tool_execution():
    """Verify tool behavior independently."""
    assert calculate_math_expression("2 + 2 * 5") == "12"
    assert calculate_math_expression("sqrt(16)") == "4.0"

def test_agent_tool_calling_loop_with_mock():
    """Verify agent loop: Tool Call -> Observation -> Final Answer."""
    mock_llm = MagicMock()

    # Step 1 response: Agent calls the calculator tool
    step1_action = AgentAction(
        thought="I need to calculate 15 * 4.",
        tool_name="calculator",
        tool_input="15 * 4",
        final_answer=None
    )

    # Step 2 response: Agent provides the final answer
    step2_action = AgentAction(
        thought="I have the calculation result.",
        tool_name=None,
        tool_input=None,
        final_answer="15 multiplied by 4 equals 60."
    )

    # Return sequence of AgentActions
    mock_llm.generate_structured.side_effect = [step1_action, step2_action]

    agent = AgentEngine(llm_client=mock_llm, max_steps=3)
    final_output = agent.run("What is 15 times 4?")

    assert final_output == "15 multiplied by 4 equals 60."
    assert mock_llm.generate_structured.call_count == 2