import pytest
from src.agent.debate_orchestrator import (
    AgentRole,
    ConsensusResult,
    MultiAgentDebateOrchestrator,
)


def test_debate_orchestrator_successful_consensus():
    orchestrator = MultiAgentDebateOrchestrator(max_rounds=3, consensus_threshold=0.75)
    result = orchestrator.run_debate(topic="Adopt Microservices Architecture")

    assert isinstance(result, ConsensusResult)
    assert result.consensus_reached is True
    assert result.total_rounds <= 3
    assert result.confidence_score >= 0.75
    assert "Consensus Approved" in result.decision


def test_debate_orchestrator_max_rounds_exceeded():
    # Unreachable threshold forces max rounds execution
    orchestrator = MultiAgentDebateOrchestrator(max_rounds=2, consensus_threshold=0.99)
    result = orchestrator.run_debate(topic="Migrate legacy monolithic database")

    assert result.consensus_reached is False
    assert result.total_rounds == 2
    assert "Inconclusive Debate" in result.decision


def test_debate_orchestrator_round_history_structure():
    orchestrator = MultiAgentDebateOrchestrator(max_rounds=1, consensus_threshold=0.50)
    result = orchestrator.run_debate(topic="Introduce GraphQL API Gateway")

    assert len(result.round_history) == 1
    messages = result.round_history[0].messages
    assert len(messages) == 3

    roles = [m.speaker_role for m in messages]
    assert AgentRole.PROPONENT in roles
    assert AgentRole.OPPONENT in roles
    assert AgentRole.JUDGE in roles


def test_debate_orchestrator_empty_topic_error():
    orchestrator = MultiAgentDebateOrchestrator()
    with pytest.raises(ValueError, match="Debate topic cannot be empty"):
        orchestrator.run_debate(topic="   ")