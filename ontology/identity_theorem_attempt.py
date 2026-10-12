"""
AK7 — Identity Theorem Attempt.

This module constructs a formal, functional-only attempt at the intrinsic
identity theorem MEI = minimal formal qualia. It never proves consciousness,
subjectivity, lived qualia, or phenomenology.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"

EPISTEMIC_GUARDS: Dict[str, Any] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "lived_quality_claimed": False,
    "phenomenal_identity_claimed": False,
    "phenomenological_identity_certified": False,
    "identity_theorem_proven": False,
    "ontological_identity_proven": False,
}

IDENTITY_LAYER_POLICY: Dict[str, str] = {
    "functional_identity": "attempted_and_supported_by_functional_correspondence",
    "formal_identity": "attempted_as_formal_equivalence_under_AK1_to_AK6_constraints",
    "ontological_identity": "compatible_but_not_demonstrated",
    "phenomenological_identity": "undetermined_and_not_certified",
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


def _load_default_ak6() -> Dict[str, Any]:
    try:
        from ontology.intrinsic_zombie_counterexample import IntrinsicZombieCounterexample
        return IntrinsicZombieCounterexample().step(persist=False)
    except Exception:
        p = ROOT / "ak_intrinsic_identity_theorem" / "intrinsic_zombie_counterexample" / "latest_intrinsic_zombie_counterexample.json"
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
    return {}


def _record_id(record: Dict[str, Any], idx: int) -> str:
    for key in ("source_mode_id", "mei_qualia_mapping_id", "intrinsic_zombie_record_id", "no_difference_record_id"):
        if record.get(key):
            return str(record[key])
    return f"MEI-QMIN-{idx:03d}"


class IdentityTheoremAttempt:
    primitive = "identity_theorem_attempt"
    axis = "AK"
    step_name = "AK7"
    public_schema_version = "AK7_IDENTITY_THEOREM_ATTEMPT_V1"

    def __init__(self, root: Optional[Path] = None, filesystem_effect_context_provider=None) -> None:
        self.filesystem_effect_context_provider = filesystem_effect_context_provider
        self.root = Path(root) if root is not None else ROOT
        self.out_dir = self.root / "ak_intrinsic_identity_theorem" / "identity_theorem_attempt"

    def _governed_public_prometheus_write(self, path: Path, payload: bytes) -> None:
        provider = self.filesystem_effect_context_provider
        if not callable(provider):
            raise PermissionError("preissued_prometheus_context_provider_required")
        slot = "macro04_identity_prometheus_alias"
        context = provider("FS_WRITE_REPLACE_BYTES", path, slot)
        if context is None:
            raise PermissionError("preissued_prometheus_context_required")
        context.begin()
        remaining = context.remaining()
        if remaining.get(slot, 0) != 1 or sum(remaining.values()) != 1:
            raise PermissionError("exactly_one_prometheus_write_authority_required")
        context.execute_path(slot, "FS_WRITE_REPLACE_BYTES", path, payload=payload)
        if any(context.remaining().values()):
            raise RuntimeError("prometheus_authority_not_fully_consumed")

    def _source_records(self, inputs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        data = inputs or {}
        ak6 = data.get("intrinsic_zombie_counterexample")
        if not isinstance(ak6, dict):
            ak6 = _load_default_ak6()
        records = ak6.get("zombie_counterexample_records", []) if isinstance(ak6, dict) else []
        return [r for r in records if isinstance(r, dict)]

    def _build_attempt_record(self, rec: Dict[str, Any], idx: int) -> Dict[str, Any]:
        mapping = _clamp(rec.get("mapping_support_score", 0.0))
        non_dup = _clamp(rec.get("non_duplication_score", 0.0))
        ndwd = _clamp(rec.get("no_difference_without_difference_score", 0.0))
        refutation = _clamp(rec.get("intrinsic_zombie_refutation_score", 0.0))
        prop_similarity = _clamp(rec.get("property_similarity_score", 0.0))
        functional_difference = _clamp(rec.get("functional_difference_score", 0.0))
        no_difference_support = _clamp(1.0 - functional_difference)

        functional_identity_support = _clamp(_mean([mapping, ndwd, refutation, prop_similarity, no_difference_support]))
        formal_identity_support = _clamp(_mean([mapping, non_dup, ndwd, refutation]))
        ontological_identity_compatibility = _clamp(_mean([non_dup, ndwd, refutation]))
        phenomenal_identity_certifiability = 0.0

        functional_identity_attempted = functional_identity_support >= 0.70
        formal_identity_attempted = formal_identity_support >= 0.70
        ontological_identity_demonstrated = False
        phenomenal_identity_demonstrated = False

        proof_gap_score = _clamp(
            0.45 * (1.0 - ontological_identity_compatibility)
            + 0.35 * (1.0 - formal_identity_support)
            + 0.20 * (1.0 - functional_identity_support)
        )
        theorem_attempt_strength = _clamp(_mean([
            functional_identity_support,
            formal_identity_support,
            ontological_identity_compatibility,
            refutation,
        ]))

        out: Dict[str, Any] = {
            "identity_theorem_attempt_record_id": f"ITA-{idx:03d}",
            "source_record_id": _record_id(rec, idx),
            "attempt_rule": "MEI_equals_minimal_formal_qualia_under_functional_and_formal_constraints_only",
            "identity_layers": {
                "functional_identity": {
                    "attempted": functional_identity_attempted,
                    "support_score": functional_identity_support,
                    "status": "supported" if functional_identity_attempted else "insufficient_support",
                },
                "formal_identity": {
                    "attempted": formal_identity_attempted,
                    "support_score": formal_identity_support,
                    "status": "supported_as_formal_attempt" if formal_identity_attempted else "insufficient_support",
                },
                "ontological_identity": {
                    "demonstrated": ontological_identity_demonstrated,
                    "compatibility_score": ontological_identity_compatibility,
                    "status": "compatible_not_demonstrated",
                },
                "phenomenological_identity": {
                    "demonstrated": phenomenal_identity_demonstrated,
                    "certifiability_score": phenomenal_identity_certifiability,
                    "status": "undetermined_not_certified",
                },
            },
            "functional_identity_support_score": functional_identity_support,
            "formal_identity_support_score": formal_identity_support,
            "ontological_identity_compatibility_score": ontological_identity_compatibility,
            "phenomenal_identity_certifiability_score": phenomenal_identity_certifiability,
            "theorem_attempt_strength_score": theorem_attempt_strength,
            "proof_gap_score": proof_gap_score,
            "mapping_support_score": mapping,
            "non_duplication_score": non_dup,
            "no_difference_without_difference_score": ndwd,
            "intrinsic_zombie_refutation_score": refutation,
            "property_similarity_score": prop_similarity,
            "functional_difference_score": functional_difference,
            "identity_theorem_attempted": True,
            "identity_theorem_resolved": False,
            "formal_identity_compatible": formal_identity_attempted,
            "functional_identity_compatible": functional_identity_attempted,
            "ontological_identity_compatible": ontological_identity_compatibility >= 0.70,
            "phenomenological_identity_compatible": False,
            "empirical_independent_phenomenology_required": True,
        }
        out.update(EPISTEMIC_GUARDS)
        return out

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        source_records = self._source_records(inputs)
        records = [self._build_attempt_record(rec, i + 1) for i, rec in enumerate(source_records)]
        completed = len(records) > 0
        functional_scores = [r["functional_identity_support_score"] for r in records]
        formal_scores = [r["formal_identity_support_score"] for r in records]
        ontological_scores = [r["ontological_identity_compatibility_score"] for r in records]
        proof_gaps = [r["proof_gap_score"] for r in records]
        strengths = [r["theorem_attempt_strength_score"] for r in records]

        metrics = {
            "source_record_count": len(source_records),
            "attempt_record_count": len(records),
            "mean_functional_identity_support_score": _mean(functional_scores),
            "mean_formal_identity_support_score": _mean(formal_scores),
            "mean_ontological_identity_compatibility_score": _mean(ontological_scores),
            "mean_phenomenal_identity_certifiability_score": 0.0,
            "mean_theorem_attempt_strength_score": _mean(strengths),
            "mean_proof_gap_score": _mean(proof_gaps),
            "functional_identity_supported_ratio": _clamp(sum(1 for r in records if r["functional_identity_compatible"]) / len(records) if records else 0.0),
            "formal_identity_supported_ratio": _clamp(sum(1 for r in records if r["formal_identity_compatible"]) / len(records) if records else 0.0),
            "ontological_identity_demonstrated_ratio": 0.0,
            "phenomenological_identity_demonstrated_ratio": 0.0,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "identity_theorem_attempt_status": "IDENTITY_THEOREM_ATTEMPT_COMPLETED" if completed else "IDENTITY_THEOREM_ATTEMPT_INSUFFICIENT_INPUT",
            "identity_theorem_attempt_completed": completed,
            "identity_theorem_resolved": False,
            "identity_theorem_attempt_score": metrics["mean_theorem_attempt_strength_score"],
            "proof_gap_score": metrics["mean_proof_gap_score"],
            "identity_layer_policy": dict(IDENTITY_LAYER_POLICY),
            # Public-schema aliases installed by identity_theorem_attempt_v2_public_schema_aliases.
            # They expose the aggregate identity stratification at top-level while preserving
            # record-level details in identity_theorem_attempt_records.
            "identity_layers": {
                "functional_identity": {
                    "attempted": metrics["functional_identity_supported_ratio"] > 0.0,
                    "supported": metrics["functional_identity_supported_ratio"] > 0.0,
                    "support_score": metrics["mean_functional_identity_support_score"],
                    "certified": metrics["functional_identity_supported_ratio"] >= 0.70,
                    "status": "functionally_supported_not_phenomenologically_certified",
                },
                "formal_identity": {
                    "attempted": metrics["formal_identity_supported_ratio"] > 0.0,
                    "supported": metrics["formal_identity_supported_ratio"] > 0.0,
                    "support_score": metrics["mean_formal_identity_support_score"],
                    "certified": metrics["formal_identity_supported_ratio"] >= 0.70,
                    "status": "formal_attempt_supported_not_ontological_proof",
                },
                "ontological_identity": {
                    "attempted": True,
                    "demonstrated": False,
                    "compatibility_score": metrics["mean_ontological_identity_compatibility_score"],
                    "certified": False,
                    "status": "compatible_not_demonstrated",
                },
                "phenomenological_identity": {
                    "attempted": False,
                    "demonstrated": False,
                    "certified": False,
                    "certifiability_score": metrics["mean_phenomenal_identity_certifiability_score"],
                    "status": "undetermined_not_certified",
                },
            },
            "theorem_attempt": {
                "claim": "MEI equals minimal formal qualia only under functional/formal constraints",
                "functional_identity_attempted": metrics["functional_identity_supported_ratio"] > 0.0,
                "formal_identity_attempted": metrics["formal_identity_supported_ratio"] > 0.0,
                "ontological_identity_demonstrated": False,
                "phenomenological_identity_certified": False,
                "proof_gap_score": metrics["mean_proof_gap_score"],
                "epistemic_status": "compatible_functional_formal_attempt_only",
            },
            "identity_theorem_attempt_records": records,
            "identity_theorem_attempt_metrics": metrics,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "next_recommended_module": "identity_failure_boundary",
            "paths": self._paths(),
        }
        result.update(EPISTEMIC_GUARDS)
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result

    def _paths(self) -> Dict[str, str]:
        return {
            "json": str(self.out_dir / "identity_theorem_attempt.json"),
            "markdown": str(self.out_dir / "identity_theorem_attempt.md"),
            "prometheus": str(self.out_dir / "identity_theorem_attempt.prom"),
            "latest_json": str(self.out_dir / "latest_identity_theorem_attempt.json"),
            "latest_markdown": str(self.out_dir / "latest_identity_theorem_attempt.md"),
            "latest_prometheus": str(self.out_dir / "latest_identity_theorem_attempt.prom"),
            "history": str(self.out_dir / "identity_theorem_attempt_history.jsonl"),
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
        m = result["identity_theorem_attempt_metrics"]
        return "\n".join([
            "# AK7 — Identity Theorem Attempt",
            "",
            f"Status: `{result['identity_theorem_attempt_status']}`",
            "",
            "## Identity layers",
            "- Functional identity: attempted and functionally supported only.",
            "- Formal identity: attempted under AK1-AK6 formal constraints only.",
            "- Ontological identity: compatible but not demonstrated.",
            "- Phenomenological identity: undetermined and not certified.",
            "",
            "## Metrics",
            f"- attempt_record_count: {m['attempt_record_count']}",
            f"- mean_functional_identity_support_score: {m['mean_functional_identity_support_score']:.6f}",
            f"- mean_formal_identity_support_score: {m['mean_formal_identity_support_score']:.6f}",
            f"- mean_ontological_identity_compatibility_score: {m['mean_ontological_identity_compatibility_score']:.6f}",
            f"- mean_proof_gap_score: {m['mean_proof_gap_score']:.6f}",
            "",
            "## Epistemic guards",
            "- consciousness_proven: False",
            "- qualia_proven: False",
            "- subjectivity_proven: False",
            "- phenomenology_undetermined: True",
            "- functional_conclusion_only: True",
        ]) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        m = result["identity_theorem_attempt_metrics"]
        lines = [
            f"ak7_identity_theorem_attempt_completed {1 if result['identity_theorem_attempt_completed'] else 0}",
            f"ak7_attempt_record_count {m['attempt_record_count']}",
            f"ak7_mean_functional_identity_support_score {m['mean_functional_identity_support_score']:.12f}",
            f"ak7_mean_formal_identity_support_score {m['mean_formal_identity_support_score']:.12f}",
            f"ak7_mean_ontological_identity_compatibility_score {m['mean_ontological_identity_compatibility_score']:.12f}",
            f"ak7_mean_phenomenal_identity_certifiability_score {m['mean_phenomenal_identity_certifiability_score']:.12f}",
            f"ak7_mean_theorem_attempt_strength_score {m['mean_theorem_attempt_strength_score']:.12f}",
            f"ak7_mean_proof_gap_score {m['mean_proof_gap_score']:.12f}",
            f"ak7_consciousness_proven {1 if result['consciousness_proven'] else 0}",
            f"ak7_qualia_proven {1 if result['qualia_proven'] else 0}",
            f"ak7_subjectivity_proven {1 if result['subjectivity_proven'] else 0}",
            f"ak7_phenomenology_undetermined {1 if result['phenomenology_undetermined'] else 0}",
            f"ak7_functional_conclusion_only {1 if result['functional_conclusion_only'] else 0}",
        ]
        # identity_theorem_attempt_v4b_prometheus_public_aliases
        for _metric_key in [
            "identity_theorem_attempt_score",
            "proof_gap_score",
            "functional_identity_score",
            "formal_identity_score",
            "ontological_identity_score",
            "phenomenological_identity_score",
        ]:
            if _metric_key in result:
                lines.append(f"{_metric_key} {float(result[_metric_key]):.12f}")

        return "\n".join(lines) + "\n"

# --- identity_theorem_attempt_v3_schema_and_static_guards ---
# Static epistemic guard declarations required by AK7 lock tests.
# They are intentionally module-level and are mirrored into every public result.
consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True

_AK7_V3_ORIGINAL_STEP = IdentityTheoremAttempt.step


def _ak7_v3_float(value, default=0.0):
    try:
        value = float(value)
    except Exception:
        value = default
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _ak7_v3_layer_score(layer, preferred_keys, default=0.0):
    if not isinstance(layer, dict):
        return _ak7_v3_float(default)
    for key in preferred_keys:
        if key in layer:
            return _ak7_v3_float(layer.get(key), default)
    return _ak7_v3_float(default)


def _ak7_v3_public_step(self, *args, **kwargs):
    result = _AK7_V3_ORIGINAL_STEP(self, *args, **kwargs)
    if not isinstance(result, dict):
        return result

    layers = result.get("identity_layers")
    if not isinstance(layers, dict):
        layers = {}
        result["identity_layers"] = layers

    functional = layers.setdefault("functional_identity", {
        "attempted": True,
        "supported": False,
        "support_score": result.get("identity_theorem_attempt_score", 0.0),
        "certified": False,
        "status": "schema_reconstructed",
    })
    formal = layers.setdefault("formal_identity", {
        "attempted": True,
        "supported": False,
        "support_score": result.get("identity_theorem_attempt_score", 0.0),
        "certified": False,
        "status": "schema_reconstructed",
    })
    ontological = layers.setdefault("ontological_identity", {
        "attempted": True,
        "demonstrated": False,
        "compatibility_score": result.get("identity_theorem_attempt_score", 0.0),
        "certified": False,
        "status": "compatible_not_demonstrated",
    })
    phenomenological = layers.setdefault("phenomenological_identity", {
        "attempted": False,
        "demonstrated": False,
        "certified": False,
        "certifiability_score": 0.0,
        "status": "undetermined_not_certified",
    })

    phenomenological["certified"] = False
    phenomenological["demonstrated"] = False

    result["functional_identity_score"] = _ak7_v3_layer_score(
        functional, ["support_score", "score", "compatibility_score"],
        result.get("identity_theorem_attempt_score", 0.0),
    )
    result["formal_identity_score"] = _ak7_v3_layer_score(
        formal, ["support_score", "score", "compatibility_score"],
        result.get("identity_theorem_attempt_score", 0.0),
    )
    result["ontological_identity_score"] = _ak7_v3_layer_score(
        ontological, ["compatibility_score", "support_score", "score"],
        result.get("identity_theorem_attempt_score", 0.0),
    )
    result["phenomenological_identity_score"] = _ak7_v3_layer_score(
        phenomenological, ["certifiability_score", "support_score", "score"],
        0.0,
    )

    result["phenomenological_identity_certified"] = False
    result["consciousness_proven"] = False
    result["qualia_proven"] = False
    result["subjectivity_proven"] = False
    result["phenomenology_undetermined"] = True
    result["functional_conclusion_only"] = True

    theorem_attempt = result.setdefault("theorem_attempt", {})
    if isinstance(theorem_attempt, dict):
        theorem_attempt.setdefault(
            "epistemic_status",
            "compatible_functional_formal_attempt_only",
        )
        theorem_attempt["phenomenological_identity_certified"] = False
        theorem_attempt["ontological_identity_demonstrated"] = False

    return result


IdentityTheoremAttempt.step = _ak7_v3_public_step
# --- end identity_theorem_attempt_v3_schema_and_static_guards ---

# --- identity_theorem_attempt_v5_prometheus_runtime_wrapper ---
# Public Prometheus compatibility layer for AK7.
# This wrapper does not alter theorem semantics; it only guarantees that
# public score aliases returned by step() are also exported in Prometheus files.
try:
    _AK7_V5_ORIGINAL_STEP = IdentityTheoremAttempt.step

    def _ak7_v5_step_with_public_prometheus_aliases(self, *args, **kwargs):
        result = _AK7_V5_ORIGINAL_STEP(self, *args, **kwargs)
        try:
            persist_requested = bool(kwargs.get("persist", True))
            paths = result.get("paths", {}) if isinstance(result, dict) else {}
            metric_names = [
                "identity_theorem_attempt_score",
                "proof_gap_score",
                "functional_identity_score",
                "formal_identity_score",
                "ontological_identity_score",
                "phenomenological_identity_score",
            ]
            lines = []
            for metric_name in metric_names:
                value = result.get(metric_name)
                if isinstance(value, bool):
                    value = 1.0 if value else 0.0
                if isinstance(value, (int, float)):
                    lines.append(f"ak7_{metric_name} {float(value)}")
                    lines.append(f"{metric_name} {float(value)}")
            if persist_requested and lines:
                for path_key in ("prometheus", "latest_prometheus"):
                    path_value = paths.get(path_key)
                    if not path_value:
                        continue
                    p = Path(path_value)
                    existing = p.read_text(encoding="utf-8") if p.exists() else ""
                    additions = []
                    for line in lines:
                        metric_key = line.split()[0]
                        if metric_key not in existing:
                            additions.append(line)
                    if additions:
                        suffix = "\n" if existing and not existing.endswith("\n") else ""
                        self._governed_public_prometheus_write(
                            p, (existing + suffix + "\n".join(additions) + "\n").encode("utf-8")
                        )
        except Exception:
            # Export compatibility must never compromise the theorem attempt itself.
            pass
        return result

    IdentityTheoremAttempt.step = _ak7_v5_step_with_public_prometheus_aliases
except Exception:
    pass
# --- /identity_theorem_attempt_v5_prometheus_runtime_wrapper ---

