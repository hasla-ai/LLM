from unittest.mock import MagicMock
import pytest

from src.core.distillation_pipeline import (
    DatasetQualityFilter,
    DistillationDatasetGenerator,
    DistillationSample,
    DistillationTrainer,
    TrainingConfig,
)


@pytest.fixture
def mock_teacher_llm():
    return MagicMock()


def test_dataset_generator(mock_teacher_llm):
    generator = DistillationDatasetGenerator(teacher_llm=mock_teacher_llm)
    sample = generator.generate_sample("Enterprise vector databases enable fast retrieval.")

    assert isinstance(sample, DistillationSample)
    assert "Enterprise vector databases" in sample.instruction
    assert sample.quality_score >= 0.8


def test_quality_filter():
    filter_engine = DatasetQualityFilter(min_quality_score=0.8, min_response_length=15)

    good_sample = DistillationSample(
        instruction="What is RAG?",
        teacher_response="Retrieval-Augmented Generation bridges internal data.",
        quality_score=0.9,
    )
    bad_sample_score = DistillationSample(
        instruction="What is RAG?",
        teacher_response="Valid response body length.",
        quality_score=0.5,
    )
    bad_sample_len = DistillationSample(
        instruction="What is RAG?",
        teacher_response="Short",
        quality_score=0.95,
    )

    filtered = filter_engine.filter([good_sample, bad_sample_score, bad_sample_len])

    assert len(filtered) == 1
    assert filtered[0].instruction == "What is RAG?"


def test_distillation_trainer_success():
    config = TrainingConfig(student_model_name="tiny-student-1b", epochs=3)
    trainer = DistillationTrainer(config=config)

    dataset = [
        DistillationSample(
            instruction="Task 1",
            teacher_response="Detailed distillation answer 1",
            quality_score=0.85,
        )
    ]

    metrics = trainer.train(dataset)

    assert metrics.status == "SUCCESS"
    assert len(metrics.epoch_losses) == 3
    assert metrics.final_loss < metrics.epoch_losses[0]


def test_distillation_trainer_empty_dataset_error():
    config = TrainingConfig()
    trainer = DistillationTrainer(config=config)

    with pytest.raises(ValueError, match="Training dataset cannot be empty"):
        trainer.train([])