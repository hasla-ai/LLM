from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    PROPONENT = "PROPONENT"
    OPPONENT = "OPPONENT"
    JUDGE = "JUDGE"


class DebateMessage(BaseModel):
    """Container for a single argument or rebuttal turn in a debate."""
    speaker_role: AgentRole
    speaker_name: str
    content: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class DebateRound(BaseModel):
    """Tracks all messages exchanged during a specific round."""
    round_number: int
    messages: List[DebateMessage]


class ConsensusResult(BaseModel):
    """Final decision output synthesized from multi-agent debate."""
    topic: str
    decision: str
    confidence_score: float
    total_rounds: int
    consensus_reached: bool
    round_history: List[DebateRound]


class MultiAgentDebateOrchestrator:
    """Orchestrates multi-turn debate rounds between specialized agents to reach consensus."""

    def __init__(self, max_rounds: int = 3, consensus_threshold: float = 0.8):
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold

    def _simulate_agent_turn(self, role: AgentRole, name: str, topic: str, round_num: int) -> DebateMessage:
        """Simulates agent argument generation per role."""
        if role == AgentRole.PROPONENT:
            content = f"Round {round_num}: Proponent argues in favor of '{topic}' based on performance and scalability gains."
            confidence = min(0.70 + (round_num * 0.08), 0.95)
        elif role == AgentRole.OPPONENT:
            content = f"Round {round_num}: Opponent highlights operational costs and implementation complexity for '{topic}'."
            confidence = min(0.65 + (round_num * 0.06), 0.90)
        else:
            content = f"Round {round_num}: Judge evaluates trade-offs between Proponent and Opponent."
            confidence = 0.85

        return DebateMessage(
            speaker_role=role,
            speaker_name=name,
            content=content,
            confidence=confidence,
        )

    def run_debate(self, topic: str) -> ConsensusResult:
        """Executes full debate loop until consensus threshold is met or max rounds reached."""
        if not topic.strip():
            raise ValueError("Debate topic cannot be empty.")

        round_history: List[DebateRound] = []
        consensus_reached = False
        final_confidence = 0.0

        for r_num in range(1, self.max_rounds + 1):
            prop_msg = self._simulate_agent_turn(AgentRole.PROPONENT, "Agent_Pro", topic, r_num)
            opp_msg = self._simulate_agent_turn(AgentRole.OPPONENT, "Agent_Con", topic, r_num)
            judge_msg = self._simulate_agent_turn(AgentRole.JUDGE, "Agent_Judge", topic, r_num)

            current_round = DebateRound(
                round_number=r_num,
                messages=[prop_msg, opp_msg, judge_msg],
            )
            round_history.append(current_round)

            # Average confidence score across participants in the current round
            avg_round_confidence = (prop_msg.confidence + opp_msg.confidence + judge_msg.confidence) / 3.0
            final_confidence = round(avg_round_confidence, 4)

            if final_confidence >= self.consensus_threshold:
                consensus_reached = True
                break

        decision = (
            f"Consensus Approved: Adopt solution for '{topic}' with mitigation plan for operational costs."
            if consensus_reached
            else f"Inconclusive Debate: Consensus threshold not reached for '{topic}' after {len(round_history)} rounds."
        )

        return ConsensusResult(
            topic=topic,
            decision=decision,
            confidence_score=final_confidence,
            total_rounds=len(round_history),
            consensus_reached=consensus_reached,
            round_history=round_history,
        )