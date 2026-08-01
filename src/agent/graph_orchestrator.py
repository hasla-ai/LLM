from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field


class AgentGraphState(BaseModel):
    """Shared state object passed across nodes in the agent graph."""
    task: str
    research_notes: Optional[str] = None
    draft_content: Optional[str] = None
    review_feedback: Optional[str] = None
    is_approved: bool = False
    step_count: int = 0
    history: List[str] = Field(default_factory=list)


class GraphNode:
    """Represents an agent node executing a distinct stage in the workflow."""
    def __init__(self, name: str, handler: Callable[[AgentGraphState], AgentGraphState]):
        self.name = name
        self.handler = handler

    def execute(self, state: AgentGraphState) -> AgentGraphState:
        state.step_count += 1
        state.history.append(f"Executed node: {self.name} (Step {state.step_count})")
        return self.handler(state)


class MultiAgentGraphOrchestrator:
    """Stateful workflow graph supporting cycles, conditional edges, and persistence."""
    def __init__(self, max_steps: int = 10):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Callable[[AgentGraphState], str]] = {}
        self.max_steps = max_steps

    def add_node(self, name: str, handler: Callable[[AgentGraphState], AgentGraphState]):
        self.nodes[name] = GraphNode(name, handler)

    def add_edge(self, from_node: str, to_node: str):
        self.edges[from_node] = to_node

    def add_conditional_edge(self, from_node: str, condition_func: Callable[[AgentGraphState], str]):
        self.conditional_edges[from_node] = condition_func

    def run(self, initial_state: AgentGraphState, start_node: str) -> AgentGraphState:
        """Executes the graph loop until END is reached or max_steps exceeded."""
        current_node_name = start_node
        state = initial_state

        while current_node_name != "END" and state.step_count < self.max_steps:
            if current_node_name not in self.nodes:
                raise ValueError(f"Node '{current_node_name}' not registered in graph.")

            node = self.nodes[current_node_name]
            state = node.execute(state)

            # Determine next node via conditional edge or standard edge
            if current_node_name in self.conditional_edges:
                current_node_name = self.conditional_edges[current_node_name](state)
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                break

        return state