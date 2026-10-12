from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"


class ComparativeHistory:
    """AU9 append-only longitudinal history for stable AU8 comparative states."""

    primitive = "comparative_history"
    step_id = "AU9"
    public_schema_version = "1.0.0"
    ready_status = "COMPARATIVE_HISTORY_READY"
    incomplete_status = "COMPARATIVE_HISTORY_INCOMPLETE"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "comparative_science" / "history"
        self.history_path = self.output_dir / "comparative_history.jsonl"
        self.latest_path = self.output_dir / "latest_comparative_history.json"
        self.index_path = self.output_dir / "comparative_history_index.json"
        self.markdown_path = self.output_dir / "latest_comparative_history.md"

    @staticmethod
    def _stable_hash(payload: Any) -> str:
        data = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def _dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _dashboard(self, inputs: dict[str, Any]) -> dict[str, Any]:
        supplied = inputs.get("comparative_dashboard")
        if isinstance(supplied, dict):
            return dict(supplied)
        from ontology.comparative_dashboard import ComparativeDashboard
        dashboard_inputs = inputs.get("dashboard_inputs")
        if not isinstance(dashboard_inputs, dict):
            dashboard_inputs = {}
        return ComparativeDashboard().step(inputs=dashboard_inputs, persist=False)

    def _snapshot_payload(self, dashboard: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "dashboard_hash": dashboard.get("dashboard_hash"),
            "dashboard_summary": self._dict(dashboard.get("dashboard_summary")),
            "architecture_registry": self._list(dashboard.get("architecture_registry")),
            "rf_profiles": self._list(dashboard.get("rf_profiles")),
            "pairwise_similarities": self._list(dashboard.get("pairwise_similarities")),
            "similarity_matrix": self._dict(dashboard.get("similarity_matrix")),
            "pairwise_distances": self._list(dashboard.get("pairwise_distances")),
            "distance_matrix": self._dict(dashboard.get("distance_matrix")),
            "clusters": self._list(dashboard.get("clusters")),
            "cluster_assignments": self._dict(dashboard.get("cluster_assignments")),
            "medoids": self._dict(dashboard.get("medoids")),
            "outliers": self._list(dashboard.get("outliers")),
            "taxonomy": self._dict(dashboard.get("taxonomy")),
            "taxonomy_entries": self._list(dashboard.get("taxonomy_entries")),
            "taxonomy_hash": dashboard.get("taxonomy_hash"),
            "coverage": self._dict(dashboard.get("coverage")),
            "data_quality": self._dict(dashboard.get("data_quality")),
            "comparability": self._dict(dashboard.get("comparability")),
            "auditability": self._dict(dashboard.get("auditability")),
            "epistemic_guards": self._dict(dashboard.get("epistemic_guards")),
        }

    def _read_records(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append(value)
        return records

    @staticmethod
    def _architecture_ids(items: list[Any]) -> set[str]:
        output: set[str] = set()
        for item in items:
            if isinstance(item, dict) and item.get("architecture_id") is not None:
                output.add(str(item["architecture_id"]))
        return output

    def _change_set(
        self,
        previous: Mapping[str, Any] | None,
        current: Mapping[str, Any],
    ) -> dict[str, Any]:
        if previous is None:
            current_ids = sorted(self._architecture_ids(self._list(current.get("architecture_registry"))))
            return {
                "change_type": "INITIAL_SNAPSHOT",
                "changed": True,
                "added_architectures": current_ids,
                "removed_architectures": [],
                "profiles_changed": bool(current.get("rf_profiles")),
                "similarities_changed": bool(current.get("similarity_matrix")),
                "distances_changed": bool(current.get("distance_matrix")),
                "clusters_changed": bool(current.get("cluster_assignments")),
                "taxonomy_changed": bool(current.get("taxonomy_hash") or current.get("taxonomy")),
                "coverage_changed": bool(current.get("coverage")),
                "data_quality_changed": bool(current.get("data_quality")),
            }
        old_ids = self._architecture_ids(self._list(previous.get("architecture_registry")))
        new_ids = self._architecture_ids(self._list(current.get("architecture_registry")))
        flags = {
            "added_architectures": sorted(new_ids - old_ids),
            "removed_architectures": sorted(old_ids - new_ids),
            "profiles_changed": previous.get("rf_profiles") != current.get("rf_profiles"),
            "similarities_changed": previous.get("similarity_matrix") != current.get("similarity_matrix"),
            "distances_changed": previous.get("distance_matrix") != current.get("distance_matrix"),
            "clusters_changed": (
                previous.get("clusters") != current.get("clusters")
                or previous.get("cluster_assignments") != current.get("cluster_assignments")
                or previous.get("medoids") != current.get("medoids")
                or previous.get("outliers") != current.get("outliers")
            ),
            "taxonomy_changed": (
                previous.get("taxonomy_hash") != current.get("taxonomy_hash")
                or previous.get("taxonomy") != current.get("taxonomy")
                or previous.get("taxonomy_entries") != current.get("taxonomy_entries")
            ),
            "coverage_changed": previous.get("coverage") != current.get("coverage"),
            "data_quality_changed": previous.get("data_quality") != current.get("data_quality"),
        }
        changed = any(bool(value) for value in flags.values())
        return {
            "change_type": "COMPARATIVE_STATE_CHANGED" if changed else "NO_CHANGE",
            "changed": changed,
            **flags,
        }

    def _validate_chain(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        previous_hash: str | None = None
        valid_count = 0
        errors: list[str] = []
        for index, record in enumerate(records, start=1):
            if record.get("sequence_index") != index:
                errors.append(f"sequence_mismatch:{index}")
            if record.get("previous_record_hash") != previous_hash:
                errors.append(f"previous_hash_mismatch:{index}")
            expected = self._stable_hash({k: v for k, v in record.items() if k != "record_hash"})
            if record.get("record_hash") != expected:
                errors.append(f"record_hash_mismatch:{index}")
            else:
                valid_count += 1
            previous_hash = str(record.get("record_hash")) if record.get("record_hash") else None
        return {
            "chain_valid": not errors,
            "record_count": len(records),
            "valid_record_count": valid_count,
            "chain_errors": errors,
            "head_hash": previous_hash,
        }

    def _write(self, result: dict[str, Any], record: dict[str, Any] | None) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if record is not None:
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        records = self._read_records()
        chain = self._validate_chain(records)
        index = {
            "primitive": self.primitive,
            "public_schema_version": self.public_schema_version,
            "record_count": len(records),
            "head_hash": chain["head_hash"],
            "chain_valid": chain["chain_valid"],
            "history_path": str(self.history_path),
        }
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        md = "\n".join([
            "# AU9 Comparative History", "",
            "Functional comparative history only. No phenomenology, qualia, subjectivity or consciousness proof is asserted.", "",
            f"Status: `{result['comparative_history_status']}`", "",
            f"Snapshot hash: `{result['snapshot_hash']}`", "",
            f"Change type: `{result['change_set']['change_type']}`", "",
            f"History count: `{result['history_count_after']}`", "",
            f"Chain valid: `{result['chain_integrity']['chain_valid']}`",
        ])
        self.markdown_path.write_text(md, encoding="utf-8")
        return {
            "jsonl": str(self.history_path),
            "latest_json": str(self.latest_path),
            "index_json": str(self.index_path),
            "markdown": str(self.markdown_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        dashboard = self._dashboard(inputs)
        dashboard_ready = (
            dashboard.get("comparative_dashboard_status") == "COMPARATIVE_DASHBOARD_READY"
            and dashboard.get("comparative_dashboard_ready") is True
            and isinstance(dashboard.get("dashboard_hash"), str)
            and len(str(dashboard.get("dashboard_hash"))) == 64
        )
        snapshot = self._snapshot_payload(dashboard)
        snapshot_hash = self._stable_hash(snapshot)
        existing = self._read_records()
        prior = existing[-1] if existing else None
        prior_snapshot = prior.get("snapshot") if isinstance(prior, dict) and isinstance(prior.get("snapshot"), dict) else None
        change_set = self._change_set(prior_snapshot, snapshot)
        append_required = bool(dashboard_ready and change_set["changed"])
        previous_record_hash = prior.get("record_hash") if isinstance(prior, dict) else None
        record: dict[str, Any] | None = None
        if append_required:
            record = {
                "sequence_index": len(existing) + 1,
                "timestamp_utc": self._now(),
                "snapshot_hash": snapshot_hash,
                "dashboard_hash": dashboard.get("dashboard_hash"),
                "previous_record_hash": previous_record_hash,
                "change_set": change_set,
                "snapshot": snapshot,
                "append_only_policy": "no_deletion_no_mutation_append_only_jsonl",
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_proven": False,
            }
            record["record_hash"] = self._stable_hash({k: v for k, v in record.items() if k != "record_hash"})
        projected_records = list(existing)
        if persist and record is not None:
            projected_records.append(record)
        chain_integrity = self._validate_chain(projected_records)
        ready = bool(dashboard_ready and chain_integrity["chain_valid"])
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": self.ready_status if ready else self.incomplete_status,
            "comparative_history_status": self.ready_status if ready else self.incomplete_status,
            "comparative_history_ready": ready,
            "dashboard_ready": dashboard_ready,
            "snapshot_hash": snapshot_hash,
            "dashboard_hash": dashboard.get("dashboard_hash"),
            "change_set": change_set,
            "append_required": append_required,
            "append_only": True,
            "history_count_before": len(existing),
            "history_count_after": len(existing) + (1 if persist and record is not None else 0),
            "record": record,
            "record_hash": record.get("record_hash") if record else None,
            "previous_record_hash": previous_record_hash,
            "chain_integrity": chain_integrity,
            "canonical_paths": {
                "history": str(self.history_path),
                "latest": str(self.latest_path),
                "index": str(self.index_path),
                "markdown": str(self.markdown_path),
            },
            "persist_requested": bool(persist),
            "persisted": False,
            "output_paths": {},
            "epistemic_scope": "functional_comparative_history_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        if persist and ready:
            result["output_paths"] = self._write(result, record)
            result["persisted"] = True
            persisted_records = self._read_records()
            result["history_count_after"] = len(persisted_records)
            result["chain_integrity"] = self._validate_chain(persisted_records)
        return result


if __name__ == "__main__":
    print(ComparativeHistory().step(inputs={}, persist=True)["comparative_history_status"])
