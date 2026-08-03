import unittest
from src.agent.ast_refactor_sandbox import ASTRefactorSandboxEngine


class TestASTRefactorSandboxEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ASTRefactorSandboxEngine()

    def test_valid_code_parsing(self):
        code = "def add(a, b):\n    return a + b\n"
        result = self.engine.validate_and_refactor(code)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertIn("def add(a, b):", result.refactored_code)

    def test_syntax_error_detection(self):
        bad_code = "def broken_func(a, b\n    return a +"
        result = self.engine.validate_and_refactor(bad_code)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("SyntaxError" in err for err in result.errors))

    def test_bare_except_refactoring(self):
        code_with_bare_except = "try:\n    x = 1 / 0\nexcept:\n    pass\n"
        result = self.engine.validate_and_refactor(code_with_bare_except)

        self.assertTrue(result.is_valid)
        self.assertIn("except Exception:", result.refactored_code)
        self.assertIn("Refactored bare 'except:' to 'except Exception:'", result.applied_refactorings)


if __name__ == "__main__":
    unittest.main()