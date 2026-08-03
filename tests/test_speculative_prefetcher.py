import unittest
from src.core.speculative_prefetcher import SpeculativePromptPrefetcher


class TestSpeculativePromptPrefetcher(unittest.TestCase):
    def setUp(self):
        self.prefetcher = SpeculativePromptPrefetcher(confidence_threshold=0.60)

        # Register speculative rule: If prompt mentions 'billing', prefetch invoice context
        self.prefetcher.register_intent_prediction_rule(
            trigger_keyword="billing",
            predicted_topic="invoice_history",
            preloaded_context="Tenant Invoice #2026-08: $450.00 Paid on 2026-08-01.",
            confidence=0.85
        )

    def test_speculative_prefetch_trigger(self):
        prompt = "Where can I view my billing account details?"
        predictions = self.prefetcher.predict_and_prefetch(prompt)

        self.assertEqual(len(predictions), 1)
        self.assertEqual(predictions[0].topic_key, "invoice_history")
        self.assertTrue(predictions[0].is_cached)
        self.assertEqual(predictions[0].confidence_score, 0.85)

    def test_prewarmed_context_retrieval(self):
        prompt = "I have a billing question."
        self.prefetcher.predict_and_prefetch(prompt)

        cached_context = self.prefetcher.get_prewarmed_context("invoice_history")
        self.assertIsNotNone(cached_context)
        self.assertIn("Tenant Invoice #2026-08", cached_context)

    def test_no_trigger_on_unrelated_prompt(self):
        prompt = "How do I deploy a Docker container?"
        predictions = self.prefetcher.predict_and_prefetch(prompt)

        self.assertEqual(len(predictions), 0)
        self.assertIsNone(self.prefetcher.get_prewarmed_context("invoice_history"))


if __name__ == "__main__":
    unittest.main()