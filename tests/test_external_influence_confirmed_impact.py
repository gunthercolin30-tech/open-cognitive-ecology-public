from ontology.external_influence_traceability_engine import (
    ExternalInfluenceTraceabilityEngine,
)


def test_traceability_reports_confirmed_governed_adoptions(tmp_path):
    engine = ExternalInfluenceTraceabilityEngine(root=tmp_path)

    result = engine.step(
        inputs={
            "adoption_records": [
                {
                    "adoption_id": "ADOPT-1",
                    "timestamp_utc": "2026-06-16T09:00:00Z",
                    "provider": "OpenRouter",
                    "query_id": "OR-010",
                    "adoption_class": "code_candidate",
                    "adoption_status": "approved_for_governed_adoption",
                    "human_approval_status": "approved",
                    "linked_commit": "abc1234",
                    "confirmed_influence": True,
                },
                {
                    "adoption_id": "ADOPT-2",
                    "timestamp_utc": "2026-06-16T09:05:00Z",
                    "provider": "OpenRouter",
                    "query_id": "OR-011",
                    "adoption_class": "priority_candidate",
                    "adoption_status": "pending_human_review",
                    "human_approval_status": "pending",
                    "confirmed_influence": False,
                },
            ]
        },
        persist=False,
    )

    assert result["external_adoption_record_count"] == 2
    assert result["confirmed_external_influence_count"] == 1
    assert result["confirmed_code_influence_count"] == 1
    assert result["confirmed_priority_influence_count"] == 0
    assert result["linked_commit_influence_count"] == 1
    assert result["latest_confirmed_external_influences"][0]["adoption_id"] == "ADOPT-1"
    assert result["diagnostics"]["confirmed_adoption_audit_enabled"] is True
    assert result["diagnostics"]["direct_execution_authorized"] is False
