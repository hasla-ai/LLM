"""Read-only checks for the SCRUM-39 protection overlay.

This module does not modify the existing Forge H2 program. It verifies that
the protected invariants and cross-cutting calculation controls are present.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _check(results: list[dict[str, Any]], check_id: str, passed: bool, message: str) -> None:
    results.append({"check_id": check_id, "passed": passed, "message": message})


def audit() -> dict[str, Any]:
    policy = _load("security/protection-policy.json")
    workflow = _load("workflow/process-agent-map.json")
    access = _load("knowledge/access-policy.json")
    formula = _load("knowledge/formula-library.json")
    formula_h2 = _load("knowledge/formula-library-h2.json")
    kernel = _load("knowledge/calculation-kernel.json")
    calculator_source = (ROOT / "app/calc.py").read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []

    protected_assets = []
    for asset in policy["protected_assets"]:
        target = ROOT / asset["path"]
        exists = target.exists()
        protected_assets.append({"path": asset["path"], "exists": exists, "classification": asset["classification"]})
        _check(results, f"asset:{asset['path']}", exists, "protected asset exists" if exists else "protected asset missing")

    phase_gates = {phase.get("gate_id") for phase in workflow.get("phases", [])}
    _check(results, "gate_order_present", {f"G{i}" for i in range(8)}.issubset(phase_gates | {"G0"}), "G0-G7 remain represented in the process map")
    _check(results, "no_silent_progression", workflow.get("orchestration_rules", {}).get("no_silent_progression") is True, "silent progression remains disabled")
    _check(results, "offline_network_policy", access.get("offline_mode", {}).get("network_policy") == "deny_all_remote_fetch", "offline remote fetch remains denied")
    _check(results, "formula_dynamic_code", formula.get("execution_policy", {}).get("allow_dynamic_code") is False, "formula library disallows dynamic code")
    _check(results, "h2_formula_dynamic_code", formula_h2.get("execution_policy", {}).get("allow_dynamic_code") is False, "H2 formula library disallows dynamic code")
    _check(results, "h2_formula_cases", len(formula_h2.get("formulas", [])) == 18 and all(item.get("validation_cases") for item in formula_h2.get("formulas", [])), "H2 formula library has 18 formulas with validation cases")
    lhv_ref = formula_h2.get("reference_values", {}).get("H2_LHV_KWH_PER_KG", {})
    _check(results, "h2_reference_value_provenance", all(lhv_ref.get(field) for field in ("value", "unit", "source_knowledge_id", "evidence_id", "verification_status")), "H2 LHV reference value carries provenance")
    _check(results, "calculator_reference_values", "reference_value(" in calculator_source and "LHV_H2_KWH_KG" not in calculator_source, "calculator reads reference values instead of hard-coded LHV")
    _check(results, "kernel_protected_overlay", kernel.get("jira_epic") == "SCRUM-29" and kernel.get("protection_issue") == "SCRUM-39", "calculation kernel is linked to SCRUM-29 and protected by SCRUM-39")
    _check(results, "kernel_deterministic", kernel.get("execution_policy", {}).get("executor") == "deterministic", "calculation kernel is deterministic")
    _check(results, "kernel_human_review", kernel.get("change_policy", {}).get("human_review_required") is True, "kernel changes require human review")

    evidence_schema = _load("schemas/evidence.schema.json")
    gate_schema = _load("schemas/gate.schema.json")
    _check(results, "evidence_hash_schema", evidence_schema.get("properties", {}).get("content_hash", {}).get("pattern") == "^sha256:[0-9a-f]{64}$", "Evidence requires SHA-256 content hash")
    _check(results, "gate_evidence_schema", gate_schema.get("properties", {}).get("required_evidence_ids", {}).get("minItems") == 1, "Gate requires at least one Evidence ID")

    try:
        status = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=False)
        working_tree = [line for line in status.stdout.splitlines() if line.strip()]
    except OSError:
        working_tree = ["git status unavailable"]
    return {
        "policy_id": policy["policy_id"],
        "jira_issue": policy["jira_issue"],
        "protected_program": policy["protected_program"],
        "valid": all(item["passed"] for item in results),
        "checks": results,
        "protected_assets": protected_assets,
        "working_tree_changes_require_review": bool(working_tree),
        "working_tree_change_count": len(working_tree),
        "mode": "read_only_audit",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
