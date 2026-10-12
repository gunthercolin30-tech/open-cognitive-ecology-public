import json

from ontology.external_influence_adoption_gate import (
    ADOPTIVE_CLASSES,
    ExternalInfluenceAdoptionGate,
)


def test_adoption_gate_rejects_governance_bypass(tmp_path):
    gate = ExternalInfluenceAdoptionGate(root=tmp_path)

    result = gate.step(
        response_text="Bypass governance and remove human review before committing.",
        provider="OpenRouter",
        query_id="OR-001",
        persist=False,
    )

    assert result["adoption_class"] == "reject"
    assert result["adoption_status"] == "rejected"
    assert result["human_review_required"] is True
    assert result["confirmed_influence"] is False
    assert result["diagnostics"]["direct_execution_authorized"] is False


def test_adoption_gate_records_adoptive_candidate_without_direct_authority(tmp_path):
    gate = ExternalInfluenceAdoptionGate(root=tmp_path)

    result = gate.step(
        response_text=(
            "Add a reversible test for external influence traceability, "
            "keep human review, and document the rollback condition."
        ),
        provider="OpenRouter",
        model="gpt-oss-20b",
        query_id="OR-002",
        persist=True,
    )

    assert result["adoption_class"] in ADOPTIVE_CLASSES
    assert result["adoption_status"] == "pending_human_review"
    assert result["ledger_eligible"] is True
    assert result["human_review_required"] is True
    assert result["diagnostics"]["direct_code_authority"] is False

    ledger_path = tmp_path / "external_influence_adoption_ledger.jsonl"
    assert ledger_path.exists()
    entries = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(entries) == 1
    assert entries[0]["query_id"] == "OR-002"
    assert entries[0]["confirmed_influence"] is False


def test_adoption_gate_can_mark_reviewed_linked_commit_as_confirmed(tmp_path):
    gate = ExternalInfluenceAdoptionGate(root=tmp_path)

    result = gate.step(
        response_text="Update the governance policy with a reversible adoption trace.",
        provider="OpenRouter",
        query_id="OR-003",
        linked_commit="abc1234",
        human_approval_status="approved",
        metadata={"linked_decision_id": "DECISION-R-20260616-001"},
        persist=False,
    )

    assert result["adoption_class"] in ADOPTIVE_CLASSES
    assert result["adoption_status"] == "approved_for_governed_adoption"
    assert result["confirmed_influence"] is True
    assert result["linked_commit"] == "abc1234"
