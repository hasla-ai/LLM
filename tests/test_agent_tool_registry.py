import unittest
from src.agent.agent_tool_registry import AgentToolRegistry


class TestAgentToolRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = AgentToolRegistry()

        # Dummy tool
        def calculate_sum(a: int, b: int) -> int:
            return a + b

        self.registry.register_tool(
            name="calculate_sum",
            description="Adds two integers.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            },
            func=calculate_sum
        )

    def test_tool_registration_and_listing(self):
        tools = self.registry.list_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "calculate_sum")

    def test_successful_tool_execution(self):
        res = self.registry.execute_tool("calculate_sum", {"a": 10, "b": 20})
        self.assertTrue(res.success)
        self.assertEqual(res.output, 30)

    def test_missing_required_argument_validation(self):
        res = self.registry.execute_tool("calculate_sum", {"a": 10})
        self.assertFalse(res.success)
        self.assertIn("Missing required parameter 'b'", res.error)

    def test_type_mismatch_argument_validation(self):
        res = self.registry.execute_tool("calculate_sum", {"a": "invalid_str", "b": 20})
        self.assertFalse(res.success)
        self.assertIn("expected type 'integer'", res.error)


if __name__ == "__main__":
    unittest.main()