from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.agent.tools import TOOL_REGISTRY

class AgentAction(BaseModel):
    """Schema for Agent's decision at each step."""
    thought: str = Field(description="Reasoning process for the current step")
    tool_name: Optional[str] = Field(None, description="Tool to call ('calculator') or None if finished")
    tool_input: Optional[str] = Field(None, description="Input string to pass to the tool")
    final_answer: Optional[str] = Field(None, description="Final answer to return if no tool needed")

class AgentEngine:
    """ReAct-style Agent Orchestrator with tool calling loop."""
    def __init__(self, llm_client: StructuredLLMClient, max_steps: int = 5):
        self.llm_client = llm_client
        self.max_steps = max_steps

    def run(self, user_prompt: str) -> str:
        """Executes the agent loop until a final answer is produced or max_steps reached."""
        conversation_history = f"User Request: {user_prompt}\nAvailable Tools: {list(TOOL_REGISTRY.keys())}\n"

        for step in range(self.max_steps):
            prompt = (
                f"{conversation_history}\n"
                "Decide the next step: either pick a tool to execute or provide the final_answer."
            )
            
            action: AgentAction = self.llm_client.generate_structured(prompt, AgentAction)

            # Case A: Agent decides it has the final answer
            if action.final_answer:
                return action.final_answer

            # Case B: Agent decides to invoke a tool
            if action.tool_name and action.tool_name in TOOL_REGISTRY:
                tool_fn = TOOL_REGISTRY[action.tool_name]
                observation = tool_fn(action.tool_input or "")
                conversation_history += (
                    f"\nStep {step+1}: Thought: {action.thought}\n"
                    f"Action: Used '{action.tool_name}' with input '{action.tool_input}'\n"
                    f"Observation: {observation}\n"
                )
            else:
                conversation_history += f"\nStep {step+1}: Invalid tool requested or no action taken."

        return "Agent reached maximum execution steps without producing a final answer."