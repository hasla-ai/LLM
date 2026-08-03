import pytest
from src.sandbox.code_sandbox import (
    CodeExecutionSandbox,
    CodeSecurityAuditor,
    SecurityPolicy,
    ViolationSeverity,
)


def test_auditor_detects_banned_imports():
    auditor = CodeSecurityAuditor()
    code = "import os\nprint(os.getcwd())"
    violations = auditor.audit(code)

    assert len(violations) > 0
    assert violations[0].rule_id == "BANNED_IMPORT"
    assert violations[0].severity == ViolationSeverity.CRITICAL


def test_auditor_detects_banned_functions():
    auditor = CodeSecurityAuditor()
    code = "data = open('secret.txt', 'r').read()"
    violations = auditor.audit(code)

    assert len(violations) > 0
    assert violations[0].rule_id == "BANNED_FUNCTION_CALL"


def test_sandbox_executes_safe_code():
    sandbox = CodeExecutionSandbox()
    code = "x = 10\ny = 20\nresult = x + y\nprint(f'Total: {result}')"
    res = sandbox.execute(code)

    assert res.is_success is True
    assert "Total: 30" in res.stdout
    assert res.return_value == 30
    assert len(res.violations) == 0


def test_sandbox_blocks_malicious_code():
    sandbox = CodeExecutionSandbox()
    code = "import subprocess\nsubprocess.run(['ls', '-la'])"
    res = sandbox.execute(code)

    assert res.is_success is False
    assert "Execution blocked" in res.stderr
    assert len(res.violations) == 1
    assert res.violations[0].rule_id == "BANNED_IMPORT"


def test_sandbox_captures_runtime_error():
    sandbox = CodeExecutionSandbox()
    code = "a = 10 / 0"
    res = sandbox.execute(code)

    assert res.is_success is False
    assert "ZeroDivisionError" in res.stderr