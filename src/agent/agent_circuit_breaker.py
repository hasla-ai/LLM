import enum
import time
from typing import Callable, Any, Dict, Optional
from pydantic import BaseModel, Field


class CircuitState(str, enum.Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Tripped: Requests immediately fail or divert to fallback
    HALF_OPEN = "half_open" # Testing recovery with limited traffic


class CircuitBreakerConfig(BaseModel):
    failure_threshold: int = 3         # Consecutively failed attempts before tripping
    recovery_timeout_sec: float = 10.0 # Time to wait before entering HALF_OPEN state
    half_open_success_threshold: int = 2


class AgentCircuitBreaker:
    """
    Mission 32: Self-Healing Agent Circuit Breaker & Fallback Mesh.
    Prevents cascading agent/tool failure loops and routes calls to fallback providers.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig = CircuitBreakerConfig()):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_state_change = time.time()

    def execute_with_fallback(
        self,
        primary_fn: Callable[[], Any],
        fallback_fn: Callable[[], Any]
    ) -> Any:
        """
        Executes primary_fn through the circuit breaker logic.
        Diverts to fallback_fn if the circuit is OPEN or primary_fn fails.
        """
        self._check_state_transition()

        if self.state == CircuitState.OPEN:
            return fallback_fn()

        try:
            result = primary_fn()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            return fallback_fn()

    def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.config.half_open_success_threshold:
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
                self.consecutive_successes = 0
                self.last_state_change = time.time()
        else:
            self.consecutive_failures = 0

    def _on_failure(self) -> None:
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        if self.consecutive_failures >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def _check_state_transition(self) -> None:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_state_change >= self.config.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                self.last_state_change = time.time()