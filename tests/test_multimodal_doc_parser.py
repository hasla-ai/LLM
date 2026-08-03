import unittest
from src.rag.multimodal_doc_parser import (
    MultiModalDocParser,
    ElementType,
    BoundingBox,
)


class TestMultiModalDocParser(unittest.TestCase):
    def setUp(self):
        self.parser = MultiModalDocParser()
        self.sample_page_data = [
            {
                "element_type": "header",
                "text_content": "Quarterly Financial Report Q3",
                "bbox": [0.1, 0.05, 0.9, 0.15],
                "confidence": 0.99
            },
            {
                "element_type": "table",
                "text_content": "| Quarter | Revenue | Operating Expenses |\n| Q3 | $4.2M | $1.1M |",
                "bbox": [0.1, 0.2, 0.9, 0.5],
                "confidence": 0.94
            },
            {
                "element_type": "figure",
                "text_content": "[Chart: Monthly Revenue Trajectory]",
                "bbox": [0.1, 0.55, 0.9, 0.85],
                "confidence": 0.91
            }
        ]

    def test_parse_page_layout_ast_generation(self):
        ast = self.parser.parse_page_layout(
            doc_id="doc_report_2026",
            page_number=1,
            raw_elements_data=self.sample_page_data
        )

        self.assertEqual(ast.doc_id, "doc_report_2026")
        self.assertEqual(len(ast.elements), 3)
        self.assertEqual(ast.elements[0].element_type, ElementType.HEADER)
        self.assertAlmostEqual(ast.elements[1].bbox.area, 0.24)  # (0.9-0.1) * (0.5-0.2) = 0.24

    def test_extract_tables_and_figures(self):
        ast = self.parser.parse_page_layout(
            doc_id="doc_report_2026",
            page_number=1,
            raw_elements_data=self.sample_page_data
        )
        visual_elements = self.parser.extract_tables_and_figures(ast)

        self.assertEqual(len(visual_elements), 2)
        types = {e.element_type for e in visual_elements}
        self.assertEqual(types, {ElementType.TABLE, ElementType.FIGURE})


if __name__ == "__main__":
    unittest.main()