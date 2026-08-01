from unittest.mock import MagicMock
from src.core.llm_client import StructuredLLMClient
from pydantic import BaseModel, Field

class TechInfo(BaseModel):
    name: str
    score: int = Field(ge=1, le=5)

def test_simple_check():
    assert 1 + 1 == 2

def test_structured_llm_output_with_mock():
    """API 호출 없이 구조화 동작을 검증하는 Mock 테스트"""
    client = StructuredLLMClient(api_key="mock-key")
    
    # OpenAI 응답을 가짜(Mock) 객체로 대체
    mock_parsed_response = TechInfo(name="LLM Engineering", score=5)
    mock_completion = MagicMock()
    mock_completion.choices[0].message.parsed = mock_parsed_response
    
    client.client.beta.chat.completions.parse = MagicMock(return_value=mock_completion)

    result = client.generate_structured("LLM이란?", TechInfo)

    assert result.name == "LLM Engineering"
    assert result.score == 5