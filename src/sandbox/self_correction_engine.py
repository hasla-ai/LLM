import traceback
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Encapsulates the execution state from Sandbox #22."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None
    return_code: int = 0


class CorrectionIteration(BaseModel):
    """Tracks a single attempt in the self-correction feedback loop."""
    attempt: int
    code_snippet: str
    execution_result: ExecutionResult
    feedback_prompt: str


class SelfCorrectionEngine:
    """
    Mission 27: Self-Correction Sandbox & Code Feedback Loop.
    Orchestrates automatic code reflection and iterative repair upon runtime or AST failures.
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def generate_feedback_prompt(self, code: str, result: ExecutionResult) -> str:
        """Formulates diagnostic context for LLM re-generation."""
        return (
            f"The following Python code failed during execution:\n\n"
            f"```python\n{code}\n```\n\n"
            f"### Execution Error ({result.error_type or 'Runtime Error'}):\n"
            f"STDERR:\n{result.stderr}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"Please analyze the failure, fix the bugs, and return the revised, fully executable Python code."
        )

    def execute_with_correction_loop(
        self,
        initial_code: str,
        sandbox_runner_fn,  # Callable wrapping Sandbox #22 execution
    ) -> Tuple[bool, str, List[CorrectionIteration]]:
        """
        Runs code in Sandbox #22 and iteratively repairs it via LLM feedback loops if it fails.
        """
        current_code = initial_code
        history: List[CorrectionIteration] = []

        for attempt in range(1, self.max_attempts + 1):
            # Run code in sandbox
            result: ExecutionResult = sandbox_runner_fn(current_code)

            if result.success:
                return True, current_code, history

            # Generate error feedback diagnostic
            feedback = self.generate_feedback_prompt(current_code, result)
            history.append(
                CorrectionIteration(
                    attempt=attempt,
                    code_snippet=current_code,
                    execution_result=result,
                    feedback_prompt=feedback,
                )
            )

            # In production, send `feedback` to LLM client to update `current_code`
            # For iteration mock: simulate code repair attempt
            current_code = f"# Fixed in attempt {attempt + 1}\n" + current_code.replace("raise Exception", "# raise Exception")

        return False, current_code, history