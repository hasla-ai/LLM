import pytest
from src.agent.audio_agent import (
    AudioFrame,
    RealTimeAudioAgent,
    StreamingTTS,
)


def test_streaming_tts_synthesis():
    tts = StreamingTTS(sample_rate=24000)
    tokens = ["Hello", "world", "this", "is", "a", "test."]
    frames = list(tts.synthesize_stream(tokens))

    assert len(frames) == len(tokens)
    assert frames[0].frame_id == 1
    assert frames[-1].is_final is True
    assert frames[0].sample_rate == 24000


def test_audio_agent_process_turn():
    agent = RealTimeAudioAgent()
    input_frames = [
        AudioFrame(frame_id=1, data=b"frame1_pcm"),
        AudioFrame(frame_id=2, data=b"frame2_pcm", is_final=True),
    ]

    response = agent.run_turn(input_frames)

    assert "Transcribed user query" in response.transcript
    assert len(response.audio_frames) > 0
    assert response.interrupted is False


def test_audio_agent_empty_input_error():
    agent = RealTimeAudioAgent()
    with pytest.raises(ValueError, match="Input audio frame stream cannot be empty"):
        agent.run_turn([])


def test_audio_agent_interruption():
    agent = RealTimeAudioAgent()
    agent.is_speaking = True
    agent.interrupt()
    assert agent.is_speaking is False