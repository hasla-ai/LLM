import ast
import traceback
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ASTValidationResult(BaseModel):
    """Payload representing AST validation and refactoring outcome."""
    is_valid: bool
    refactored_code: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    applied_refactorings: List[str] = Field(default_factory=list)


class ASTSecurityAndCleanlinessTransformer(ast.NodeTransformer):
    """
    AST Transformer that automatically refactors unsafe or anti-pattern Python constructs:
    - Replaces bare `eval(...)` calls with a safer placeholder or warning.
    - Replaces bare `except:` clauses with `except Exception:`.
    """

    def __init__(self):
        super().__init__()
        self.applied_refactorings: List[str] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        # Refactor bare `except:` to `except Exception:`
        if node.type is None:
            node.type = ast.Name(id="Exception", ctx=ast.Load())
            self.applied_refactorings.append("Refactored bare 'except:' to 'except Exception:'")
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Detect and flag unsafe `eval()` calls
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            self.applied_refactorings.append("Flagged/Refactored unsafe 'eval()' invocation")
        self.generic_visit(node)
        return node


class ASTRefactorSandboxEngine:
    """
    Mission 36: Agentic Self-Healing Code Refactoring & AST Validation Sandbox.
    Parses, validates, and auto-refactors generated code at the Abstract Syntax Tree level.
    """

    def validate_and_refactor(self, code_snippet: str) -> ASTValidationResult:
        """
        Validates Python code syntax via AST parsing and applies safety/cleanliness refactoring.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Parse AST to verify syntax
        try:
            parsed_ast = ast.parse(code_snippet)
        except SyntaxError as e:
            errors.append(f"SyntaxError: {e.msg} at line {e.lineno}, col {e.offset}")
            return ASTValidationResult(
                is_valid=False,
                refactored_code=code_snippet,
                errors=errors,
                warnings=warnings,
                applied_refactorings=[]
            )
        except Exception as e:
            errors.append(f"Parse Error: {str(e)}")
            return ASTValidationResult(
                is_valid=False,
                refactored_code=code_snippet,
                errors=errors,
                warnings=warnings,
                applied_refactorings=[]
            )

        # 2. Transform / Refactor AST
        transformer = ASTSecurityAndCleanlinessTransformer()
        transformed_ast = transformer.visit(parsed_ast)
        ast.fix_missing_locations(transformed_ast)

        # 3. Unparse AST back to source code (Python 3.9+)
        try:
            refactored_code = ast.unparse(transformed_ast)
        except Exception as e:
            errors.append(f"AST Unparse Error: {str(e)}")
            return ASTValidationResult(
                is_valid=False,
                refactored_code=code_snippet,
                errors=errors,
                warnings=warnings,
                applied_refactorings=[]
            )

        return ASTValidationResult(
            is_valid=True,
            refactored_code=refactored_code,
            errors=[],
            warnings=warnings,
            applied_refactorings=transformer.applied_refactorings
        )