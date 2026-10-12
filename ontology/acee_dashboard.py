"""ACEE17 — unified read-only dashboard for autonomous cognitive evolution.

Consumes authoritative ACEE12/13/14/16 outputs. It does not execute cycles,
recompute impact/causality, select mutations, perform rollback, mutate lineage,
or alter architecture archives.
"""
from __future__ import annotations

import fcntl
import hashlib
import html
import json
import math
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_DASHBOARD"
STATUS_READY = "ACEE_DASHBOARD_READY"
STATUS_DEGRADED = "ACEE_DASHBOARD_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
REQUIRED_CHARTS = (
    "cycle_score_over_time", "error_count_over_time",
    "evolution_score_over_time", "governance_score_over_time",
    "rollback_count_over_time", "accepted_vs_rejected_mutations",
    "lineage_tree", "best_architecture_curve", "causal_impact_chart",
    "closure_pressure_curve", "stability_curve",
)
DECISIONS = ("accept", "reject", "rollback", "repeat", "sandbox_longer", "undetermined")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _list(value: Any) -> List[Any]:
    return deepcopy(list(value)) if isinstance(value, (list, tuple)) else []


def _finite(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


class ACEEDashboard:
    """Build deterministic JSON/HTML views from precomputed ACEE evidence."""

    def __init__(self, root: Path | None = None, runtime_dir: Path | None = None) -> None:
        self.root = (Path(root) if root is not None else Path.home() / "open-cognitive-ecology").expanduser().resolve()
        default = self.root / "acee_runtime" / "ACEE17_acee_dashboard"
        self.runtime_dir = (Path(runtime_dir) if runtime_dir is not None else default).expanduser().resolve()
        try:
            self.runtime_dir.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("runtime_dir_outside_root") from exc

    def _base(self, timestamp: str) -> Dict[str, Any]:
        return {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "status": STATUS_READY,
            "dashboard_ready": True,
            "timestamp_utc": timestamp,
            "cycle_count": 0,
            "charts": {name: {} if name in {"accepted_vs_rejected_mutations", "lineage_tree"} else [] for name in REQUIRED_CHARTS},
            "artifacts": {"json_path": None, "html_path": None},
            "persist_requested": False,
            "persisted": False,
            "source_integrity": {},
            "diagnostics": {"blocking_reasons": [], "warnings": []},
            "cycle_executed_by_dashboard": False,
            "validation_executed_by_dashboard": False,
            "impact_recomputed_by_dashboard": False,
            "causality_recomputed_by_dashboard": False,
            "selection_executed_by_dashboard": False,
            "rollback_executed_by_dashboard": False,
            "lineage_modified_by_dashboard": False,
            "archive_modified_by_dashboard": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
        }

    @staticmethod
    def _timestamp_key(record: Mapping[str, Any]) -> Tuple[str, str, str]:
        return (str(record.get("timestamp_utc") or ""), str(record.get("cycle_id") or ""), str(record.get("record_id") or ""))

    def _load_sources(self) -> Dict[str, Any]:
        sources: Dict[str, Any] = {}
        warnings: List[str] = []
        try:
            from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker
            sources["longitudinal"] = AceeLongitudinalTracker(root=self.root).step(inputs={"operation": "list_trajectory"}, persist=False)
        except Exception as exc:
            warnings.append(f"longitudinal_unavailable:{type(exc).__name__}")
            sources["longitudinal"] = {}
        try:
            from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy
            sources["genealogy"] = AceeArchitectureGenealogy(root=self.root).step(inputs={"operation": "list_genealogy"}, persist=False)
        except Exception as exc:
            warnings.append(f"genealogy_unavailable:{type(exc).__name__}")
            sources["genealogy"] = {}
        try:
            from ontology.acee_lineage_manager import AceeLineageManager
            sources["lineage"] = AceeLineageManager(root=self.root).step(inputs={"operation": "list_lineages"}, persist=False)
        except Exception as exc:
            warnings.append(f"lineage_unavailable:{type(exc).__name__}")
            sources["lineage"] = {}
        try:
            from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
            sources["archive"] = AceeBestArchitectureArchive(root=self.root).step(inputs={"operation": "list_best_architectures"}, persist=False)
        except Exception as exc:
            warnings.append(f"archive_unavailable:{type(exc).__name__}")
            sources["archive"] = {}
        sources["warnings"] = warnings
        return sources

    @staticmethod
    def _records_from(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        candidates = inputs.get("records")
        if candidates is None:
            longitudinal = _mapping(inputs.get("longitudinal"))
            candidates = longitudinal.get("trajectory") or longitudinal.get("cycles") or longitudinal.get("records")
        if isinstance(candidates, Mapping):
            candidates = list(candidates.values())
        return [_mapping(item) for item in _list(candidates) if isinstance(item, Mapping)]

    @staticmethod
    def _metric(record: Mapping[str, Any], *names: str) -> Optional[float]:
        for name in names:
            value = _finite(record.get(name))
            if value is not None:
                return value
            for container_name in ("impact_evaluation", "source_payloads", "metrics", "diagnostics"):
                container = record.get(container_name)
                if isinstance(container, Mapping):
                    if container_name == "source_payloads":
                        for payload in container.values():
                            if isinstance(payload, Mapping):
                                nested = _finite(payload.get(name))
                                if nested is not None:
                                    return nested
                    nested = _finite(container.get(name))
                    if nested is not None:
                        return nested
        return None

    def build_dashboard_model(self, inputs: Mapping[str, Any] | None = None) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        if not supplied:
            supplied = self._load_sources()
        timestamp = str(supplied.get("timestamp_utc") or _now())
        result = self._base(timestamp)
        records = sorted(self._records_from(supplied), key=self._timestamp_key)
        result["cycle_count"] = len(records)
        warnings = list(_list(supplied.get("warnings")))

        scores: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        evolution: List[Dict[str, Any]] = []
        governance: List[Dict[str, Any]] = []
        rollback_curve: List[Dict[str, Any]] = []
        causal: List[Dict[str, Any]] = []
        closure: List[Dict[str, Any]] = []
        stability: List[Dict[str, Any]] = []
        decision_counts = {name: 0 for name in DECISIONS}
        rollback_count = 0

        for index, record in enumerate(records, start=1):
            cycle_id = str(record.get("cycle_id") or f"cycle-{index}")
            point = {"index": index, "cycle_id": cycle_id, "timestamp_utc": str(record.get("timestamp_utc") or "")}
            before = self._metric(record, "before_score", "baseline_score")
            after = self._metric(record, "after_score", "candidate_score")
            delta = self._metric(record, "score_delta", "impact_score")
            scores.append({**point, "before_score": before, "after_score": after, "score_delta": delta})
            errors.append({**point, "error_count": self._metric(record, "error_count")})
            evolution.append({**point, "evolution_score": self._metric(record, "evolution_score")})
            governance.append({**point, "governance_score": self._metric(record, "governance_score")})
            rollback_performed = record.get("rollback_performed") is True
            if rollback_performed:
                rollback_count += 1
            rollback_curve.append({**point, "rollback_count": rollback_count, "rollback_performed": rollback_performed, "rollback_phase_completed": record.get("rollback_phase_completed") is True})
            decision = str(record.get("decision") or "undetermined").strip().lower()
            if decision not in decision_counts:
                warnings.append(f"unknown_decision:{decision}")
                decision = "undetermined"
            decision_counts[decision] += 1
            causal.append({**point, "causal_impact": self._metric(record, "causal_impact", "causal_effect", "causal_score")})
            closure.append({**point, "closure_pressure": self._metric(record, "closure_pressure")})
            stability.append({**point, "stability_score": self._metric(record, "stability_score")})

        genealogy = _mapping(supplied.get("genealogy"))
        lineage = _mapping(supplied.get("lineage"))
        archive = _mapping(supplied.get("archive"))
        lineage_tree = genealogy.get("genealogy") or genealogy.get("graph") or genealogy.get("lineage_tree") or lineage.get("lineages") or {}
        archives = archive.get("archives") or supplied.get("archives") or []
        if isinstance(archives, Mapping):
            archives = list(archives.values())
        best_curve = []
        best_seen: Optional[float] = None
        for item in sorted([_mapping(x) for x in _list(archives)], key=lambda x: (str(x.get("timestamp_utc") or ""), str(x.get("archive_id") or ""))):
            score = _finite(item.get("architecture_score", item.get("score")))
            if score is None:
                warnings.append("archive_score_invalid")
                continue
            best_seen = score if best_seen is None else max(best_seen, score)
            best_curve.append({"archive_id": item.get("archive_id"), "timestamp_utc": item.get("timestamp_utc"), "architecture_score": score, "best_score": best_seen})

        result["charts"] = {
            "cycle_score_over_time": scores,
            "error_count_over_time": errors,
            "evolution_score_over_time": evolution,
            "governance_score_over_time": governance,
            "rollback_count_over_time": rollback_curve,
            "accepted_vs_rejected_mutations": decision_counts,
            "lineage_tree": deepcopy(lineage_tree) if isinstance(lineage_tree, (dict, list)) else {},
            "best_architecture_curve": best_curve,
            "causal_impact_chart": causal,
            "closure_pressure_curve": closure,
            "stability_curve": stability,
        }
        result["source_integrity"] = {
            "records_ordered": records == sorted(records, key=self._timestamp_key),
            "rollback_semantics_separated": all(point["rollback_count"] >= 0 for point in rollback_curve),
            "source_payloads_modified": False,
        }
        result["diagnostics"]["warnings"] = sorted(set(str(x) for x in warnings))
        result["dashboard_hash"] = _sha({
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "cycle_count": result["cycle_count"],
            "charts": result["charts"],
            "epistemic": {key: result[key] for key in (
                "functional_conclusion_only", "phenomenology_undetermined",
                "consciousness_proven", "subjectivity_proven", "qualia_proven",
                "phenomenology_proven", "collective_consciousness_proven",
                "collective_subjectivity_proven", "collective_qualia_proven",
                "collective_phenomenology_proven",
            )},
        })
        return result

    def render_html(self, dashboard_model: Mapping[str, Any]) -> str:
        model = _mapping(dashboard_model)
        charts = _mapping(model.get("charts"))
        summary_rows = [
            ("cycle_count", model.get("cycle_count", 0)),
            ("rollback_count", (charts.get("rollback_count_over_time") or [{}])[-1].get("rollback_count", 0) if charts.get("rollback_count_over_time") else 0),
            ("dashboard_hash", model.get("dashboard_hash", "")),
        ]
        rows = "".join(f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k, v in summary_rows)
        sections = []
        for name in REQUIRED_CHARTS:
            encoded = html.escape(json.dumps(charts.get(name), ensure_ascii=False, sort_keys=True))
            sections.append(f"<section><h2>{html.escape(name)}</h2><pre>{encoded}</pre></section>")
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>ACEE17 Dashboard</title>"
            "<style>body{font-family:Arial,sans-serif;margin:32px;max-width:1400px}table{border-collapse:collapse;width:100%}"
            "th,td{border:1px solid #ccc;padding:8px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f5f5;padding:12px}"
            ".guard{padding:12px;background:#fff4cc}</style></head><body><h1>ACEE17 Unified Dashboard</h1>"
            "<p class='guard'>Functional evidence only. Phenomenology remains undetermined; no consciousness, subjectivity or qualia proof is asserted.</p>"
            f"<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>{''.join(sections)}</body></html>"
        )

    def verify_dashboard(self, dashboard: Mapping[str, Any]) -> Dict[str, Any]:
        payload = _mapping(dashboard)
        reasons: List[str] = []
        charts = payload.get("charts")
        if not isinstance(charts, Mapping):
            reasons.append("charts_missing")
        else:
            for name in REQUIRED_CHARTS:
                if name not in charts:
                    reasons.append(f"chart_missing:{name}")
        if payload.get("functional_conclusion_only") is not True or payload.get("phenomenology_undetermined") is not True:
            reasons.append("epistemic_guard_missing")
        for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven", "collective_consciousness_proven", "collective_subjectivity_proven", "collective_qualia_proven", "collective_phenomenology_proven"):
            if payload.get(key) is not False:
                reasons.append(f"epistemic_violation:{key}")
        expected = _sha({
            "public_schema_version": payload.get("public_schema_version"),
            "cycle_count": payload.get("cycle_count"),
            "charts": payload.get("charts"),
            "epistemic": {key: payload.get(key) for key in (
                "functional_conclusion_only", "phenomenology_undetermined",
                "consciousness_proven", "subjectivity_proven", "qualia_proven",
                "phenomenology_proven", "collective_consciousness_proven",
                "collective_subjectivity_proven", "collective_qualia_proven",
                "collective_phenomenology_proven",
            )},
        })
        if payload.get("dashboard_hash") != expected:
            reasons.append("dashboard_hash_invalid")
        return {"verified": not reasons, "verification_errors": reasons}

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        model = self.build_dashboard_model(supplied)
        verification = self.verify_dashboard(model)
        model["verification"] = verification
        model["persist_requested"] = bool(persist)
        if not verification["verified"]:
            model["status"] = STATUS_DEGRADED
            model["dashboard_ready"] = False
            model["diagnostics"]["blocking_reasons"] = list(
                verification["verification_errors"]
            )
            return model

        if not persist:
            html_text = self.render_html(model)
            json_payload = deepcopy(model)
            json_payload["exports"] = {"json": None, "html": html_text}
            model["exports"] = {
                "json": json.dumps(
                    json_payload,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                "html": html_text,
            }
            return model

        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.runtime_dir / ".dashboard.lock"
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            json_path = self.runtime_dir / "latest_dashboard.json"
            html_path = self.runtime_dir / "latest_dashboard.html"

            model["artifacts"] = {
                "json_path": str(json_path),
                "html_path": str(html_path),
            }
            model["persisted"] = True

            html_text = self.render_html(model)
            persisted_payload = deepcopy(model)
            persisted_payload["exports"] = {
                "json": None,
                "html": html_text,
            }
            json_text = json.dumps(
                persisted_payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            model["exports"] = {
                "json": json_text,
                "html": html_text,
            }

            _atomic_write(json_path, json_text)
            _atomic_write(html_path, html_text)

        return model


if __name__ == "__main__":
    print(ACEEDashboard().step(inputs={}, persist=True)["status"])
