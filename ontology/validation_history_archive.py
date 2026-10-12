from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ValidationHistoryArchive:
    primitive = "validation_history_archive"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "independent_validation_observatory"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _normalise_record(self, path: Path, data: Any) -> dict[str, Any] | None:
        if isinstance(data, dict):
            success = bool(data.get("success", data.get("overall_success", False)))
            timestamp = str(data.get("timestamp_utc", data.get("timestamp", "")))
            primitive = str(data.get("primitive", data.get("stage", path.stem)))
            category = "generic"
            p = str(path)
            if "github" in p:
                category = "github"
            elif "zenodo" in p:
                category = "zenodo"
            elif "replication" in p:
                category = "replication"
            elif "consensus" in p:
                category = "consensus"
            elif "validation" in p:
                category = "validation"
            return {
                "path": str(path.relative_to(self.root)) if path.is_relative_to(self.root) else str(path),
                "category": category,
                "primitive": primitive,
                "success": success,
                "timestamp_utc": timestamp,
                "schema": "dict",
            }
        if isinstance(data, list):
            success_items = [x for x in data if isinstance(x, dict) and bool(x.get("success", x.get("overall_success", False)))]
            return {
                "path": str(path.relative_to(self.root)) if path.is_relative_to(self.root) else str(path),
                "category": "list_record",
                "primitive": path.stem,
                "success": len(success_items) > 0 or len(data) > 0,
                "timestamp_utc": "",
                "schema": "list",
                "item_count": len(data),
                "successful_item_count": len(success_items),
            }
        return None

    def _collect_json_records(self) -> list[dict[str, Any]]:
        roots = [
            self.root / "external_validation",
            self.root / "replication_packages",
            self.root / "runtime_experiments",
        ]
        records: list[dict[str, Any]] = []
        for base in roots:
            if not base.exists():
                continue
            for path in base.rglob("*.json"):
                data = self._read_json(path)
                record = self._normalise_record(path, data)
                if record is not None:
                    records.append(record)
        records.sort(key=lambda r: r.get("path", ""))
        return records

    def step(self, persist: bool = True) -> dict[str, Any]:
        records = self._collect_json_records()
        successful = [r for r in records if r.get("success")]
        category_counts: dict[str, int] = {}
        for record in records:
            category = str(record.get("category", "generic"))
            category_counts[category] = category_counts.get(category, 0) + 1

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H18",
            "record_count": len(records),
            "successful_record_count": len(successful),
            "category_counts": category_counts,
            "validation_history_active": True,
            "traceability_ready": len(records) > 0,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "records": records[-250:],
        }

        if persist:
            state_path = self.output_dir / "latest_validation_history_archive.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "validation_history_archive.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
