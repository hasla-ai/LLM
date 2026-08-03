import unittest
import time
from src.agent.agent_circuit_breaker import (
    AgentCircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)


class TestAgentCircuitBreaker(unittest.TestCase):
    def setUp(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout_sec=0.2,
            half_open_success_threshold=1
        )
        self.breaker = AgentCircuitBreaker(name="llm_agent_service", config=config)

    def test_normal_execution(self):
        res = self.breaker.execute_with_fallback(
            primary_fn=lambda: "primary_ok",
            fallback_fn=lambda: "fallback_ok"
        )
        self.assertEqual(res, "primary_ok")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_tripping_to_open_and_fallback(self):
        def failing_primary():
            raise RuntimeError("API Timeout")

        # 1st failure
        self.breaker.execute_with_fallback(failing_primary, lambda: "fallback_used")
        # 2nd failure -> Trips circuit to OPEN
        res = self.breaker.execute_with_fallback(failing_primary, lambda: "fallback_used")

        self.assertEqual(res, "fallback_used")
        self.assertEqual(self.breaker.state, CircuitState.OPEN)

    def test_recovery_half_open_to_closed(self):
        def failing_primary():
            raise RuntimeError("API Timeout")

        # Trip to OPEN
        self.breaker.execute_with_fallback(failing_primary, lambda: "fb")
        self.breaker.execute_with_fallback(failing_primary, lambda: "fb")
        self.assertEqual(self.breaker.state, CircuitState.OPEN)

        # Wait for recovery timeout
        time.sleep(0.25)

        # Primary succeeds in HALF_OPEN state -> Recovers to CLOSED
        res = self.breaker.execute_with_fallback(
            primary_fn=lambda: "recovered_primary",
            fallback_fn=lambda: "fb"
        )
        self.assertEqual(res, "recovered_primary")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)


if __name__ == "__main__":
    unittest.main()