from typing import Any, Dict, Generator, List, Optional
from pydantic import BaseModel, Field


class AudioFrame(BaseModel):
    """Container for streaming audio chunks."""
    frame_id: int
    data: bytes
    sample_rate: int = 16000
    format: str = "pcm"
    is_final: bool = False


class AudioAgentResponse(BaseModel):
    """Response returned by the audio agent loop."""
    transcript: str
    response_text: str
    audio_frames: List[AudioFrame]
    interrupted: bool = False


class StreamingTTS:
    """Engine for converting text streams into chunked audio frames."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def synthesize_stream(self, text_tokens: List[str]) -> Generator[AudioFrame, None, None]:
        """Yields audio frames for each text chunk/token."""
        for idx, token in enumerate(text_tokens):
            dummy_pcm_payload = f"audio_bytes_{token}".encode("utf-8")
            is_last = idx == len(text_tokens) - 1
            yield AudioFrame(
                frame_id=idx + 1,
                data=dummy_pcm_payload,
                sample_rate=self.sample_rate,
                is_final=is_last,
            )


class RealTimeAudioAgent:
    """Agent that orchestrates real-time audio interaction and text response generation."""

    def __init__(self, tts_engine: Optional[StreamingTTS] = None, llm_client: Any = None):
        self.tts_engine = tts_engine or StreamingTTS()
        self.llm_client = llm_client
        self.is_speaking: bool = False

    def process_speech_input(self, audio_frames: List[AudioFrame]) -> str:
        """Simulates automatic speech recognition (ASR) on incoming audio frames."""
        combined_payload = b"".join([f.data for f in audio_frames])
        if not combined_payload:
            return ""
        return "Transcribed user query from audio stream."

    def run_turn(self, audio_input: List[AudioFrame]) -> AudioAgentResponse:
        """Executes a full voice turn: ASR -> Agent Processing -> Streaming TTS."""
        if not audio_input:
            raise ValueError("Input audio frame stream cannot be empty.")

        transcript = self.process_speech_input(audio_input)
        response_text = f"Agent response to: {transcript}"

        # Generate audio frames using StreamingTTS
        text_tokens = response_text.split()
        generated_frames = list(self.tts_engine.synthesize_stream(text_tokens))

        return AudioAgentResponse(
            transcript=transcript,
            response_text=response_text,
            audio_frames=generated_frames,
            interrupted=False,
        )

    def interrupt(self) -> None:
        """Triggers interruption state when user speaks mid-response."""
        self.is_speaking = False