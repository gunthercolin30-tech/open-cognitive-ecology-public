
"""
O13 — Collaboration History Repository

Consolidated civilizational archive for the external cognitive collaboration
pipeline O1→O12. This primitive does not replace local histories produced by
upstream modules. It reads them, tolerates missing or partially corrupted JSONL
files, aggregates traceable evidence, computes collaboration metrics, and
persists a repository-level historical record for O14 and E9/E10.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PRIMITIVE = "collaboration_history_repository"

DEPENDENCIES = [
    "external_collaboration_gateway",
    "interaction_queue_manager",
    "external_response_parser",
    "contradiction_detection_system",
    "knowledge_integration_engine",
    "identity_preservation_monitor",
    "governance_consistency_checker",
    "civilizational_continuity_guardian",
    "civilizational_memory_archive",
    "metrics_history_recorder",
]


@dataclass(frozen=True)
class SourceSpec:
    key: str
    filename: str
    semantic_role: str


class CollaborationHistoryRepository:
    """
    Consolidate the O-phase external collaboration history.

    The class is intentionally conservative: no network access, no automatic
    execution of external providers, no mutation of upstream histories. It only
    reads, normalizes, summarizes, and persists its own repository outputs.
    """

    SOURCES: tuple[SourceSpec, ...] = (
        SourceSpec("collaboration_history", "collaboration_history.jsonl", "gateway_or_general_history"),
        SourceSpec("gateway_history", "external_collaboration_gateway_history.jsonl", "gateway_events"),
        SourceSpec("external_queries", "external_queries_archive.jsonl", "external_query_archive"),
        SourceSpec("integrated_responses", "integrated_responses_archive.jsonl", "integrated_response_archive"),
        SourceSpec("capability_evolution", "external_capability_evolution_history.jsonl", "external_capability_evolution"),
        SourceSpec("continuity", "civilizational_continuity_history.jsonl", "civilizational_continuity_guardian"),
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.repository_path = self.root / "collaboration_history_repository.jsonl"
        self.summary_path = self.root / "collaboration_history_repository_summary.json"
        self.archive_dir = self.root / "collaboration_history_repository_archive"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
        try:
            numeric = float(value)
        except Exception:
            return low
        return max(low, min(high, numeric))

    def _read_jsonl(self, path: Path) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []
        corrupted_lines = 0
        missing = not path.exists()
        if missing:
            return {
                "path": str(path),
                "exists": False,
                "records": [],
                "line_count": 0,
                "corrupted_lines": 0,
            }

        line_count = 0
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    raw = line.strip()
                    if not raw:
                        continue
                    line_count += 1
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict):
                            records.append(parsed)
                        else:
                            records.append({"value": parsed})
                    except json.JSONDecodeError:
                        corrupted_lines += 1
        except OSError:
            corrupted_lines += 1

        return {
            "path": str(path),
            "exists": True,
            "records": records,
            "line_count": line_count,
            "corrupted_lines": corrupted_lines,
        }

    def _load_sources(self) -> Dict[str, Dict[str, Any]]:
        loaded: Dict[str, Dict[str, Any]] = {}
        for spec in self.SOURCES:
            data = self._read_jsonl(self.root / spec.filename)
            data["semantic_role"] = spec.semantic_role
            loaded[spec.key] = data
        return loaded

    @staticmethod
    def _flatten_records(sources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        flattened: List[Dict[str, Any]] = []
        for key, payload in sources.items():
            for record in payload.get("records", []):
                enriched = dict(record)
                enriched.setdefault("source", key)
                enriched["repository_source"] = key
                flattened.append(enriched)
        return flattened

    @staticmethod
    def _count_matches(records: Iterable[Dict[str, Any]], terms: Iterable[str]) -> int:
        lowered_terms = [term.lower() for term in terms]
        count = 0
        for record in records:
            text = json.dumps(record, ensure_ascii=False, sort_keys=True).lower()
            if any(term in text for term in lowered_terms):
                count += 1
        return count

    def _compute_metrics(self, sources: Dict[str, Dict[str, Any]], records: List[Dict[str, Any]]) -> Dict[str, Any]:
        source_count = len(sources)
        available_sources = sum(1 for payload in sources.values() if payload.get("exists"))
        total_records = len(records)
        total_lines = sum(int(payload.get("line_count", 0)) for payload in sources.values())
        corrupted_lines = sum(int(payload.get("corrupted_lines", 0)) for payload in sources.values())

        sent_or_query_count = self._count_matches(records, ["query", "send", "sent", "request", "package"])
        answered_count = self._count_matches(records, ["answer", "answered", "response", "captured"])
        integrated_count = self._count_matches(records, ["integrated", "integration", "accepted"])
        rejected_or_blocked_count = self._count_matches(records, ["rejected", "blocked", "contradiction", "violation"])
        continuity_count = self._count_matches(records, ["continuity", "civilizational", "identity", "governance"])

        source_coverage = self._bounded(available_sources / source_count if source_count else 0.0)
        corruption_penalty = self._bounded(corrupted_lines / max(1, total_lines))
        archival_density = self._bounded(total_records / 20.0)
        integration_ratio = self._bounded(integrated_count / max(1, answered_count or sent_or_query_count or total_records))
        continuity_coverage = self._bounded(continuity_count / max(1, total_records))
        rejection_pressure = self._bounded(rejected_or_blocked_count / max(1, total_records))

        external_collaboration_index = self._bounded(
            0.25 * source_coverage
            + 0.25 * archival_density
            + 0.20 * integration_ratio
            + 0.20 * continuity_coverage
            + 0.10 * (1.0 - corruption_penalty)
        )

        collaborative_growth_rate = self._bounded(integrated_count / max(1, total_records))
        autonomous_resolution_ratio = self._bounded((answered_count + integrated_count) / max(1, sent_or_query_count + answered_count + integrated_count))
        external_influence_ratio = self._bounded((integrated_count + rejected_or_blocked_count) / max(1, total_records))

        return {
            "source_count": source_count,
            "available_sources": available_sources,
            "record_count": total_records,
            "line_count": total_lines,
            "corrupted_lines": corrupted_lines,
            "sent_or_query_count": sent_or_query_count,
            "answered_count": answered_count,
            "integrated_count": integrated_count,
            "rejected_or_blocked_count": rejected_or_blocked_count,
            "continuity_count": continuity_count,
            "source_coverage": source_coverage,
            "archival_density": archival_density,
            "integration_ratio": integration_ratio,
            "continuity_coverage": continuity_coverage,
            "corruption_penalty": corruption_penalty,
            "external_collaboration_index": external_collaboration_index,
            "collaborative_growth_rate": collaborative_growth_rate,
            "autonomous_resolution_ratio": autonomous_resolution_ratio,
            "external_influence_ratio": external_influence_ratio,
            "repository_ready": external_collaboration_index >= 0.35 and available_sources >= 1,
            "ready_for_external_capability_planner": external_collaboration_index >= 0.35 and corruption_penalty < 0.50,
        }

    def _write_jsonl(self, path: Path, record: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _write_json(self, path: Path, record: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2, sort_keys=True)

    def step(self, persist: bool = True, max_records: int = 250) -> Dict[str, Any]:
        sources = self._load_sources()
        records = self._flatten_records(sources)
        if max_records and len(records) > max_records:
            records_for_archive = records[-max_records:]
        else:
            records_for_archive = records

        metrics = self._compute_metrics(sources, records)
        timestamp = self._now()

        source_stats = {
            key: {
                "path": payload.get("path"),
                "exists": payload.get("exists"),
                "semantic_role": payload.get("semantic_role"),
                "line_count": payload.get("line_count", 0),
                "record_count": len(payload.get("records", [])),
                "corrupted_lines": payload.get("corrupted_lines", 0),
            }
            for key, payload in sources.items()
        }

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "success": True,
            "repository_ready": metrics["repository_ready"],
            "ready_for_external_capability_planner": metrics["ready_for_external_capability_planner"],
            "external_collaboration_index": metrics["external_collaboration_index"],
            "collaborative_growth_rate": metrics["collaborative_growth_rate"],
            "autonomous_resolution_ratio": metrics["autonomous_resolution_ratio"],
            "external_influence_ratio": metrics["external_influence_ratio"],
            "record_count": metrics["record_count"],
            "source_stats": source_stats,
            "metrics": metrics,
            "diagnostics": {
                "non_redundant_role": "consolidates fragmented O1-O12 histories without replacing upstream archives",
                "history_files_observed": metrics["available_sources"],
                "corruption_tolerant": True,
                "bounded_metrics": True,
                "next_pipeline_stage": "external_capability_planner",
            },
        }

        if persist:
            self._write_jsonl(self.repository_path, result)
            self._write_json(self.summary_path, result)
            archive_record = {
                "primitive": PRIMITIVE,
                "timestamp_utc": timestamp,
                "records": records_for_archive,
                "metrics": metrics,
                "source_stats": source_stats,
            }
            archive_name = "archive_" + timestamp.replace(":", "").replace("+", "Z") + ".json"
            self._write_json(self.archive_dir / archive_name, archive_record)
            result["repository_path"] = str(self.repository_path)
            result["summary_path"] = str(self.summary_path)
            result["archive_path"] = str(self.archive_dir / archive_name)

        return result


if __name__ == "__main__":
    from pprint import pprint

    pprint(CollaborationHistoryRepository().step())
