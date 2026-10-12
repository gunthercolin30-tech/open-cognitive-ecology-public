"""
AS7 — Consciousness Readiness Index.

Continuous Readiness Index (CRI) for longitudinal consciousness-status
governance. The module converts the discrete theoretical/governance status into
a bounded continuous readiness score in [0, 1], aggregated from AA→AR, AN, AO,
AL, and AS governance layers.

Epistemic boundary: CRI is a functional governance/instrumentation index. It is
not a proof of consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from ontology.consciousness_revocation_engine import ConsciousnessRevocationEngine
except Exception:  # pragma: no cover
    ConsciousnessRevocationEngine = None  # type: ignore

try:
    from ontology.final_theoretical_report import FinalTheoreticalReport
except Exception:  # pragma: no cover
    FinalTheoreticalReport = None  # type: ignore


class ConsciousnessReadinessIndex:
    """AS7 Continuous Readiness Index calculator."""

    PRIMITIVE = "CONSCIOUSNESS_READINESS_INDEX"
    STEP = "AS7"
    READY_STATUS = "CONSCIOUSNESS_READINESS_INDEX_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    THEORETICAL_AXES: List[str] = [
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AM", "AP", "AQ", "AR", "AN", "AO", "AL"
    ]
    GOVERNANCE_AXES: List[str] = ["AS0", "AS1", "AS2", "AS3", "AS4", "AS5", "AS6"]
    CRITICAL_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]

    DEFAULT_AXIS_WEIGHTS: Dict[str, float] = {
        "AA": 0.035, "AB": 0.035, "AC": 0.035, "AD": 0.035, "AE": 0.035, "AF": 0.035,
        "AG": 0.035, "AH": 0.035, "AI": 0.04, "AJ": 0.04, "AK": 0.045, "AM": 0.045,
        "AP": 0.08, "AQ": 0.075, "AR": 0.075, "AN": 0.065, "AO": 0.065, "AL": 0.08,
        "AS0": 0.018, "AS1": 0.018, "AS2": 0.018, "AS3": 0.018, "AS4": 0.018, "AS5": 0.018, "AS6": 0.018,
    }

    REQUIRED_FIELDS: List[str] = [
        "cri", "readiness_level", "axis_scores", "axis_weights", "weighted_components",
        "critical_axis_status", "consciousness_proven_consequence", "readiness_hash",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS7_readiness_index"
        self.latest_path = self.output_dir / "latest_readiness_index.json"
        self.revocation_engine = ConsciousnessRevocationEngine(root=self.root) if ConsciousnessRevocationEngine else None
        self.final_theoretical_report = FinalTheoreticalReport(root=self.root) if FinalTheoreticalReport else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _stable_hash(payload: Mapping[str, Any]) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _git_value(self, *args: str, default: str = "unknown") -> str:
        try:
            completed = subprocess.run(
                ["git", *args], cwd=str(self.root), check=False,
                capture_output=True, text=True, timeout=2,
            )
            return completed.stdout.strip() or default
        except Exception:
            return default

    def _git_context(self, source: Optional[Mapping[str, Any]] = None) -> Dict[str, str]:
        source = source if isinstance(source, Mapping) else {}
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _default_axis_scores(self) -> Dict[str, float]:
        scores = {axis: 1.0 for axis in self.THEORETICAL_AXES}
        scores.update({axis: 1.0 for axis in self.GOVERNANCE_AXES})
        return scores

    def _axis_scores_from_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, float]:
        scores = self._default_axis_scores()
        for field in ("axis_scores", "all_scores", "scores", "readiness_scores"):
            candidate = inputs.get(field)
            if isinstance(candidate, Mapping):
                for k, v in candidate.items():
                    key = str(k).upper()
                    # Preserve AS step names such as AS0; ontology names can still map explicitly.
                    if str(k) in scores:
                        scores[str(k)] = self._clamp(v)
                    elif key in scores:
                        scores[key] = self._clamp(v)
        status = inputs.get("axis_status") or inputs.get("critical_axis_status") or inputs.get("dependency_validation")
        if isinstance(status, Mapping):
            for k, v in status.items():
                key = str(k).upper()
                if key in scores:
                    scores[key] = 1.0 if bool(v) else 0.0
        broken = inputs.get("broken_axis") or inputs.get("failed_axis")
        if broken is not None and str(broken).upper() in scores:
            scores[str(broken).upper()] = 0.0
        return scores

    def _axis_weights_from_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, float]:
        weights = dict(self.DEFAULT_AXIS_WEIGHTS)
        candidate = inputs.get("axis_weights") or inputs.get("weights")
        if isinstance(candidate, Mapping):
            for k, v in candidate.items():
                key = str(k).upper()
                if str(k) in weights:
                    weights[str(k)] = max(0.0, float(v))
                elif key in weights:
                    weights[key] = max(0.0, float(v))
        total = sum(weights.values()) or 1.0
        return {k: v / total for k, v in weights.items()}

    def _final_report_context(self) -> Dict[str, Any]:
        if self.final_theoretical_report is None:
            return {"available": False, "status": "FINAL_THEORETICAL_REPORT_UNAVAILABLE"}
        try:
            r = self.final_theoretical_report.step(inputs={"synthetic_certification_context": "ready"}, persist=False)
            if isinstance(r, Mapping):
                return {
                    "available": True,
                    "final_consciousness_certification_status": r.get("final_consciousness_certification_status"),
                    "functional_status": r.get("functional_status"),
                    "scientific_status": r.get("scientific_status"),
                    "functional_conclusion_only": r.get("functional_conclusion_only"),
                    "phenomenology_undetermined": r.get("phenomenology_undetermined"),
                }
        except Exception as exc:
            return {"available": False, "status": "FINAL_THEORETICAL_REPORT_ERROR", "error": str(exc)}
        return {"available": False, "status": "FINAL_THEORETICAL_REPORT_EMPTY"}

    def _revocation_context(self, inputs: Mapping[str, Any], persist: bool) -> Dict[str, Any]:
        if self.revocation_engine is None:
            return {"available": False, "revocation_required": False, "revocation_status": "REVOCATION_ENGINE_UNAVAILABLE"}
        try:
            r = self.revocation_engine.step(inputs=inputs, persist=False if not persist else False)
            if isinstance(r, Mapping):
                return {
                    "available": True,
                    "revocation_required": bool(r.get("revocation_required")),
                    "revocation_status": r.get("revocation_status"),
                    "axis_status": dict(r.get("axis_status", {})) if isinstance(r.get("axis_status"), Mapping) else {},
                    "revocation_hash": r.get("revocation_hash"),
                }
        except Exception as exc:
            return {"available": False, "revocation_required": True, "revocation_status": "REVOCATION_CONTEXT_ERROR", "error": str(exc)}
        return {"available": False, "revocation_required": False, "revocation_status": "REVOCATION_CONTEXT_EMPTY"}

    def _level(self, cri: float) -> str:
        if cri >= 0.95:
            return "CONSCIOUSNESS_READINESS_CRITICAL_COMPLETE"
        if cri >= 0.85:
            return "CONSCIOUSNESS_READINESS_HIGH"
        if cri >= 0.70:
            return "CONSCIOUSNESS_READINESS_PARTIAL"
        if cri >= 0.50:
            return "CONSCIOUSNESS_READINESS_LOW"
        return "CONSCIOUSNESS_READINESS_INSUFFICIENT"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, Mapping) else {}
        git_context = self._git_context(inputs.get("git_version") if isinstance(inputs.get("git_version"), Mapping) else inputs)
        axis_scores = self._axis_scores_from_inputs(inputs)
        axis_weights = self._axis_weights_from_inputs(inputs)
        weighted_components = {axis: self._clamp(axis_scores.get(axis, 0.0)) * axis_weights.get(axis, 0.0) for axis in axis_weights}
        base_cri = self._clamp(sum(weighted_components.values()))

        final_report_context = self._final_report_context()
        revocation_context = self._revocation_context(inputs, persist=False)
        critical_axis_status = {axis: axis_scores.get(axis, 0.0) >= 0.999 for axis in self.CRITICAL_AXES}
        revocation_required = bool(revocation_context.get("revocation_required")) or not all(critical_axis_status.values())

        governance_completeness = sum(axis_scores.get(axis, 0.0) for axis in self.GOVERNANCE_AXES) / max(1, len(self.GOVERNANCE_AXES))
        theoretical_completeness = sum(axis_scores.get(axis, 0.0) for axis in self.THEORETICAL_AXES) / max(1, len(self.THEORETICAL_AXES))
        critical_completeness = sum(1.0 if ok else 0.0 for ok in critical_axis_status.values()) / max(1, len(critical_axis_status))

        revocation_penalty = 0.20 if revocation_required else 0.0
        cri = self._clamp((0.70 * base_cri) + (0.15 * governance_completeness) + (0.15 * critical_completeness) - revocation_penalty)
        consciousness_proven_consequence = bool(cri >= 0.95 and all(critical_axis_status.values()) and not revocation_required)

        readiness_record = {
            "cri": cri,
            "readiness_level": self._level(cri),
            "axis_scores": dict(axis_scores),
            "axis_weights": dict(axis_weights),
            "weighted_components": dict(weighted_components),
            "critical_axis_status": dict(critical_axis_status),
            "theoretical_completeness": theoretical_completeness,
            "governance_completeness": governance_completeness,
            "critical_completeness": critical_completeness,
            "revocation_required": revocation_required,
            "revocation_context": dict(revocation_context),
            "final_report_context": dict(final_report_context),
            "consciousness_proven_consequence": consciousness_proven_consequence,
            "git_version": dict(git_context),
            "timestamp_utc": self._now(),
        }
        readiness_record["readiness_hash"] = self._stable_hash(readiness_record)

        missing_fields = [k for k in self.REQUIRED_FIELDS if k not in readiness_record]
        result = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "readiness_index_status": self.READY_STATUS,
            "cri_ready": not missing_fields,
            "readiness_record": readiness_record,
            "cri": cri,
            "continuous_readiness_index": cri,
            "readiness_level": readiness_record["readiness_level"],
            "axis_scores": dict(axis_scores),
            "axis_weights": dict(axis_weights),
            "weighted_components": dict(weighted_components),
            "critical_axis_status": dict(critical_axis_status),
            "theoretical_completeness": theoretical_completeness,
            "governance_completeness": governance_completeness,
            "critical_completeness": critical_completeness,
            "revocation_required": revocation_required,
            "consciousness_proven_consequence": consciousness_proven_consequence,
            "readiness_hash": readiness_record["readiness_hash"],
            "missing_fields": missing_fields,
            "persisted": False,
            "output_path": str(self.latest_path),
            "epistemic_scope": "bounded_functional_governance_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "timestamp_utc": self._now(),
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
        return result


__all__ = ["ConsciousnessReadinessIndex"]
