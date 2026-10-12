"""
M9 — scientific_revision_execution_monitor.

This primitive observes the governed execution of scientific self-revision
activities. It does not generate recommendations (M7), decide whether revision
is required (M8), or execute corrective actions (governance/execution layer L).

Epistemic scope: functional, measurable execution metrics only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ScientificRevisionExecutionMonitor:
    """
    M9 — monitor scientific revision execution.

    Measures:
      - revision_execution_rate
      - revision_effectiveness
      - revision_success_rate

    Observes links between M7/M8 revision signals and governed execution traces.
    It remains non-executive and therefore preserves the governance boundary.
    """

    primitive = "scientific_revision_execution_monitor"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "scientific_revision_execution_monitor_report.json"
        self.history_path = self.report_dir / "scientific_revision_execution_monitor_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return []

    @staticmethod
    def _mean(values: list[float], default: float = 0.0) -> float:
        clean = [v for v in values if isinstance(v, (int, float))]
        return sum(clean) / len(clean) if clean else default

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _read_jsonl_tail(self, path: Path, limit: int = 200) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]
        except Exception:
            return []
        records: list[dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(item)
            except Exception:
                continue
        return records

    def _call_step(self, module_name: str, class_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            try:
                result = instance.step(payload, persist=False)
            except TypeError:
                try:
                    result = instance.step(payload)
                except TypeError:
                    result = instance.step()
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "upstream_error": f"{type(exc).__name__}: {exc}"}

    def _collect_sources(self, payload: dict[str, Any]) -> dict[str, Any]:
        sources: dict[str, Any] = {}

        aliases = {
            "self_revision_recommendation_engine": ["self_revision_recommendation_engine", "m7", "recommendation_report"],
            "scientific_self_revision_supervisor": ["scientific_self_revision_supervisor", "m8", "supervision_report"],
            "scientific_self_revision_controller": ["scientific_self_revision_controller", "revision_controller"],
            "execution_request_generation": ["execution_request_generation", "execution_requests"],
            "controlled_execution_layer": ["controlled_execution_layer", "controlled_execution"],
            "outcome_monitoring": ["outcome_monitoring", "outcomes"],
            "effectiveness_assessment": ["effectiveness_assessment", "effectiveness"],
            "adaptive_policy_update": ["adaptive_policy_update", "policy_update"],
        }
        for canonical, keys in aliases.items():
            for key in keys:
                value = payload.get(key)
                if isinstance(value, (dict, list)):
                    sources[canonical] = value
                    break

        if isinstance(payload.get("execution_records"), list):
            sources["execution_records"] = payload["execution_records"]
        if isinstance(payload.get("revision_events"), list):
            sources["revision_events"] = payload["revision_events"]

        if payload.get("use_reports", True):
            report_files = {
                "self_revision_recommendation_engine": self.report_dir / "self_revision_recommendation_engine_report.json",
                "scientific_self_revision_supervisor": self.report_dir / "scientific_self_revision_supervisor_report.json",
                "execution_request_generation": self.root / "governance" / "execution_request_generation" / "latest_execution_request_generation.json",
                "controlled_execution_layer": self.root / "governance" / "controlled_execution_layer" / "latest_controlled_execution_layer.json",
                "outcome_monitoring": self.root / "governance" / "outcome_monitoring" / "latest_outcome_monitoring.json",
                "effectiveness_assessment": self.root / "governance" / "effectiveness_assessment" / "latest_effectiveness_assessment.json",
                "adaptive_policy_update": self.root / "governance" / "adaptive_policy_update" / "latest_adaptive_policy_update.json",
            }
            for canonical, path in report_files.items():
                if canonical not in sources:
                    loaded = self._read_json(path)
                    if loaded:
                        sources[canonical] = loaded

        if payload.get("use_history", True):
            histories = {
                "m7_history": self.report_dir / "self_revision_recommendation_history.jsonl",
                "m8_history": self.report_dir / "scientific_self_revision_supervisor_history.jsonl",
                "execution_request_history": self.root / "governance" / "execution_request_generation" / "execution_request_generation_history.jsonl",
                "controlled_execution_history": self.root / "governance" / "controlled_execution_layer" / "controlled_execution_layer_history.jsonl",
                "outcome_monitoring_history": self.root / "governance" / "outcome_monitoring" / "outcome_monitoring_history.jsonl",
                "effectiveness_history": self.root / "governance" / "effectiveness_assessment" / "effectiveness_assessment_history.jsonl",
                "adaptive_policy_history": self.root / "governance" / "adaptive_policy_update" / "adaptive_policy_update_history.jsonl",
            }
            for key, path in histories.items():
                records = self._read_jsonl_tail(path)
                if records:
                    sources[key] = records

        if payload.get("use_upstream", False) is True:
            upstream_specs = {
                "self_revision_recommendation_engine": ("ontology.self_revision_recommendation_engine", "SelfRevisionRecommendationEngine"),
                "scientific_self_revision_supervisor": ("ontology.scientific_self_revision_supervisor", "ScientificSelfRevisionSupervisor"),
            }
            for canonical, (module_name, class_name) in upstream_specs.items():
                if canonical not in sources:
                    sources[canonical] = self._call_step(module_name, class_name, payload)

        return sources

    def _recommended_revision_count(self, sources: dict[str, Any]) -> int:
        count = 0
        m7 = self._as_dict(sources.get("self_revision_recommendation_engine"))
        recommendations = self._as_list(m7.get("scientific_revision_recommendations"))
        count += len(recommendations)

        for record in self._as_list(sources.get("m7_history")):
            recs = self._as_list(record.get("scientific_revision_recommendations"))
            count += len(recs)

        m8 = self._as_dict(sources.get("scientific_self_revision_supervisor"))
        if m8.get("self_revision_required") is True or m8.get("scientific_self_revision_decision") == "self_revision_required":
            count = max(count, 1)
        for record in self._as_list(sources.get("m8_history")):
            if record.get("self_revision_required") is True or record.get("scientific_self_revision_decision") == "self_revision_required":
                count += 1

        return count

    def _extract_execution_records(self, sources: dict[str, Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        for key in ("execution_records", "revision_events"):
            for item in self._as_list(sources.get(key)):
                if isinstance(item, dict):
                    records.append(item)

        for canonical in ("execution_request_generation", "controlled_execution_layer", "outcome_monitoring", "effectiveness_assessment", "adaptive_policy_update", "scientific_self_revision_controller"):
            item = sources.get(canonical)
            if isinstance(item, dict):
                records.append({"source": canonical, **item})
            elif isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        records.append({"source": canonical, **sub})

        for hist_key in ("execution_request_history", "controlled_execution_history", "outcome_monitoring_history", "effectiveness_history", "adaptive_policy_history"):
            for item in self._as_list(sources.get(hist_key)):
                if isinstance(item, dict):
                    records.append({"source": hist_key, **item})

        return records

    def _is_revision_related(self, record: dict[str, Any]) -> bool:
        text = json.dumps(record, sort_keys=True, default=str).lower()
        markers = [
            "scientific",
            "revision",
            "self_revision",
            "evidence",
            "robustness",
            "false_positive",
            "bias",
            "anomaly",
            "consistency",
            "m7",
            "m8",
        ]
        return any(marker in text for marker in markers)

    def _is_executed(self, record: dict[str, Any]) -> bool:
        status_values = []
        for key in ("execution_status", "status", "decision", "result", "controlled_execution_status"):
            value = record.get(key)
            if value is not None:
                status_values.append(str(value).lower())
        text = " ".join(status_values)
        positive = ["executed", "completed", "applied", "approved", "success", "accepted", "done"]
        negative = ["rejected", "blocked", "pending", "failed", "not_executed", "cancelled"]
        if any(n in text for n in negative):
            return False
        if any(p in text for p in positive):
            return True
        if record.get("success") is True:
            return True
        if record.get("execution_completed") is True:
            return True
        return False

    def _success_score(self, record: dict[str, Any]) -> float:
        candidates = [
            record.get("revision_success_rate"),
            record.get("success_rate"),
            record.get("execution_success_rate"),
            record.get("outcome_success_score"),
            record.get("effectiveness_score"),
            record.get("revision_effectiveness"),
            record.get("policy_update_effectiveness"),
        ]
        scores = [self._clamp(v, default=-1.0) for v in candidates if v is not None]
        scores = [s for s in scores if s >= 0.0]
        if scores:
            return self._mean(scores, default=0.0)
        if record.get("success") is True or self._is_executed(record):
            return 1.0
        if record.get("success") is False:
            return 0.0
        return 0.5

    def _effectiveness_score(self, record: dict[str, Any]) -> float:
        candidates = [
            record.get("revision_effectiveness"),
            record.get("effectiveness_score"),
            record.get("effectiveness"),
            record.get("measured_effectiveness"),
            record.get("outcome_improvement_score"),
            record.get("post_revision_improvement"),
            record.get("policy_update_effectiveness"),
        ]
        scores = [self._clamp(v, default=-1.0) for v in candidates if v is not None]
        scores = [s for s in scores if s >= 0.0]
        if scores:
            return self._mean(scores, default=0.0)
        return self._success_score(record)

    def _compute_metrics(self, payload: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
        explicit_records = self._as_list(payload.get("execution_records")) or self._as_list(payload.get("revision_events"))
        recommended = self._recommended_revision_count(sources)
        records = self._extract_execution_records(sources)
        revision_records = [r for r in records if self._is_revision_related(r)]

        # In explicit tests, do not let unrelated reports dilute the intended sample.
        if explicit_records:
            revision_records = [r for r in explicit_records if isinstance(r, dict)]
            recommended = max(recommended, len(revision_records))

        executed_records = [r for r in revision_records if self._is_executed(r)]
        denominator = max(recommended, len(revision_records), 1)
        revision_execution_rate = self._clamp(len(executed_records) / denominator)

        if revision_records:
            revision_success_rate = self._mean([self._success_score(r) for r in revision_records], default=0.0)
            revision_effectiveness = self._mean([self._effectiveness_score(r) for r in revision_records], default=0.0)
        else:
            revision_success_rate = 1.0 if recommended == 0 else 0.0
            revision_effectiveness = 1.0 if recommended == 0 else 0.0

        monitoring_confidence = self._clamp(self._mean([
            1.0 if "scientific_self_revision_supervisor" in sources else 0.0,
            1.0 if "self_revision_recommendation_engine" in sources else 0.0,
            1.0 if revision_records else 0.5,
        ], default=0.5))

        if recommended == 0 and not revision_records:
            decision = "no_revision_activity"
        elif revision_execution_rate < 0.40 or revision_success_rate < 0.40 or revision_effectiveness < 0.40:
            decision = "revision_execution_degraded"
        elif revision_execution_rate < 0.75 or revision_success_rate < 0.70 or revision_effectiveness < 0.70:
            decision = "revision_execution_watch"
        else:
            decision = "revision_execution_effective"

        return {
            "recommended_revision_count": recommended,
            "observed_revision_execution_count": len(revision_records),
            "executed_revision_count": len(executed_records),
            "revision_execution_rate": round(revision_execution_rate, 6),
            "revision_effectiveness": round(self._clamp(revision_effectiveness), 6),
            "revision_success_rate": round(self._clamp(revision_success_rate), 6),
            "execution_monitoring_confidence": round(monitoring_confidence, 6),
            "scientific_revision_execution_decision": decision,
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = dict(inputs or {})
        sources = self._collect_sources(payload)
        metrics = self._compute_metrics(payload, sources)

        source_signal_summary = {
            key: {
                "available": True,
                "type": type(value).__name__,
                "item_count": len(value) if isinstance(value, list) else None,
            }
            for key, value in sorted(sources.items())
        }

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": self._utc_now(),
            **metrics,
            "source_signal_summary": source_signal_summary,
            "governance_boundary": {
                "generates_recommendations": False,
                "decides_revision_required": False,
                "executes_revision": False,
                "observes_execution": True,
            },
            "report_path": str(self.report_path),
            "history_path": str(self.history_path),
        }

        if persist:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False) + "\n")

        return result
