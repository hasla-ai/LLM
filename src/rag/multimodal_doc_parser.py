import enum
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ElementType(str, enum.Enum):
    HEADER = "header"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    FIGURE = "figure"
    KEY_VALUE_GRID = "key_value_grid"


class BoundingBox(BaseModel):
    """Normalized spatial bounding box coordinates [xmin, ymin, xmax, ymax] (0.0 to 1.0)."""
    xmin: float = Field(ge=0.0, le=1.0)
    ymin: float = Field(ge=0.0, le=1.0)
    xmax: float = Field(ge=0.0, le=1.0)
    ymax: float = Field(ge=0.0, le=1.0)

    @property
    def area(self) -> float:
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)


class LayoutElement(BaseModel):
    """Represents a structural block extracted from a visual document page."""
    element_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    element_type: ElementType
    page_number: int
    text_content: str
    bbox: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0, default=0.95)
    metadata: Dict[str, str] = Field(default_factory=dict)


class ParsedDocumentAST(BaseModel):
    """Hierarchical Abstract Syntax Tree representation of a visual document."""
    doc_id: str
    num_pages: int
    elements: List[LayoutElement] = Field(default_factory=list)


class MultiModalDocParser:
    """
    Mission 30: Multi-Modal RAG Document Parsing & Layout Analysis Engine.
    Parses unstructured document images into structured AST nodes with spatial bounding boxes.
    """

    def parse_page_layout(
        self,
        doc_id: str,
        page_number: int,
        raw_elements_data: List[Dict]
    ) -> ParsedDocumentAST:
        """
        Parses raw layout elements into typed LayoutElement models and spatial bounding boxes.
        """
        elements = []
        for raw in raw_elements_data:
            bbox = BoundingBox(
                xmin=raw["bbox"][0],
                ymin=raw["bbox"][1],
                xmax=raw["bbox"][2],
                ymax=raw["bbox"][3]
            )
            element = LayoutElement(
                element_type=ElementType(raw["element_type"]),
                page_number=page_number,
                text_content=raw["text_content"],
                bbox=bbox,
                confidence=raw.get("confidence", 0.95),
                metadata=raw.get("metadata", {})
            )
            elements.append(element)

        return ParsedDocumentAST(
            doc_id=doc_id,
            num_pages=page_number,
            elements=elements
        )

    def extract_tables_and_figures(self, doc_ast: ParsedDocumentAST) -> List[LayoutElement]:
        """Filters AST for non-textual layout structures (Tables & Figures) requiring visual embeddings."""
        return [
            elem for elem in doc_ast.elements
            if elem.element_type in (ElementType.TABLE, ElementType.FIGURE)
        ]