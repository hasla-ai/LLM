from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ElementType(str, Enum):
    HEADER = "HEADER"
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    IMAGE = "IMAGE"
    KEY_VALUE_PAIR = "KEY_VALUE_PAIR"


class BoundingBox(BaseModel):
    """Normalized coordinates [0.0, 1.0] for region of interest on document page."""
    x_min: float = Field(ge=0.0, le=1.0)
    y_min: float = Field(ge=0.0, le=1.0)
    x_max: float = Field(ge=0.0, le=1.0)
    y_max: float = Field(ge=0.0, le=1.0)


class DocumentLayoutElement(BaseModel):
    """A detected spatial element within a document page."""
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    raw_text: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class DocumentImage(BaseModel):
    """Metadata and raw payload wrapper for multi-modal document image inputs."""
    document_id: str
    width_px: int
    height_px: int
    image_bytes: Optional[bytes] = None
    page_number: int = 1


class ParsedVisualDocument(BaseModel):
    """Parsed representation containing spatial elements and layout structure."""
    document_id: str
    page_number: int
    elements: List[DocumentLayoutElement] = Field(default_factory=list)

    def get_elements_by_type(self, element_type: ElementType) -> List[DocumentLayoutElement]:
        """Filter layout elements by specific type."""
        return [elem for elem in self.elements if elem.element_type == element_type]


class DocumentVisualParser:
    """Parses visual document structure and segments region of interest elements."""

    def parse_page(self, doc_image: DocumentImage, mock_elements: Optional[List[DocumentLayoutElement]] = None) -> ParsedVisualDocument:
        """Segments document layout into spatial components."""
        elements = mock_elements or [
            DocumentLayoutElement(
                element_id="hdr_1",
                element_type=ElementType.HEADER,
                bounding_box=BoundingBox(x_min=0.1, y_min=0.05, x_max=0.9, y_max=0.12),
                raw_text="INVOICE #INV-2026-0891",
                confidence=0.99,
            ),
            DocumentLayoutElement(
                element_id="kv_1",
                element_type=ElementType.KEY_VALUE_PAIR,
                bounding_box=BoundingBox(x_min=0.1, y_min=0.15, x_max=0.5, y_max=0.25),
                raw_text="Total Due: $4,250.00",
                confidence=0.96,
            ),
            DocumentLayoutElement(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                bounding_box=BoundingBox(x_min=0.1, y_min=0.3, x_max=0.9, y_max=0.7),
                raw_text="Item | Qty | Rate | Amount\nGPU Cluster | 2 | $2000 | $4000\nSupport | 1 | $250 | $250",
                confidence=0.95,
            ),
        ]

        return ParsedVisualDocument(
            document_id=doc_image.document_id,
            page_number=doc_image.page_number,
            elements=elements,
        )


class MultiModalVisionAgent:
    """Orchestrates multi-modal visual QA and grounded structured data extraction."""

    def __init__(self, parser: Optional[DocumentVisualParser] = None):
        self.parser = parser or DocumentVisualParser()

    def answer_visual_question(self, doc_image: DocumentImage, question: str) -> Dict[str, Any]:
        """Answers a question grounded in the document layout and text content."""
        parsed_doc = self.parser.parse_page(doc_image)
        question_lower = question.lower()

        matching_elements: List[DocumentLayoutElement] = []
        for elem in parsed_doc.elements:
            if any(term in elem.raw_text.lower() for term in question_lower.split()):
                matching_elements.append(elem)

        if not matching_elements:
            matching_elements = parsed_doc.elements

        evidence_text = "\n".join([f"[{e.element_type.value}] {e.raw_text}" for e in matching_elements])
        answer = f"Based on the visual document review: {matching_elements[0].raw_text}"

        return {
            "question": question,
            "answer": answer,
            "grounded_elements": [e.element_id for e in matching_elements],
            "evidence": evidence_text,
        }

    def extract_structured_data(self, doc_image: DocumentImage) -> Dict[str, Any]:
        """Extracts structured Key-Value and Table data from visual document layout."""
        parsed_doc = self.parser.parse_page(doc_image)

        headers = [e.raw_text for e in parsed_doc.get_elements_by_type(ElementType.HEADER)]
        key_values = [e.raw_text for e in parsed_doc.get_elements_by_type(ElementType.KEY_VALUE_PAIR)]
        tables = [e.raw_text for e in parsed_doc.get_elements_by_type(ElementType.TABLE)]

        return {
            "document_id": doc_image.document_id,
            "page_number": doc_image.page_number,
            "headers": headers,
            "key_value_pairs": key_values,
            "tables": tables,
            "element_count": len(parsed_doc.elements),
        }