import unittest
from src.core.speculative_decoder import SpeculativeDecoderEngine, TokenDraft


class TestSpeculativeDecoderEngine(unittest.TestCase):
    def setUp(self):
        self.decoder = SpeculativeDecoderEngine(acceptance_threshold=0.70)

    def test_draft_generation(self):
        draft = self.decoder.generate_draft_tokens(prompt="Explain quantum computing", num_speculative_tokens=4)
        self.assertEqual(len(draft.tokens), 4)
        self.assertEqual(len(draft.confidence_scores), 4)

    def test_validation_acceptance_sequence(self):
        draft = TokenDraft(
            draft_id="d_test",
            tokens=["tok1", "tok2", "tok3"],
            confidence_scores=[0.90, 0.80, 0.50]  # tok3 falls below 0.70
        )

        result = self.decoder.validate_draft(draft)
        self.assertEqual(result.num_accepted, 2)
        self.assertEqual(result.accepted_tokens, ["tok1", "tok2"])
        self.assertEqual(result.num_rejected, 1)

    def test_full_acceptance_rate(self):
        draft = TokenDraft(
            draft_id="d_perfect",
            tokens=["a", "b", "c"],
            confidence_scores=[0.95, 0.88, 0.75]
        )

        result = self.decoder.validate_draft(draft)
        self.assertEqual(result.num_accepted, 3)
        self.assertEqual(result.acceptance_rate, 1.0)


if __name__ == "__main__":
    unittest.main()