import time
import pytest
from src.eval.telemetry_tracer import (
    LLMTelemetryCollector,
    ObservabilityTracer,
    SpanStatus,
)


def test_span_lifecycle_and_duration():
    tracer = ObservabilityTracer()
    tracer.start_trace()

    with tracer.trace("llm_inference", {"model": "gpt-4o"}) as span:
        time.sleep(0.01)
        span.prompt_tokens = 100
        span.completion_tokens = 50

    recorded_spans = tracer.collector.spans
    assert len(recorded_spans) == 1
    assert recorded_spans[0].name == "llm_inference"
    assert recorded_spans[0].status == SpanStatus.OK
    assert recorded_spans[0].duration_ms > 0
    assert recorded_spans[0].prompt_tokens == 100


def test_nested_span_hierarchy():
    tracer = ObservabilityTracer()
    tracer.start_trace()

    with tracer.trace("agent_pipeline") as parent_span:
        with tracer.trace("vector_search") as child_span_1:
            pass
        with tracer.trace("llm_generation") as child_span_2:
            pass

    spans = tracer.collector.spans
    assert len(spans) == 3

    # child_span_1 and child_span_2 finish first, parent finishes last
    parent = [s for s in spans if s.name == "agent_pipeline"][0]
    children = [s for s in spans if s.name != "agent_pipeline"]

    assert len(children) == 2
    for child in children:
        assert child.parent_span_id == parent.span_id


def test_error_span_recording():
    tracer = ObservabilityTracer()

    with pytest.raises(ValueError):
        with tracer.trace("failing_operation"):
            raise ValueError("API Connection Timeout")

    spans = tracer.collector.spans
    assert len(spans) == 1
    assert spans[0].status == SpanStatus.ERROR
    assert "API Connection Timeout" in spans[0].error_message


def test_telemetry_metrics_aggregation():
    collector = LLMTelemetryCollector()
    tracer = ObservabilityTracer(collector)

    with tracer.trace("op_1") as s1:
        s1.prompt_tokens = 200
        s1.completion_tokens = 50

    with tracer.trace("op_2") as s2:
        s2.prompt_tokens = 300
        s2.completion_tokens = 100

    metrics = collector.get_summary_metrics()
    assert metrics["total_spans"] == 2
    assert metrics["error_count"] == 0
    assert metrics["prompt_tokens"] == 500
    assert metrics["completion_tokens"] == 150
    assert metrics["total_tokens"] == 650