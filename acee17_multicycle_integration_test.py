from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def cycle(
    cycle_id,
    timestamp_utc,
    before,
    after,
    decision,
    rollback_phase_completed,
    rollback_performed,
):
    return {
        "cycle_id": cycle_id,
        "timestamp_utc": timestamp_utc,
        "before_score": before,
        "after_score": after,
        "score_delta": after - before,
        "decision": decision,
        "rollback_status": (
            "performed" if rollback_performed else "not_performed"
        ),
        "rollback_phase_completed": rollback_phase_completed,
        "rollback_performed": rollback_performed,
        "validation_status": "passed",
        "causal_status": "resolved",
        "metrics": {
            "error_count": 0,
            "evolution_score": after,
            "governance_score": 0.90,
            "closure_pressure": 0.10,
            "stability_score": 0.94,
            "causal_impact": after - before,
        },
        "generation_id": f"generation-{cycle_id}",
        "lineage_id": "lineage-main",
    }


def main():
    records = [
        cycle("c1", "2026-07-14T09:00:00Z", 0.80, 0.84, "accept", True, False),
        cycle("c2", "2026-07-14T10:00:00Z", 0.84, 0.81, "rollback", True, True),
        cycle("c3", "2026-07-14T11:00:00Z", 0.81, 0.86, "accept", True, False),
    ]

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        result = ACEEDashboard(
            root=root,
            runtime_dir=root / "runtime",
        ).step(
            inputs={
                "records": records,
                "genealogy": {},
                "lineage": {},
                "archive": {},
            },
            persist=False,
        )

        assert result["cycle_count"] == 3
        charts = result["charts"]
        assert charts["rollback_count_over_time"][-1]["rollback_count"] == 1
        decisions = charts["accepted_vs_rejected_mutations"]
        assert decisions["accept"] == 2
        assert decisions["rollback"] == 1
        assert len(charts["cycle_score_over_time"]) == 3
        assert len(charts["closure_pressure_curve"]) == 3
        assert len(charts["stability_curve"]) == 3

    print("ACEE17_MULTICYCLE_INTEGRATION_OK")


if __name__ == "__main__":
    main()
