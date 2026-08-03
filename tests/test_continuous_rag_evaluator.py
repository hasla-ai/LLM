import unittest
from src.eval.continuous_rag_evaluator import ContinuousRAGEvaluatorEngine


class TestContinuousRAGEvaluatorEngine(unittest.TestCase):
    def setUp(self):
        self.evaluator = ContinuousRAGEvaluatorEngine(hallucination_threshold=0.50)

    def test_faithful_rag_triplet_evaluation(self):
        query = "What is the capital of France?"
        contexts = ["Paris is the capital and largest city of France."]
        answer = "Paris is the capital of France."

        metrics = self.evaluator.evaluate_rag_triplet(
            eval_id="e_101",
            query=query,
            retrieved_contexts=contexts,
            generated_answer=answer
        )

        self.assertGreaterEqual(metrics.faithfulness_score, 0.50)
        self.assertGreaterEqual(metrics.answer_relevance_score, 0.50)
        self.assertFalse(metrics.is_hallucination_suspected)

    def test_hallucination_detection_on_unsupported_claims(self):
        query = "What is the capital of France?"
        contexts = ["Paris is the capital and largest city of France."]
        # Completely ungrounded answer
        answer = "Berlin is located in Germany with a population of 3.6 million."

        metrics = self.evaluator.evaluate_rag_triplet(
            eval_id="e_102",
            query=query,
            retrieved_contexts=contexts,
            generated_answer=answer
        )

        self.assertLess(metrics.faithfulness_score, 0.50)
        self.assertTrue(metrics.is_hallucination_suspected)


if __name__ == "__main__":
    unittest.main()