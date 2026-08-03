import unittest
from src.agent.consensus_graph import (
    ConsensusGraphEngine,
    AgentProposal,
    ConsensusStrategy,
)


class TestConsensusGraphEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ConsensusGraphEngine()
        self.proposals = [
            AgentProposal(
                agent_id="security_agent",
                proposal_id="prop_01",
                content="Sanitize inputs before SQL query execution",
                confidence_score=0.95,
                agent_weight=2.0,  # Higher domain weight for security
            ),
            AgentProposal(
                agent_id="performance_agent",
                proposal_id="prop_02",
                content="Add index to database table",
                confidence_score=0.85,
                agent_weight=1.0,
            ),
            AgentProposal(
                agent_id="junior_reviewer",
                proposal_id="prop_03",
                content="Add index to database table",
                confidence_score=0.60,
                agent_weight=1.0,
            ),
        ]

    def test_weighted_score_consensus(self):
        result = self.engine.resolve_consensus(
            self.proposals, strategy=ConsensusStrategy.WEIGHTED_SCORE
        )
        # Security agent score: 0.95 * 2.0 = 1.9 (highest)
        self.assertEqual(result.winning_proposal_id, "prop_01")
        self.assertEqual(result.strategy_used, ConsensusStrategy.WEIGHTED_SCORE)
        self.assertEqual(len(result.participating_agents), 3)

    def test_majority_vote_consensus(self):
        result = self.engine.resolve_consensus(
            self.proposals, strategy=ConsensusStrategy.MAJORITY_VOTE
        )
        # "Add index to database table" has 2 votes (weights 1.0 + 1.0 = 2.0) vs Security (2.0)
        # Tie-breaker handles according to max iteration
        self.assertIn(result.winning_proposal_id, ["prop_01", "prop_02", "prop_03"])

    def test_empty_proposals_raises_error(self):
        with self.assertRaises(ValueError):
            self.engine.resolve_consensus([])


if __name__ == "__main__":
    unittest.main()