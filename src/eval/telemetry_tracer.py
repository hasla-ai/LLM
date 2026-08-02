import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SpanStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


class TraceSpan(BaseModel):
    """Represents an OpenTelemetry-compatible span in an LLM execution trace."""
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: SpanStatus = SpanStatus.OK
    attributes: Dict[str, Any] = Field(default_factory=dict)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error_message: Optional[str] = None

    def finish(self, status: SpanStatus = SpanStatus.OK, error_message: Optional[str] = None) -> None:
        """Concludes the span execution and calculates duration in milliseconds."""
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        self.error_message = error_message


class TraceContext:
    """Context manager for tracing operations with automatic span lifecycle management."""

    def __init__(self, tracer: "ObservabilityTracer", name: str, attributes: Optional[Dict[str, Any]] = None):
        self.tracer = tracer
        self.name = name
        self.attributes = attributes or {}
        self.span: Optional[TraceSpan] = None

    def __enter__(self) -> TraceSpan:
        self.span = self.tracer.start_span(self.name, self.attributes)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.tracer.end_span(self.span, status=SpanStatus.ERROR, error_message=str(exc_val))
        else:
            self.tracer.end_span(self.span, status=SpanStatus.OK)


class LLMTelemetryCollector:
    """Aggregates metrics and traces across execution spans."""

    def __init__(self):
        self.spans: List[TraceSpan] = []

    def record_span(self, span: TraceSpan) -> None:
        """Stores completed span in the telemetry registry."""
        self.spans.append(span)

    def get_total_tokens(self) -> Dict[str, int]:
        """Calculates total prompt and completion tokens across all spans."""
        total_prompt = sum(s.prompt_tokens for s in self.spans)
        total_completion = sum(s.completion_tokens for s in self.spans)
        return {
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
        }

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates aggregated execution statistics."""
        durations = [s.duration_ms for s in self.spans if s.duration_ms is not None]
        errors = [s for s in self.spans if s.status == SpanStatus.ERROR]
        tokens = self.get_total_tokens()

        avg_latency = sum(durations) / len(durations) if durations else 0.0

        return {
            "total_spans": len(self.spans),
            "error_count": len(errors),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": tokens["total_tokens"],
            "prompt_tokens": tokens["prompt_tokens"],
            "completion_tokens": tokens["completion_tokens"],
        }


class ObservabilityTracer:
    """Orchestrates trace contexts and exports trace spans to the collector."""

    def __init__(self, collector: Optional[LLMTelemetryCollector] = None):
        self.collector = collector or LLMTelemetryCollector()
        self.current_trace_id: Optional[str] = None
        self.span_stack: List[TraceSpan] = []

    def start_trace(self) -> str:
        """Starts a new trace hierarchy."""
        self.current_trace_id = str(uuid.uuid4())
        self.span_stack = []
        return self.current_trace_id

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> TraceSpan:
        """Creates a new active span under the current trace hierarchy."""
        if not self.current_trace_id:
            self.start_trace()

        parent_span_id = self.span_stack[-1].span_id if self.span_stack else None

        span = TraceSpan(
            trace_id=self.current_trace_id,
            parent_span_id=parent_span_id,
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
        )
        self.span_stack.append(span)
        return span

    def end_span(
        self,
        span: TraceSpan,
        status: SpanStatus = SpanStatus.OK,
        error_message: Optional[str] = None,
    ) -> None:
        """Concludes the span and pushes it to the telemetry collector."""
        span.finish(status=status, error_message=error_message)
        if self.span_stack and self.span_stack[-1].span_id == span.span_id:
            self.span_stack.pop()

        self.collector.record_span(span)

    def trace(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> TraceContext:
        """Helper to create a trace context manager block."""
        return TraceContext(self, name, attributes)