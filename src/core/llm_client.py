import os
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class StructuredLLMClient:
    """Pydantic 스키마 기반 구조화된 출력을 보장하는 LLM 클라이언트"""
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_structured(self, prompt: str, response_schema: Type[T]) -> T:
        """Pydantic 스키마 형태에 맞춘 응답 생성"""
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise JSON output generator."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_schema,
        )
        return completion.choices[0].message.parsed