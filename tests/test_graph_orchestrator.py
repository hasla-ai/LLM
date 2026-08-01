from src.agent.graph_orchestrator import AgentGraphState, MultiAgentGraphOrchestrator


def researcher_handler(state: AgentGraphState) -> AgentGraphState:
    state.research_notes = f"Key findings for task: {state.task}"
    return state


def writer_handler(state: AgentGraphState) -> AgentGraphState:
    if state.review_feedback:
        state.draft_content = f"Revised draft based on feedback: {state.review_feedback}"
    else:
        state.draft_content = f"Initial draft with notes: {state.research_notes}"
    return state


def reviewer_handler(state: AgentGraphState) -> AgentGraphState:
    # First pass requires revision, second pass approves
    if state.step_count < 4:
        state.is_approved = False
        state.review_feedback = "Needs more detail on architectural safety."
    else:
        state.is_approved = True
        state.review_feedback = "Looks great, approved!"
    return state


def review_condition(state: AgentGraphState) -> str:
    return "END" if state.is_approved else "writer"


def test_multi_agent_graph_cyclic_execution():
    orchestrator = MultiAgentGraphOrchestrator(max_steps=10)

    orchestrator.add_node("researcher", researcher_handler)
    orchestrator.add_node("writer", writer_handler)
    orchestrator.add_node("reviewer", reviewer_handler)

    orchestrator.add_edge("researcher", "writer")
    orchestrator.add_edge("writer", "reviewer")
    orchestrator.add_conditional_edge("reviewer", review_condition)

    initial_state = AgentGraphState(task="Write Mission 7 Spec")
    final_state = orchestrator.run(initial_state, start_node="researcher")

    assert final_state.is_approved is True
    assert final_state.research_notes is not None
    assert "Revised draft" in final_state.draft_content
    assert final_state.step_count > 3
    assert len(final_state.history) >= 4


def test_graph_max_steps_safety_termination():
    orchestrator = MultiAgentGraphOrchestrator(max_steps=3)

    # Endless loop setup
    orchestrator.add_node("node_a", lambda s: s)
    orchestrator.add_edge("node_a", "node_a")

    initial_state = AgentGraphState(task="Infinite Loop Test")
    final_state = orchestrator.run(initial_state, start_node="node_a")

    assert final_state.step_count == 3