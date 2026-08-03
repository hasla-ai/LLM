import unittest
from src.sandbox.self_correction_engine import (
    SelfCorrectionEngine,
    ExecutionResult,
)


class TestSelfCorrectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SelfCorrectionEngine(max_attempts=3)

    def test_successful_execution_first_try(self):
        def mock_sandbox_pass(code: str) -> ExecutionResult:
            return ExecutionResult(success=True, stdout="Output: 42")

        success, final_code, history = self.engine.execute_with_correction_loop(
            "print(42)", mock_sandbox_pass
        )

        self.assertTrue(success)
        self.assertEqual(len(history), 0)

    def test_self_correction_loop_recovery(self):
        attempt_counter = 0

        def mock_sandbox_fail_then_pass(code: str) -> ExecutionResult:
            nonlocal attempt_counter
            attempt_counter += 1
            if attempt_counter < 2:
                return ExecutionResult(
                    success=False,
                    stderr="ZeroDivisionError: division by zero",
                    error_type="ZeroDivisionError",
                )
            return ExecutionResult(success=True, stdout="Fixed!")

        success, final_code, history = self.engine.execute_with_correction_loop(
            "x = 1 / 0", mock_sandbox_fail_then_pass
        )

        self.assertTrue(success)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].execution_result.error_type, "ZeroDivisionError")


if __name__ == "__main__":
    unittest.main()