from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ReplicationStatisticsEngine:
    primitive = "replication_statistics_engine"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "independent_validation_observatory"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _safe_count_external_replications(self, records: list[dict[str, Any]]) -> int:
        explicit = 0
        for record in records:
            p = str(record.get("path", "")).lower()
            primitive = str(record.get("primitive", "")).lower()
            if "independent" in p and "replication" in p and record.get("success"):
                explicit += 1
            elif "external_replication" in primitive and record.get("success"):
                explicit += 1
        evidence_path = self.root / "external_validation" / "github_replication_feedback" / "latest_github_replication_feedback.json"
        data = self._read_json(evidence_path)
        if isinstance(data, dict):
            explicit = max(explicit, int(data.get("replication_feedback_count", 0) or 0))
        return explicit

    def step(self, validation_archive_state: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        archive = validation_archive_state or {}
        records = archive.get("records", [])
        if not isinstance(records, list):
            records = []
        records = [r for r in records if isinstance(r, dict)]
        record_count = int(archive.get("record_count", len(records)) or 0)
        successful_count = int(archive.get("successful_record_count", sum(1 for r in records if r.get("success"))) or 0)
        external_replication_count = self._safe_count_external_replications(records)
        success_ratio = successful_count / record_count if record_count else 0.0
        category_counts = archive.get("category_counts", {}) if isinstance(archive.get("category_counts", {}), dict) else {}
        diversity = min(1.0, len(category_counts) / 6.0)
        validation_growth_rate = min(1.0, record_count / 100.0)
        validation_stability_index = mean([success_ratio, diversity, 1.0 if record_count > 0 else 0.0])

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H18",
            "external_replication_count": external_replication_count,
            "validation_growth_rate": round(validation_growth_rate, 6),
            "validation_stability_index": round(validation_stability_index, 6),
            "record_count": record_count,
            "successful_record_count": successful_count,
            "success_ratio": round(success_ratio, 6),
            "category_diversity_index": round(diversity, 6),
            "statistics_ready": True,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
        }
        if persist:
            state_path = self.output_dir / "latest_replication_statistics_engine.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "replication_statistics_engine.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
