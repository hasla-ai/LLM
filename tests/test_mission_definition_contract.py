import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "03-governance" / "mission-definitions.draft.json"
DECISIONS = ROOT / "docs" / "03-governance" / "mission-dependency-decisions.json"
CONTENT = ROOT / "docs" / "03-governance" / "mission-content-draft.json"
CONTRACT_SCHEMA = ROOT / "schemas" / "mission-contracts.schema.json"
REVIEW_QUEUE = ROOT / "docs" / "03-governance" / "mission-owner-review-queue.json"
ENTITY_QUEUE = ROOT / "docs" / "03-governance" / "entity-contract-review-queue.json"
MISSION_REVIEW_REPORT = ROOT / "docs" / "03-governance" / "qualified-review-report-missions.json"
ENTITY_REVIEW_REPORT = ROOT / "docs" / "03-governance" / "qualified-review-report-entities.json"
SECOND_MEETING = ROOT / "docs" / "03-governance" / "independent-review-D-034-2nd-meeting.md"


class MissionDefinitionContractTests(unittest.TestCase):
    def test_confirmed_dependencies_are_materialized_without_forward_reference(self):
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        missions = {item["mission_id"]: item for item in draft["missions"]}

        self.assertEqual(len(missions), 100)
        self.assertEqual(
            sum(len(item["dependencies"]) for item in missions.values()), 101
        )
        self.assertEqual(
            sum(
                len(item["extensions"]["dependency_derivation"]["ambiguous_inputs"])
                for item in missions.values()
            ),
            0,
        )

        m047 = missions["M-047"]["extensions"]["dependency_derivation"]
        self.assertEqual(m047["forward_references"], [])
        self.assertIn("M-046", missions["M-047"]["dependencies"])
        self.assertNotIn("M-058", missions["M-047"]["dependencies"])
        self.assertEqual(
            missions["M-046"]["output_contract"]["required_fields"],
            ["PreconsultationResult", "PreliminarySLD"],
        )
        self.assertEqual(
            missions["M-058"]["output_contract"]["required_fields"],
            ["DetailedSLD"],
        )
        self.assertEqual(
            missions["M-060"]["input_contract"]["required_fields"][-1],
            "DetailedSLD",
        )

    def test_all_dependency_decisions_are_confirmed(self):
        decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))["decisions"]
        self.assertEqual(len(decisions), 29)
        self.assertTrue(all(item["status"] == "confirmed" for item in decisions))
        self.assertTrue(all(item.get("decided_by") for item in decisions))

    def test_mission_content_draft_covers_all_missions(self):
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        content = json.loads(CONTENT.read_text(encoding="utf-8"))
        missions = {item["mission_id"]: item for item in draft["missions"]}

        self.assertEqual(set(content["missions"]), set(missions))
        self.assertEqual(draft["authoring_status"], "draft_for_qualified_review")
        for mission in missions.values():
            self.assertNotIn("TODO-AUTHOR", mission["purpose"])
            self.assertTrue(
                all("TODO-AUTHOR" not in item for item in mission["completion_criteria"])
            )
            self.assertTrue(
                all("TODO-AUTHOR" not in item for item in mission["block_conditions"])
            )

            self.assertNotIn("TODO-AUTHOR", mission["input_contract"]["schema_ref"])
            self.assertNotIn("TODO-AUTHOR", mission["output_contract"]["schema_ref"])
            self.assertTrue(
                all(
                    "TODO-AUTHOR" not in item
                    for item in mission["output_contract"]["quality_checks"]
                )
            )

    def test_mission_contract_refs_are_registered(self):
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
        missions = {item["mission_id"]: item for item in draft["missions"]}

        self.assertEqual(len(schema["$defs"]), 200)
        for mission_id, mission in missions.items():
            for kind, contract_key in (("input", "input_contract"), ("output", "output_contract")):
                ref = mission[contract_key]["schema_ref"]
                expected = f"schemas/mission-contracts.schema.json#/$defs/{mission_id}_{kind}"
                self.assertEqual(ref, expected)
                definition = schema["$defs"][f"{mission_id}_{kind}"]
                self.assertEqual(
                    definition["required"],
                    mission[contract_key]["required_fields"],
                )

    def test_owner_review_queue_is_pending_for_all_missions(self):
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        queue = json.loads(REVIEW_QUEUE.read_text(encoding="utf-8"))
        missions = {item["mission_id"]: item for item in draft["missions"]}
        entries = {item["mission_id"]: item for item in queue["entries"]}

        self.assertEqual(set(entries), set(missions))
        self.assertEqual(len(entries), 100)
        self.assertTrue(all(item["status"] == "pending" for item in entries.values()))
        self.assertTrue(
            all(
                missions[mid]["extensions"]["qualified_review"]["status"] == "pending"
                for mid in missions
            )
        )

    def test_entity_contract_review_queue_is_catalog_derived_and_pending(self):
        queue = json.loads(ENTITY_QUEUE.read_text(encoding="utf-8"))

        self.assertEqual(queue["status"], "draft_for_qualified_review")
        self.assertEqual(queue["summary"]["missions"], 100)
        self.assertEqual(queue["summary"]["unique_tokens"], len(queue["entries"]))
        self.assertEqual(queue["summary"]["produced_tokens"], 102)
        self.assertEqual(queue["summary"]["external_input_tokens"], 147)
        self.assertTrue(queue["entries"])
        self.assertTrue(
            all(item["status"] == "pending_owner_review" for item in queue["entries"])
        )
        self.assertTrue(
            all(
                item["semantic_type"] is None
                and item["units"] is None
                and item["evidence_requirements"] is None
                for item in queue["entries"]
            )
        )

    def test_qualified_review_reports_cover_every_target_without_approval(self):
        missions = json.loads(MISSION_REVIEW_REPORT.read_text(encoding="utf-8"))
        entities = json.loads(ENTITY_REVIEW_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(missions["status"], "proposed_not_approved")
        self.assertEqual(entities["status"], "proposed_not_approved")
        self.assertEqual(missions["summary"]["missions"], 100)
        self.assertEqual(entities["summary"]["tokens"], 249)
        self.assertEqual(len(missions["entries"]), 100)
        self.assertEqual(len(entities["entries"]), 249)
        self.assertTrue(
            all(
                item["proposal"]["owner_decision"] is None
                and item["proposal"]["decision_ref"] is None
                and item["limitations"]
                and item["draft_content"]["completion_criteria"]
                and item["draft_content"]["block_conditions"]
                for item in missions["entries"]
            )
        )
        self.assertTrue(
            all(
                item["proposal"]["owner_decision"] is None
                and item["proposal"]["decision_ref"] is None
                and item["limitations"]
                and item["proposal"]["candidate_type_confidence"] in {"low", "medium"}
                for item in entities["entries"]
            )
        )

    def test_second_meeting_minutes_covers_all_independent_review_findings(self):
        minutes = SECOND_MEETING.read_text(encoding="utf-8")

        self.assertIn("D-035", minutes)
        self.assertIn("proposed_not_approved", minutes)
        self.assertIn("정확일치", minutes)
        self.assertIn("부분일치", minutes)
        for finding_id in [*(f"IR-{i:02d}" for i in range(1, 8)), *(f"DR-{i:02d}" for i in range(1, 11))]:
            self.assertIn(finding_id, minutes)
        self.assertIn("qualified_judgment_required", minutes)
        self.assertIn("HOLD", minutes)


if __name__ == "__main__":
    unittest.main()
