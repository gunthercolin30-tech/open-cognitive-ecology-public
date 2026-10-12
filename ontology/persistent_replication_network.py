
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class PersistentReplicationNetwork:
    primitive = "persistent_replication_network"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "distributed_scientific_ecosystem"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _json_files(self) -> list[Path]:
        bases = [
            self.root / "external_validation",
            self.root / "replication_packages",
        ]
        files: list[Path] = []
        for base in bases:
            if base.exists():
                files.extend(base.rglob("*.json"))
        return sorted(set(files))

    def _extract_signal(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {
                "success": any(isinstance(x, dict) and bool(x.get("success", x.get("overall_success", False))) for x in data),
                "item_count": len(data),
            }
        return {}

    def step(self, persist: bool = True) -> dict[str, Any]:
        files = self._json_files()
        replication_files: list[str] = []
        successful_replication_records = 0
        external_replication_count = 0
        package_count = 0

        for path in files:
            low = str(path).lower()
            if "replication" in low:
                replication_files.append(str(path.relative_to(self.root)))
            if "replication_package" in low:
                package_count += 1
            data = self._extract_signal(self._read_json(path))
            if not data:
                continue
            if "replication" in low and bool(data.get("success", data.get("overall_success", False))):
                successful_replication_records += 1
            if "external_replication_count" in data:
                try:
                    external_replication_count = max(external_replication_count, int(data.get("external_replication_count") or 0))
                except Exception:
                    pass

        network_node_count = len(set(Path(p).parts[0] if Path(p).parts else p for p in replication_files))
        replication_link_count = len(replication_files)
        persistence_score = mean([
            min(1.0, len(replication_files) / 25.0),
            min(1.0, successful_replication_records / 10.0),
            min(1.0, package_count / 10.0),
            1.0 if external_replication_count > 0 else 0.5,
        ])
        resilience_index = mean([
            persistence_score,
            min(1.0, replication_link_count / 50.0),
            1.0 if package_count > 0 else 0.5,
        ])

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H20",
            "persistent_replication_network_ready": True,
            "external_replication_count": external_replication_count,
            "replication_file_count": len(replication_files),
            "successful_replication_record_count": successful_replication_records,
            "replication_package_count": package_count,
            "replication_network_node_count": network_node_count,
            "replication_link_count": replication_link_count,
            "network_persistence_score": round(persistence_score, 6),
            "network_resilience_index": round(resilience_index, 6),
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "diagnostics": {
                "non_closure_compliant": True,
                "traceability_ready": len(replication_files) > 0,
                "sample_replication_files": replication_files[-20:],
            },
        }

        if persist:
            state_path = self.output_dir / "latest_persistent_replication_network.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "persistent_replication_network.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)

        return result
