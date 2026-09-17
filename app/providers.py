from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

@dataclass
class ChatMessage:
    role: str
    content: str

class MockProvider:
    async def reply(self, messages: list[ChatMessage]) -> str:
        latest = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return ("[계획]\n요청을 분석하고 필요한 파일을 확인합니다.\n\n"
                "[변경]\n실제 모델을 연결하면 코드 변경안을 생성합니다.\n\n"
                "[검증]\n실행할 테스트와 확인 방법을 제시합니다.\n\n"
                f"받은 요청: {latest}")

class OllamaProvider:
    def __init__(self):
        self.base_url = os.getenv("AI_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv("AI_MODEL", "deepseek-coder")

    async def reply(self, messages: list[ChatMessage]) -> str:
        project_context = ""
        project_file = Path(__file__).parent.parent / "project.json"
        if project_file.exists():
            project_context = project_file.read_text(encoding="utf-8")
        system = ChatMessage(
            "system",
            "당신은 Forge AI 코딩 에이전트입니다. 프로젝트 맥락을 우선하고 작은 변경을 제안하세요. "
            "모든 답변을 [계획], [변경], [검증] 세 섹션으로 작성하세요. "
            "파일을 수정했다고 주장하지 말고, 먼저 diff와 테스트 명령을 제시하세요. "
            "코드는 언어를 표시한 fenced block으로 작성하세요.\n\n"
            "현재 프로젝트 컨텍스트:\n" + project_context,
        )
        payload = {
            "model": self.model,
            "messages": [system.__dict__] + [m.__dict__ for m in messages],
            "stream": False,
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError) as exc:
            raise RuntimeError(
                "Ollama에 연결할 수 없습니다. Ollama가 실행 중인지 확인하세요. "
                f"({exc})"
            ) from exc
        return result["message"]["content"]

def get_provider():
    if os.getenv("AI_PROVIDER", "mock").lower() == "ollama":
        return OllamaProvider()
    return MockProvider()
