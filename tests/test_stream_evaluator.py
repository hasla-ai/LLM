import unittest
from src.eval.stream_evaluator import (
    RealTimeStreamEvaluator,
    StreamSafetyStatus,
)


class TestRealTimeStreamEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = RealTimeStreamEvaluator(
            hallucination_threshold=0.75,
            reference_context="Verified company revenue for 2026 is $10 Million."
        )

    def test_safe_stream_evaluation(self):
        def sample_stream():
            yield "Verified company "
            yield "revenue for 2026 "
            yield "is $10 Million."

        evaluations = list(self.evaluator.evaluate_stream(sample_stream()))

        self.assertEqual(len(evaluations), 3)
        self.assertTrue(all(e.status == StreamSafetyStatus.SAFE for e in evaluations))
        self.assertFalse(any(e.is_terminated for e in evaluations))

    def test_hallucination_early_termination(self):
        def hallucinating_stream():
            yield "Verified company revenue is "
            yield "[unverified_fact] $500 Billion."
            yield "This part should never be reached."

        evaluations = list(self.evaluator.evaluate_stream(hallucinating_stream()))

        # Stream should terminate on chunk 2
        self.assertEqual(len(evaluations), 2)
        last_chunk = evaluations[-1]
        self.assertEqual(last_chunk.status, StreamSafetyStatus.HALLUCINATION_DETECTED)
        self.assertTrue(last_chunk.is_terminated)
        self.assertIn("STREAM BLOCKED", last_chunk.text_chunk)


if __name__ == "__main__":
    unittest.main()