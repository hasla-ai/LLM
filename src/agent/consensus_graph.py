import enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ConsensusStrategy(str, enum.Enum):
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_SCORE = "weighted_score"
    HIGHEST_CONFIDENCE = "highest_confidence"


class AgentProposal(BaseModel):
    """Proposal payload submitted by an individual agent node."""
    agent_id: str
    proposal_id: str
    content: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    agent_weight: float = Field(gt=0.0, default=1.0)


class ConsensusResult(BaseModel):
    """Final output generated after resolving consensus across agent proposals."""
    winning_proposal_id: str
    winning_content: str
    consensus_score: float
    strategy_used: ConsensusStrategy
    participating_agents: List[str]


class ConsensusGraphEngine:
    """
    Mission 33: Multi-Agent Consensus Graph & Conflict Resolution Engine.
    Aggregates multi-agent proposals and resolves conflicts using graph consensus algorithms.
    """

    def resolve_consensus(
        self,
        proposals: List[AgentProposal],
        strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_SCORE
    ) -> ConsensusResult:
        """
        Resolves conflicts among agent proposals based on the selected consensus strategy.
        """
        if not proposals:
            raise ValueError("Cannot resolve consensus with an empty list of proposals.")

        participating_agents = [p.agent_id for p in proposals]

        if strategy == ConsensusStrategy.HIGHEST_CONFIDENCE:
            winning = max(proposals, key=lambda p: p.confidence_score)
            return ConsensusResult(
                winning_proposal_id=winning.proposal_id,
                winning_content=winning.content,
                consensus_score=winning.confidence_score,
                strategy_used=strategy,
                participating_agents=participating_agents
            )

        elif strategy == ConsensusStrategy.WEIGHTED_SCORE:
            # Score = confidence_score * agent_weight
            winning = max(proposals, key=lambda p: p.confidence_score * p.agent_weight)
            total_weight = sum(p.agent_weight for p in proposals)
            winning_score = (winning.confidence_score * winning.agent_weight) / (total_weight if total_weight > 0 else 1.0)

            return ConsensusResult(
                winning_proposal_id=winning.proposal_id,
                winning_content=winning.content,
                consensus_score=round(winning_score, 4),
                strategy_used=strategy,
                participating_agents=participating_agents
            )

        else: # MAJORITY_VOTE
            # Group identical/similar content votes
            vote_counts: Dict[str, float] = {}
            proposal_map: Dict[str, AgentProposal] = {}

            for p in proposals:
                vote_counts[p.content] = vote_counts.get(p.content, 0) + p.agent_weight
                proposal_map[p.content] = p

            winning_content = max(vote_counts.keys(), key=lambda c: vote_counts[c])
            winning = proposal_map[winning_content]

            return ConsensusResult(
                winning_proposal_id=winning.proposal_id,
                winning_content=winning_content,
                consensus_score=vote_counts[winning_content] / sum(vote_counts.values()),
                strategy_used=strategy,
                participating_agents=participating_agents
            )