import ast
import io
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class ViolationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityViolation(BaseModel):
    """Details of a security policy violation found during static code audit."""
    rule_id: str
    description: str
    severity: ViolationSeverity
    line_number: Optional[int] = None


class SecurityPolicy(BaseModel):
    """Configurable security boundaries for sandboxed python code execution."""
    banned_imports: Set[str] = Field(
        default_factory=lambda: {"os", "sys", "subprocess", "shutil", "builtins", "socket", "pathlib", "importlib"}
    )
    banned_functions: Set[str] = Field(
        default_factory=lambda: {"exec", "eval", "__import__", "open", "compile", "globals", "locals"}
    )
    max_execution_time_sec: float = 2.0
    max_output_length: int = 2000


class ExecutionResult(BaseModel):
    """Structured output returned after sandboxed code execution."""
    is_success: bool
    stdout: str
    stderr: str
    return_value: Optional[Any] = None
    violations: List[SecurityViolation] = Field(default_factory=list)


class CodeSecurityAuditor:
    """Inspects Python Abstract Syntax Trees (AST) for policy violations prior to execution."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()

    def audit(self, code: str) -> List[SecurityViolation]:
        """Parses Python code into an AST and inspects nodes against security policy."""
        violations: List[SecurityViolation] = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            violations.append(
                SecurityViolation(
                    rule_id="SYNTAX_ERROR",
                    description=f"Invalid python syntax: {str(e)}",
                    severity=ViolationSeverity.HIGH,
                    line_number=e.lineno,
                )
            )
            return violations

        for node in ast.walk(tree):
            # Check for banned imports (import os, import sys.path)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in self.policy.banned_imports:
                        violations.append(
                            SecurityViolation(
                                rule_id="BANNED_IMPORT",
                                description=f"Import of module '{module_name}' is forbidden.",
                                severity=ViolationSeverity.CRITICAL,
                                line_number=node.lineno,
                            )
                        )

            # Check for banned from-imports (from os import path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    if module_name in self.policy.banned_imports:
                        violations.append(
                            SecurityViolation(
                                rule_id="BANNED_IMPORT_FROM",
                                description=f"From-import from module '{module_name}' is forbidden.",
                                severity=ViolationSeverity.CRITICAL,
                                line_number=node.lineno,
                            )
                        )

            # Check for banned function calls (eval(), exec(), open())
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.policy.banned_functions:
                        violations.append(
                            SecurityViolation(
                                rule_id="BANNED_FUNCTION_CALL",
                                description=f"Call to prohibited function '{node.func.id}()' detected.",
                                severity=ViolationSeverity.HIGH,
                                line_number=node.lineno,
                            )
                        )

        return violations


class CodeExecutionSandbox:
    """Executes pre-audited Python code in a restricted local scope with output capturing."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.auditor = CodeSecurityAuditor(self.policy)

    def execute(self, code: str) -> ExecutionResult:
        """Audits and safely executes valid code, returning stdout and return values."""
        violations = self.auditor.audit(code)
        if violations:
            return ExecutionResult(
                is_success=False,
                stdout="",
                stderr="Execution blocked due to security policy violations.",
                return_value=None,
                violations=violations,
            )

        # Redirect stdout and stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr
        stdout_buffer, stderr_buffer = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = stdout_buffer, stderr_buffer

        # Safe extraction of builtins dict regardless of Pytest environment wrapper
        builtins_dict = (
            __builtins__ if isinstance(__builtins__, dict) else getattr(__builtins__, "__dict__", {})
        )

        global_scope: Dict[str, Any] = {
            "__builtins__": {
                k: v for k, v in builtins_dict.items() if k not in self.policy.banned_functions
            }
        }
        local_scope: Dict[str, Any] = {}

        try:
            exec(code, global_scope, local_scope)
            ret_val = local_scope.get("result", None)

            raw_stdout = stdout_buffer.getvalue()
            if len(raw_stdout) > self.policy.max_output_length:
                raw_stdout = raw_stdout[: self.policy.max_output_length] + "\n...[Output Truncated]"

            return ExecutionResult(
                is_success=True,
                stdout=raw_stdout,
                stderr=stderr_buffer.getvalue(),
                return_value=ret_val,
                violations=[],
            )
        except Exception as e:
            return ExecutionResult(
                is_success=False,
                stdout=stdout_buffer.getvalue(),
                stderr=f"Runtime Error: {type(e).__name__}: {str(e)}",
                return_value=None,
                violations=[],
            )
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr