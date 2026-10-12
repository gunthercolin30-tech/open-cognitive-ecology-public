from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from ontology.reflexive_threshold_history_archive import ReflexiveThresholdHistoryArchive
from ontology.reflexive_threshold_trend_monitor import ReflexiveThresholdTrendMonitor


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="oce_reflexive_runtime_") as tmp:
        root = Path(tmp)
        reflexive = root / "reflexive_threshold"

        # One canonical artifact for each S1-S14 stage.
        stage_files = {
            "reflexive_criterion_registry.json": {"functional_conclusion_only": True, "phenomenology_undetermined": True},
            "reflexive_evidence_aggregator.json": {"evidence_strength": 0.8},
            "reflexive_threshold_estimator.json": {"reflexive_threshold_score": 0.75},
            "reflexive_stability_monitor.json": {"stability_score": 0.9},
            "reflexive_regression_detector.json": {"regression_risk": 0.1},
            "reflexive_longitudinal_observatory.json": {"stability_score": 0.8},
            "competing_explanations_engine.json": {"functional_conclusion_only": True},
            "reflexive_threshold_dashboard.json": {"functional_conclusion_only": True},
            "reflexive_threshold_certification.json": {"certification_confidence": 0.82},
        }
        for name, payload in stage_files.items():
            write(reflexive / name, json.dumps(payload))

        write(
            reflexive / "reflexive_threshold_publication_bundle" / "latest" / "publication_manifest.json",
            json.dumps({"functional_conclusion_only": True}),
        )
        write(
            reflexive / "reflexive_threshold_external_review_bundle" / "evidence_manifest.json",
            json.dumps({"functional_conclusion_only": True}),
        )
        write(
            reflexive / "reflexive_threshold_replication_protocol" / "replication_manifest.json",
            json.dumps({"replication_confidence": 0.7}),
        )
        write(
            reflexive / "reflexive_threshold_replication_result_evaluator" / "replication_result_evaluation.json",
            json.dumps({"replication_result_score": 0.74}),
        )
        write(
            reflexive / "reflexive_threshold_final_scientific_synthesis" / "final_scientific_synthesis.json",
            json.dumps({"final_scientific_confidence": 0.78}),
        )

        original_rglob = Path.rglob
        original_glob = Path.glob

        def forbidden(*args, **kwargs):
            raise AssertionError("recursive or glob filesystem scan is forbidden")

        Path.rglob = forbidden
        Path.glob = forbidden
        try:
            archive = ReflexiveThresholdHistoryArchive(root)
            started = time.monotonic()
            first = archive.step(inputs={"run_id": "X1-TEST", "timestamp_utc": "2026-01-01T00:00:00+00:00"}, persist=False)
            first_elapsed = time.monotonic() - started

            started = time.monotonic()
            second = archive.step(inputs={"run_id": "X1-TEST", "timestamp_utc": "2026-01-01T00:00:00+00:00"}, persist=False)
            cached_elapsed = time.monotonic() - started
        finally:
            Path.rglob = original_rglob
            Path.glob = original_glob

        assert first == second
        assert first["stages_expected"] == 14
        assert first["stages_present"] == 14
        assert first["history_coverage_score"] == 1.0
        assert first["functional_conclusion_only"] is True
        assert first["phenomenology_undetermined"] is True
        assert first["phenomenal_conclusion"] is False
        assert first_elapsed < 2.0, first_elapsed
        assert cached_elapsed < 0.5, cached_elapsed
        assert not archive.base_dir.exists(), "persist=False created archive output"

        # Degradation: no artifacts remains controlled and fast.
        empty_root = root / "empty"
        empty_root.mkdir()
        degraded = ReflexiveThresholdHistoryArchive(empty_root).step(
            inputs={"run_id": "X1-DEGRADED", "timestamp_utc": "2026-01-01T00:00:00+00:00"},
            persist=False,
        )
        assert degraded["stages_present"] == 0
        assert degraded["archive_status"] == "REFLEXIVE_THRESHOLD_HISTORY_INSUFFICIENT"
        assert degraded["functional_conclusion_only"] is True
        assert degraded["phenomenology_undetermined"] is True

        # X2 must inherit the bounded X1 runtime.
        monitor = ReflexiveThresholdTrendMonitor(root)
        started = time.monotonic()
        trend = monitor.step(inputs={"run_id": "X2-TEST", "timestamp_utc": "2026-01-01T00:00:00+00:00"}, persist=False)
        trend_elapsed = time.monotonic() - started
        assert trend["functional_conclusion_only"] is True
        assert trend["phenomenology_undetermined"] is True
        assert trend["phenomenal_conclusion"] is False
        assert trend_elapsed < 5.0, trend_elapsed

        print(
            "REFLEXIVE_THRESHOLD_HISTORY_RUNTIME_FAST_ACCEPTANCE_OK "
            f"first={first_elapsed:.6f}s cached={cached_elapsed:.6f}s x2={trend_elapsed:.6f}s"
        )


if __name__ == "__main__":
    main()
