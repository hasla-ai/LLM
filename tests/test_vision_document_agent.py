import pytest
from src.agent.vision_document_agent import (
    BoundingBox,
    DocumentImage,
    DocumentLayoutElement,
    DocumentVisualParser,
    ElementType,
    MultiModalVisionAgent,
)


def test_bounding_box_validation():
    box = BoundingBox(x_min=0.1, y_min=0.2, x_max=0.8, y_max=0.9)
    assert box.x_min == 0.1
    assert box.y_max == 0.9

    with pytest.raises(ValueError):
        BoundingBox(x_min=-0.1, y_min=0.0, x_max=1.0, y_max=1.0)


def test_document_visual_parser():
    parser = DocumentVisualParser()
    doc_image = DocumentImage(document_id="doc_101", width_px=1024, height_px=1280)
    parsed = parser.parse_page(doc_image)

    assert parsed.document_id == "doc_101"
    assert len(parsed.elements) == 3
    tables = parsed.get_elements_by_type(ElementType.TABLE)
    assert len(tables) == 1
    assert "GPU Cluster" in tables[0].raw_text


def test_vision_agent_visual_question_answering():
    agent = MultiModalVisionAgent()
    doc_image = DocumentImage(document_id="doc_102", width_px=800, height_px=1000)

    res = agent.answer_visual_question(doc_image, "What is the Total Due on the invoice?")
    assert "Total Due" in res["answer"] or "INVOICE" in res["answer"]
    assert len(res["grounded_elements"]) > 0


def test_vision_agent_structured_extraction():
    agent = MultiModalVisionAgent()
    doc_image = DocumentImage(document_id="doc_103", width_px=800, height_px=1000)

    res = agent.extract_structured_data(doc_image)
    assert res["document_id"] == "doc_103"
    assert len(res["headers"]) == 1
    assert len(res["tables"]) == 1
    assert res["element_count"] == 3