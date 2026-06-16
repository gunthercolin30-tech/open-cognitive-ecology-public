from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


class ResidualLocalArtifactClassifier:
    """
    F17.3 — Residual Local Artifact Classifier.

    Classifies remaining local artifacts after F17.1/F17.2 into:
    KEEP_LOCAL, MOVE_TO_SSD, ROUTE_PRODUCER, MANUAL_REVIEW.

    This module does not delete files. It produces auditable reports only.
    Functional-only validation: no phenomenal subjectivity claim.
    """

    primitive = "residual_local_artifact_classifier"
    refinement = "F17.3-R1"

    KEEP_LOCAL_PREFIXES = (
        ".git/",
        ".venv/",
        "ontology/",
        "validation/",
        "docs/",
        ".pytest_cache/",
        "__pycache__/",
    )

    KEEP_LOCAL_EXACT = {
        "ontology_inventory.txt",
        "ontology_integration_report.txt",
        "dependency_registry.py",
        "README.md",
        ".DS_Store",
    }

    ROUTE_PRODUCER_PREFIXES = (
        "terminal_conversation_runtime/",
        "distributed_identity_state/",
        "distributed_attention_state/",
        "external_collaboration_execution/",
        "runtime_experiments/",
        "metrics/",
        "grafana/",
        "civilizational_mutation/",
        "distributed_nodes/",
        "community_nodes/",
        "external_collaboration/",
        "external_memory/",
        "local_storage_fallback/",
        "collaboration_history_repository_archive/",
        "secrets/",
    )

    MOVE_TO_SSD_SUFFIXES = (
        ".jsonl",
        ".json",
        ".prom",
        ".html",
        ".db",
        ".sqlite",
        ".csv",
        ".gz",
    )

    REVIEW_SUFFIXES = (
        ".zip",
        ".pdf",
        ".docx",
        ".numbers",
        ".txt",
        ".md",
    )

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _route_destination_hint(self, rel: str) -> str:
        s = rel.lower()
        name = Path(rel).name.lower()

        if "metric" in s or name.endswith(".prom") or s.startswith("metrics/"):
            return str(self.ssd_root / "OCE_METRICS" / "residual_local_artifacts" / rel)
        if "dashboard" in s or name.endswith(".html") or "grafana" in s:
            return str(self.ssd_root / "OCE_DASHBOARDS" / "residual_local_artifacts" / rel)
        if "memory" in s or name.endswith(".db") or name.endswith(".sqlite") or "knowledge" in s:
            return str(self.ssd_root / "OCE_MEMORY" / "residual_local_artifacts" / rel)
        if "experiment" in s or "runtime_experiments" in s:
            return str(self.ssd_root / "OCE_EXPERIMENTS" / "residual_local_artifacts" / rel)
        if (
            "distributed" in s
            or "continuity" in s
            or "node" in s
            or "replication" in s
            or "migration" in s
            or "recovery" in s
        ):
            return str(self.ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY" / "residual_local_artifacts" / rel)
        return str(self.ssd_root / "OCE_ARCHIVE" / "residual_local_artifacts" / rel)

    def _producer_hint(self, rel: str) -> str:
        top = rel.split("/", 1)[0]
        direct = {
            "terminal_conversation_runtime": "persistent_civilizational_conversational_agent or proactive terminal runtime producer",
            "distributed_identity_state": "distributed_identity_persistence_validator",
            "distributed_attention_state": "distributed_attention_state_exchange",
            "external_collaboration_execution": "autonomous_external_collaboration_runner or external_collaboration_gateway",
            "runtime_experiments": "runtime experiment / scientific validation / population simulation producers",
            "metrics": "metrics_history_recorder / prometheus exporter / grafana exporter",
            "grafana": "grafana dashboard exporter",
            "civilizational_mutation": "mutation and controlled evolution producers",
            "distributed_nodes": "distributed_civilizational_node / inter_individual_coordination_protocol / migration / replication",
            "community_nodes": "real_community_node_certification",
            "external_memory": "persistent_external_memory_fabric legacy local database",
            "local_storage_fallback": "civilizational_storage_router fallback generated during SSD-absent test",
            "external_collaboration": "autonomous external collaboration runner",
            "secrets": "credential vault or credential access audit",
        }
        return direct.get(top, "unknown_or_manual_review")

    def classify_path(self, path: Path) -> Dict[str, Any]:
        rel = str(path.relative_to(self.root))
        suffix = path.suffix.lower()
        size = path.stat().st_size if path.exists() else 0

        if rel in self.KEEP_LOCAL_EXACT or rel.startswith(self.KEEP_LOCAL_PREFIXES):
            cls = "KEEP_LOCAL"
            reason = "source_code_validation_git_or_environment_file"
            action = "do_not_move"
        elif rel.startswith(self.ROUTE_PRODUCER_PREFIXES):
            cls = "ROUTE_PRODUCER"
            reason = "active_runtime_artifact_directory_still_local"
            action = "patch_producer_or_route_directory_before_delete"
        elif suffix in self.MOVE_TO_SSD_SUFFIXES:
            cls = "MOVE_TO_SSD"
            reason = "runtime_artifact_suffix_and_no_keep_rule"
            action = "copy_to_ssd_with_checksum_then_delete_after_non_reappearance_test"
        elif suffix in self.REVIEW_SUFFIXES or "gunther_corpus/" in rel:
            cls = "MANUAL_REVIEW"
            reason = "human_or_phase_archive_document_requires_explicit_decision"
            action = "review_before_move_or_delete"
        else:
            cls = "MANUAL_REVIEW"
            reason = "unclassified_residual_file"
            action = "review_before_action"

        return {
            "relative_path": rel,
            "size_bytes": size,
            "suffix": suffix,
            "classification": cls,
            "reason": reason,
            "recommended_action": action,
            "destination_hint": self._route_destination_hint(rel) if cls in {"MOVE_TO_SSD", "ROUTE_PRODUCER"} else None,
            "producer_hint": self._producer_hint(rel),
        }

    def discover(self) -> List[Path]:
        return sorted((p for p in self.root.rglob("*") if p.is_file()), key=lambda p: str(p.relative_to(self.root)))

    def _summary(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for row in rows:
            cls = row["classification"]
            item = summary.setdefault(cls, {"file_count": 0, "size_bytes": 0})
            item["file_count"] += 1
            item["size_bytes"] += int(row.get("size_bytes") or 0)
        return summary

    def _markdown_report(self, payload: Dict[str, Any]) -> str:
        summary = payload["summary"]
        lines = [
            "# F17.3 Residual Local Artifact Classification",
            "",
            f"- generated_at_utc: `{payload['timestamp_utc']}`",
            f"- root: `{payload['root']}`",
            f"- ssd_root: `{payload['ssd_root']}`",
            f"- ssd_available: `{payload['ssd_available']}`",
            f"- total_files: `{payload['total_files']}`",
            "",
            "## Summary",
            "",
            "| Classification | Files | Bytes |",
            "|---|---:|---:|",
        ]
        for cls in ["KEEP_LOCAL", "MOVE_TO_SSD", "ROUTE_PRODUCER", "MANUAL_REVIEW"]:
            item = summary.get(cls, {"file_count": 0, "size_bytes": 0})
            lines.append(f"| {cls} | {item['file_count']} | {item['size_bytes']} |")

        lines.extend([
            "",
            "## Priority residual producers",
            "",
        ])

        route_rows = [r for r in payload["rows"] if r["classification"] == "ROUTE_PRODUCER"]
        for r in sorted(route_rows, key=lambda x: x["size_bytes"], reverse=True)[:80]:
            lines.append(f"- `{r['relative_path']}` — {r['size_bytes']} bytes — {r['producer_hint']}")

        lines.extend([
            "",
            "## Large manual-review files",
            "",
        ])

        manual_rows = [r for r in payload["rows"] if r["classification"] == "MANUAL_REVIEW"]
        for r in sorted(manual_rows, key=lambda x: x["size_bytes"], reverse=True)[:80]:
            lines.append(f"- `{r['relative_path']}` — {r['size_bytes']} bytes — {r['reason']}")

        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[dict] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        persist = bool(inputs.get("persist", True))
        max_files = inputs.get("max_files")
        if max_files is not None:
            max_files = int(max_files)

        files = self.discover()
        if max_files is not None:
            files = files[:max_files]

        rows = [self.classify_path(p) for p in files]
        summary = self._summary(rows)
        digest = _sha256_text(json.dumps(rows, ensure_ascii=False, sort_keys=True))

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "root": str(self.root),
            "ssd_root": str(self.ssd_root),
            "ssd_available": self._ssd_available(),
            "total_files": len(rows),
            "summary": summary,
            "rows_sha256": digest,
            "rows": rows,
            "deletion_performed": False,
            "epistemic_boundary": "functional_storage_classification_only_no_phenomenal_subjectivity_claim",
        }

        report_json = None
        report_md = None

        if persist:
            if self._ssd_available():
                base = self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_3_residual_classifier"
            else:
                base = self.root / "local_storage_fallback" / "archive" / "f17_3_residual_classifier"
            base.mkdir(parents=True, exist_ok=True)
            report_json = base / "f17_3_residual_local_artifact_classification.json"
            report_md = base / "f17_3_residual_local_artifact_classification.md"
            report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            report_md.write_text(self._markdown_report(payload), encoding="utf-8")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": "Residual Local Artifact Classification Completed",
            "ssd_available": self._ssd_available(),
            "total_files": len(rows),
            "summary": summary,
            "route_producer_count": summary.get("ROUTE_PRODUCER", {}).get("file_count", 0),
            "move_to_ssd_count": summary.get("MOVE_TO_SSD", {}).get("file_count", 0),
            "manual_review_count": summary.get("MANUAL_REVIEW", {}).get("file_count", 0),
            "keep_local_count": summary.get("KEEP_LOCAL", {}).get("file_count", 0),
            "report_json": str(report_json) if report_json else None,
            "report_md": str(report_md) if report_md else None,
            "deletion_performed": False,
            "non_closure_compliant": True,
            "next_step": "F17.4 targeted producer routing or controlled residual migration",
            "epistemic_boundary": payload["epistemic_boundary"],
        }
