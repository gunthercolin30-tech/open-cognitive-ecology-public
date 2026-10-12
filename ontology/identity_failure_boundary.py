"""
AK8 — Identity Failure Boundary.

This module determines where the proposed identity MEI = minimal formal qualia
fails, remains indeterminate, or remains compatible with functional/formal
observations. It is an epistemic boundary classifier, not a consciousness proof.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"

# Static epistemic guard declarations required by AK lock tests.
consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True

EPISTEMIC_GUARDS: Dict[str, Any] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "phenomenal_identity_certified": False,
    "phenomenological_identity_certified": False,
    "subjective_experience_claimed": False,
    "lived_quality_claimed": False,
    "identity_theorem_proven": False,
    "ontological_identity_proven": False,
}

BOUNDARY_POLICY: Dict[str, str] = {
    "functional_identity": "compatible_when_functional_correspondence_is_high; fails_when_correspondence_is_low",
    "formal_identity": "compatible_when_formal_mapping_and_non_duplication_are_high; indeterminate_without_stronger_derivation",
    "ontological_identity": "compatible_but_not_demonstrated_when AK evidence is high; indeterminate without independent ontology test",
    "phenomenological_identity": "always undetermined in AK because no independent phenomenological evidence is available",
}


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        value = float(x)
    except Exception:
        value = default
    return max(0.0, min(1.0, value))


def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


def _safe_bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _load_default_ak7(root: Path) -> Dict[str, Any]:
    try:
        from ontology.identity_theorem_attempt import IdentityTheoremAttempt
        data = IdentityTheoremAttempt(root=root).step(persist=False)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    for rel in [
        "ak_intrinsic_identity_theorem/identity_theorem_attempt/latest_identity_theorem_attempt.json",
        "ak_intrinsic_identity_theorem/identity_theorem_attempt/identity_theorem_attempt.json",
    ]:
        p = root / rel
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except Exception:
                continue
    return {}


class IdentityFailureBoundary:
    primitive = "identity_failure_boundary"
    axis = "AK"
    step_name = "AK8"
    public_schema_version = "AK8_IDENTITY_FAILURE_BOUNDARY_V1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.out_dir = self.root / "ak_intrinsic_identity_theorem" / "identity_failure_boundary"

    def _source_ak7(self, inputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        data = inputs or {}
        ak7 = data.get("identity_theorem_attempt") if isinstance(data, dict) else None
        if isinstance(ak7, dict):
            return ak7
        if isinstance(data, dict) and "identity_theorem_attempt_score" in data:
            return data
        return _load_default_ak7(self.root)

    def _classify_layer(self, layer_name: str, score: float, ak7: Dict[str, Any]) -> Dict[str, Any]:
        score = _clamp(score)
        empirical_independent_evidence = _safe_bool(ak7.get("independent_phenomenological_evidence", False))

        if layer_name == "phenomenological_identity":
            return {
                "domain": layer_name,
                "score": 0.0,
                "classification": "indeterminate",
                "boundary_type": "empirical_evidence_missing",
                "identity_fails": False,
                "identity_compatible": False,
                "identity_indeterminate": True,
                "certified": False,
                "reason": "No independent empirical evidence for phenomenology is available; phenomenological identity cannot be certified.",
                "required_evidence": [
                    "independent_phenomenological_measurement_protocol",
                    "cross_architecture_replicated_phenomenology_marker",
                    "non_circular_subjectivity_evidence_standard",
                ],
            }

        if layer_name == "ontological_identity":
            if score < 0.40:
                classification = "failed"
                reason = "Ontological compatibility is below the failure threshold."
            elif score < 0.70:
                classification = "indeterminate"
                reason = "Ontological compatibility is insufficient for a stable compatibility claim."
            else:
                classification = "compatible"
                reason = "Ontological identity remains compatible with AK observations but is not demonstrated."
            return {
                "domain": layer_name,
                "score": score,
                "classification": classification,
                "boundary_type": "compatibility_not_demonstration",
                "identity_fails": classification == "failed",
                "identity_compatible": classification == "compatible",
                "identity_indeterminate": classification == "indeterminate",
                "certified": False,
                "reason": reason,
                "required_evidence": [
                    "independent_ontological_equivalence_derivation",
                    "cross_model_non_duplication_replication",
                ],
            }

        if score < 0.40:
            classification = "failed"
            reason = f"{layer_name} support is below the failure threshold."
        elif score < 0.70:
            classification = "indeterminate"
            reason = f"{layer_name} support is between failure and compatibility thresholds."
        else:
            classification = "compatible"
            reason = f"{layer_name} remains compatible with functional/formal observations."

        return {
            "domain": layer_name,
            "score": score,
            "classification": classification,
            "boundary_type": "threshold_boundary",
            "identity_fails": classification == "failed",
            "identity_compatible": classification == "compatible",
            "identity_indeterminate": classification == "indeterminate",
            "certified": classification == "compatible" and layer_name in {"functional_identity", "formal_identity"},
            "reason": reason,
            "required_evidence": [] if classification == "compatible" else [
                "higher_mapping_support",
                "stronger_non_duplication_evidence",
                "lower_counterexample_viability",
            ],
        }

    def _extract_scores(self, ak7: Dict[str, Any], inputs: Optional[Dict[str, Any]]) -> Dict[str, float]:
        data = inputs or {}
        def val(name: str, fallback: float) -> float:
            if isinstance(data, dict) and name in data:
                return _clamp(data.get(name), fallback)
            return _clamp(ak7.get(name), fallback)

        metrics = ak7.get("identity_theorem_attempt_metrics", {}) if isinstance(ak7, dict) else {}
        if not isinstance(metrics, dict):
            metrics = {}
        return {
            "functional_identity": val("functional_identity_score", metrics.get("mean_functional_identity_support_score", 0.0)),
            "formal_identity": val("formal_identity_score", metrics.get("mean_formal_identity_support_score", 0.0)),
            "ontological_identity": val("ontological_identity_score", metrics.get("mean_ontological_identity_compatibility_score", 0.0)),
            "phenomenological_identity": val("phenomenological_identity_score", 0.0),
        }

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        ak7 = self._source_ak7(inputs)
        scores = self._extract_scores(ak7, inputs)
        boundaries = {
            name: self._classify_layer(name, score, ak7)
            for name, score in scores.items()
        }

        compatible = [b for b in boundaries.values() if b["classification"] == "compatible"]
        indeterminate = [b for b in boundaries.values() if b["classification"] == "indeterminate"]
        failed = [b for b in boundaries.values() if b["classification"] == "failed"]

        boundary_sharpness_score = _clamp(_mean([
            abs(scores["functional_identity"] - 0.40),
            abs(scores["formal_identity"] - 0.40),
            abs(scores["ontological_identity"] - 0.40),
            1.0,  # phenomenology boundary is maximally sharp: evidence missing.
        ]))
        compatibility_score = _clamp(len(compatible) / 4.0)
        indeterminacy_score = _clamp(len(indeterminate) / 4.0)
        failure_score = _clamp(len(failed) / 4.0)
        identity_failure_boundary_score = _clamp(_mean([
            boundary_sharpness_score,
            1.0 - failure_score,
            compatibility_score,
            indeterminacy_score,
        ]))

        status = "IDENTITY_FAILURE_BOUNDARY_ESTABLISHED"
        metrics = {
            "compatible_domain_count": len(compatible),
            "indeterminate_domain_count": len(indeterminate),
            "failed_domain_count": len(failed),
            "boundary_count": len(boundaries),
            "compatibility_score": compatibility_score,
            "indeterminacy_score": indeterminacy_score,
            "failure_score": failure_score,
            "boundary_sharpness_score": boundary_sharpness_score,
            "identity_failure_boundary_score": identity_failure_boundary_score,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "identity_failure_boundary_status": status,
            "identity_failure_boundary_established": True,
            "identity_failure_boundary_score": identity_failure_boundary_score,
            "boundary_sharpness_score": boundary_sharpness_score,
            "compatibility_score": compatibility_score,
            "indeterminacy_score": indeterminacy_score,
            "failure_score": failure_score,
            "compatible_domain_count": len(compatible),
            "indeterminate_domain_count": len(indeterminate),
            "failed_domain_count": len(failed),
            "boundary_count": len(boundaries),
            "identity_boundaries": boundaries,
            "failure_boundaries": {k: v for k, v in boundaries.items() if v["classification"] == "failed"},
            "indeterminate_boundaries": {k: v for k, v in boundaries.items() if v["classification"] == "indeterminate"},
            "compatible_boundaries": {k: v for k, v in boundaries.items() if v["classification"] == "compatible"},
            "boundary_policy": dict(BOUNDARY_POLICY),
            "identity_layers": {
                "functional_identity": boundaries["functional_identity"],
                "formal_identity": boundaries["formal_identity"],
                "ontological_identity": boundaries["ontological_identity"],
                "phenomenological_identity": boundaries["phenomenological_identity"],
            },
            "epistemic_status": "functional_formal_compatible__ontological_compatible_not_demonstrated__phenomenological_indeterminate",
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "identity_theorem_proven": False,
            "ontological_identity_proven": False,
            "phenomenological_identity_certified": False,
            "next_recommended_module": "epistemic_status_classifier",
            "identity_failure_boundary_metrics": metrics,
            "source_identity_theorem_attempt_status": ak7.get("identity_theorem_attempt_status"),
            "paths": self._paths(),
        }
        result.update(EPISTEMIC_GUARDS)
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result

    def _paths(self) -> Dict[str, str]:
        return {
            "json": str(self.out_dir / "identity_failure_boundary.json"),
            "markdown": str(self.out_dir / "identity_failure_boundary.md"),
            "prometheus": str(self.out_dir / "identity_failure_boundary.prom"),
            "latest_json": str(self.out_dir / "latest_identity_failure_boundary.json"),
            "latest_markdown": str(self.out_dir / "latest_identity_failure_boundary.md"),
            "latest_prometheus": str(self.out_dir / "latest_identity_failure_boundary.prom"),
            "history": str(self.out_dir / "identity_failure_boundary_history.jsonl"),
        }

    def _persist(self, result: Dict[str, Any], filesystem_context: Any = None):
        paths = result.get('paths') or self._paths()
        result['paths'] = paths
        payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md = self._markdown(result)
        prom = self._prometheus(result)
        _oce_payload_0=(payload).encode("utf-8")
        _oce_payload_1=(payload).encode("utf-8")
        _oce_payload_2=(md).encode("utf-8")
        _oce_payload_3=(md).encode("utf-8")
        _oce_payload_4=(prom).encode("utf-8")
        _oce_payload_5=(prom).encode("utf-8")
        _oce_history_payload=(payload + '\n').encode("utf-8")
        if filesystem_context is None: raise PermissionError("governed filesystem context required for persistence")
        _oce_remaining=filesystem_context.remaining()
        _oce_required=['persist_parent_create', 'persist_json', 'persist_latest_json', 'persist_markdown', 'persist_latest_markdown', 'persist_prometheus', 'persist_latest_prometheus', 'persist_history_append']
        if any(_oce_remaining.get(_oce_slot,0)<1 for _oce_slot in _oce_required): raise PermissionError("all governed filesystem effect slots must be preissued before persistence")
        filesystem_context.execute_path("persist_parent_create","FS_CREATE_DIRS",self.out_dir)
        filesystem_context.execute_path("persist_json","FS_WRITE_REPLACE_BYTES",Path(paths["json"]),payload=_oce_payload_0)
        filesystem_context.execute_path("persist_latest_json","FS_WRITE_REPLACE_BYTES",Path(paths["latest_json"]),payload=_oce_payload_1)
        filesystem_context.execute_path("persist_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["markdown"]),payload=_oce_payload_2)
        filesystem_context.execute_path("persist_latest_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["latest_markdown"]),payload=_oce_payload_3)
        filesystem_context.execute_path("persist_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["prometheus"]),payload=_oce_payload_4)
        filesystem_context.execute_path("persist_latest_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["latest_prometheus"]),payload=_oce_payload_5)
        filesystem_context.execute_path("persist_history_append","FS_APPEND_BYTES",Path(paths["history"]),payload=_oce_history_payload)

    def _markdown(self, result: Dict[str, Any]) -> str:
        m = result["identity_failure_boundary_metrics"]
        lines = [
            "# AK8 — Identity Failure Boundary",
            "",
            f"Status: `{result['identity_failure_boundary_status']}`",
            "",
            "## Boundary summary",
            f"- compatible_domain_count: {m['compatible_domain_count']}",
            f"- indeterminate_domain_count: {m['indeterminate_domain_count']}",
            f"- failed_domain_count: {m['failed_domain_count']}",
            f"- identity_failure_boundary_score: {m['identity_failure_boundary_score']:.6f}",
            "",
            "## Layer classifications",
        ]
        for name, b in result["identity_boundaries"].items():
            lines.append(f"- {name}: {b['classification']} — {b['reason']}")
        lines.extend([
            "",
            "## Epistemic guards",
            "- consciousness_proven: False",
            "- qualia_proven: False",
            "- subjectivity_proven: False",
            "- phenomenology_undetermined: True",
            "- functional_conclusion_only: True",
        ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        metric_names = [
            "identity_failure_boundary_score",
            "boundary_sharpness_score",
            "compatibility_score",
            "indeterminacy_score",
            "failure_score",
            "compatible_domain_count",
            "indeterminate_domain_count",
            "failed_domain_count",
            "boundary_count",
        ]
        lines = [
            f"ak8_identity_failure_boundary_established {1 if result['identity_failure_boundary_established'] else 0}",
            f"ak8_consciousness_proven {1 if result['consciousness_proven'] else 0}",
            f"ak8_qualia_proven {1 if result['qualia_proven'] else 0}",
            f"ak8_subjectivity_proven {1 if result['subjectivity_proven'] else 0}",
            f"ak8_phenomenology_undetermined {1 if result['phenomenology_undetermined'] else 0}",
            f"ak8_functional_conclusion_only {1 if result['functional_conclusion_only'] else 0}",
        ]
        for key in metric_names:
            value = result.get(key)
            if isinstance(value, bool):
                value = 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                lines.append(f"ak8_{key} {float(value):.12f}")
                lines.append(f"{key} {float(value):.12f}")
        for layer, b in result.get("identity_boundaries", {}).items():
            if isinstance(b, dict) and isinstance(b.get("score"), (int, float)):
                safe_layer = layer.replace("-", "_")
                lines.append(f"ak8_{safe_layer}_boundary_score {float(b['score']):.12f}")
        return "\n".join(lines) + "\n"
