import json
import unittest
from src.core.synthetic_data_generator import SyntheticDataGeneratorEngine


class TestSyntheticDataGeneratorEngine(unittest.TestCase):
    def setUp(self):
        self.generator = SyntheticDataGeneratorEngine(quality_threshold=0.60)

    def test_synthetic_sample_generation_and_approval(self):
        sample = self.generator.generate_sample(
            sample_id="synth_001",
            instruction_seed="Explain how transformer attention works.",
            domain_context={"field": "AI Engineering"}
        )

        self.assertEqual(sample.sample_id, "synth_001")
        self.assertGreaterEqual(sample.quality_score, 0.60)
        self.assertTrue(sample.is_approved)

    def test_export_approved_samples_to_jsonl(self):
        sample1 = self.generator.generate_sample(
            sample_id="synth_001",
            instruction_seed="Explain transformer attention."
        )

        jsonl_output = self.generator.export_to_jsonl([sample1])
        lines = jsonl_output.strip().split("\n")

        self.assertEqual(len(lines), 1)
        parsed = json.loads(lines[0])
        self.assertEqual(parsed["sample_id"], "synth_001")


if __name__ == "__main__":
    unittest.main()