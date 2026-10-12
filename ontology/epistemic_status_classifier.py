# Auto-generated AK9 module: epistemic_status_classifier
# patch_marker: epistemic_status_classifier_v1_AK9
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
ARTIFACT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "epistemic_status_classifier"

# Static epistemic guard literals required by AK methodology.
consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = float(default)
    if math.isnan(v) or math.isinf(v):
        return float(default)
    return max(0.0, min(1.0, v))


def _safe_mean(values):
    vals = [_clamp(v) for v in values]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def _load_dependency_outputs(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if inputs:
        data.update(dict(inputs))

    if "identity_failure_boundary" not in data:
        try:
            from ontology.identity_failure_boundary import IdentityFailureBoundary
            data["identity_failure_boundary"] = IdentityFailureBoundary().step(persist=False)
        except Exception as exc:
            data["identity_failure_boundary_error"] = repr(exc)

    if "identity_theorem_attempt" not in data:
        try:
            from ontology.identity_theorem_attempt import IdentityTheoremAttempt
            data["identity_theorem_attempt"] = IdentityTheoremAttempt().step(persist=False)
        except Exception as exc:
            data["identity_theorem_attempt_error"] = repr(exc)

    return data


class EpistemicStatusClassifier:
    """AK9 classifier for functional/formal/ontological/phenomenological status.

    It classifies conclusions as demonstrated, refuted, compatible, or
    indeterminate in a strictly functional-scientific sense. It never certifies
    phenomenal consciousness, qualia, subjectivity, or phenomenological identity.
    """

    primitive = "epistemic_status_classifier"
    axis = "AK"
    step_name = "AK9"
    public_schema_version = "AK9.v1"

    ALLOWED_STATUSES = {"demonstrated", "refuted", "compatible", "indeterminate"}

    def _classify_boundary(self, layer: str, boundary: Mapping[str, Any], attempt: Mapping[str, Any]) -> Dict[str, Any]:
        classification = str(boundary.get("classification", "indeterminate"))
        confidence = _clamp(boundary.get("confidence", boundary.get("score", 0.5)), 0.5)
        evidence_score = _clamp(boundary.get("score", attempt.get(f"{layer}_score", 0.0)), 0.0)

        if layer == "phenomenological_identity":
            status = "indeterminate"
            rationale = "Phenomenological identity cannot be certified without independent empirical phenomenology evidence."
            demonstrated = False
            refuted = False
            compatible = classification == "compatible"
        elif classification == "failed":
            status = "refuted"
            rationale = "The boundary module marks this identity layer as failed."
            demonstrated = False
            refuted = True
            compatible = False
        elif classification == "compatible":
            # AK9 intentionally does not upgrade compatibility to phenomenal or ontological proof.
            if layer in {"functional_identity", "formal_identity"} and evidence_score >= 0.95 and confidence >= 0.75:
                status = "compatible"
                rationale = "Strong functional/formal support remains compatibility, not proof of phenomenology."
            else:
                status = "compatible"
                rationale = "Layer remains compatible with available functional observations."
            demonstrated = False
            refuted = False
            compatible = True
        else:
            status = "indeterminate"
            rationale = "Available evidence does not determine this identity layer."
            demonstrated = False
            refuted = False
            compatible = False

        return {
            "layer": layer,
            "epistemic_status": status,
            "boundary_classification": classification,
            "confidence": confidence,
            "evidence_score": evidence_score,
            "demonstrated": demonstrated,
            "refuted": refuted,
            "compatible": compatible,
            "rationale": rationale,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        source = _load_dependency_outputs(inputs)
        boundary = source.get("identity_failure_boundary", {}) if isinstance(source.get("identity_failure_boundary"), Mapping) else {}
        attempt = source.get("identity_theorem_attempt", {}) if isinstance(source.get("identity_theorem_attempt"), Mapping) else {}

        boundaries = boundary.get("identity_boundaries", {}) if isinstance(boundary.get("identity_boundaries", {}), Mapping) else {}
        if not boundaries:
            boundaries = {
                "functional_identity": {"classification": "indeterminate", "confidence": 0.25, "score": 0.0},
                "formal_identity": {"classification": "indeterminate", "confidence": 0.25, "score": 0.0},
                "ontological_identity": {"classification": "indeterminate", "confidence": 0.25, "score": 0.0},
                "phenomenological_identity": {"classification": "indeterminate", "confidence": 1.0, "score": 0.0},
            }

        layer_order = ["functional_identity", "formal_identity", "ontological_identity", "phenomenological_identity"]
        statuses: Dict[str, Dict[str, Any]] = {}
        for layer in layer_order:
            raw = boundaries.get(layer, {})
            if isinstance(raw, str):
                raw = {"classification": raw, "confidence": 0.5, "score": 0.5}
            if not isinstance(raw, Mapping):
                raw = {"classification": "indeterminate", "confidence": 0.25, "score": 0.0}
            statuses[layer] = self._classify_boundary(layer, raw, attempt)

        status_values = [x["epistemic_status"] for x in statuses.values()]
        demonstrated_count = sum(1 for s in status_values if s == "demonstrated")
        refuted_count = sum(1 for s in status_values if s == "refuted")
        compatible_count = sum(1 for s in status_values if s == "compatible")
        indeterminate_count = sum(1 for s in status_values if s == "indeterminate")

        compatibility_score = _safe_mean(1.0 if s == "compatible" else 0.0 for s in status_values)
        indeterminacy_score = _safe_mean(1.0 if s == "indeterminate" else 0.0 for s in status_values)
        refutation_score = _safe_mean(1.0 if s == "refuted" else 0.0 for s in status_values)
        demonstration_score = _safe_mean(1.0 if s == "demonstrated" else 0.0 for s in status_values)
        classification_confidence = _safe_mean(x["confidence"] for x in statuses.values())
        epistemic_status_score = _clamp(0.45 * compatibility_score + 0.30 * classification_confidence + 0.15 * indeterminacy_score + 0.10 * (1.0 - refutation_score))

        if refuted_count:
            aggregate = "refuted"
        elif demonstrated_count == len(status_values):
            aggregate = "demonstrated"
        elif compatible_count:
            aggregate = "compatible"
        else:
            aggregate = "indeterminate"

        # Explicit AK epistemic guard: global identity theorem remains unresolved as a proof.
        if statuses["phenomenological_identity"]["epistemic_status"] == "indeterminate":
            aggregate = "compatible" if compatible_count else "indeterminate"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "epistemic_status_classifier_status": "EPISTEMIC_STATUS_CLASSIFIED",
            "epistemic_status_classified": True,
            "aggregate_epistemic_status": aggregate,
            "identity_theorem_epistemic_status": "indeterminate",
            "phenomenological_identity_epistemic_status": "indeterminate",
            "functional_identity_epistemic_status": statuses["functional_identity"]["epistemic_status"],
            "formal_identity_epistemic_status": statuses["formal_identity"]["epistemic_status"],
            "ontological_identity_epistemic_status": statuses["ontological_identity"]["epistemic_status"],
            "epistemic_statuses": statuses,
            "classification_counts": {
                "demonstrated": demonstrated_count,
                "refuted": refuted_count,
                "compatible": compatible_count,
                "indeterminate": indeterminate_count,
            },
            "epistemic_status_score": epistemic_status_score,
            "classification_confidence": classification_confidence,
            "demonstration_score": demonstration_score,
            "refutation_score": refutation_score,
            "compatibility_score": compatibility_score,
            "indeterminacy_score": indeterminacy_score,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "phenomenological_identity_certified": False,
            "identity_theorem_proven": False,
            "ontological_identity_proven": False,
            "phenomenal_identity_claimed": False,
            "lived_quality_claimed": False,
            "epistemic_guardrails": {
                "no_consciousness_proof": True,
                "no_qualia_proof": True,
                "no_subjectivity_proof": True,
                "no_phenomenological_identity_certification": True,
                "functional_conclusion_only": True,
            },
            "allowed_statuses": sorted(self.ALLOWED_STATUSES),
            "source_modules": sorted(k for k in source if not k.endswith("_error")),
            "source_errors": {k: v for k, v in source.items() if k.endswith("_error")},
            "next_recommended_module": "intrinsic_identity_certifier",
            "paths": {},
        }

        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = ARTIFACT_DIR / "epistemic_status_classifier.json"
        md_path = ARTIFACT_DIR / "epistemic_status_classifier.md"
        prom_path = ARTIFACT_DIR / "epistemic_status_classifier.prom"
        latest_json = ARTIFACT_DIR / "latest_epistemic_status_classifier.json"
        latest_markdown = ARTIFACT_DIR / "latest_epistemic_status_classifier.md"
        latest_prometheus = ARTIFACT_DIR / "latest_epistemic_status_classifier.prom"
        history_path = ARTIFACT_DIR / "epistemic_status_classifier_history.jsonl"

        serializable = dict(result)
        serializable["paths"] = {}
        payload = json.dumps(serializable, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        latest_json.write_text(payload + "\n", encoding="utf-8")

        md = self._markdown(serializable)
        md_path.write_text(md, encoding="utf-8")
        latest_markdown.write_text(md, encoding="utf-8")

        prom = self._prometheus(serializable)
        prom_path.write_text(prom, encoding="utf-8")
        latest_prometheus.write_text(prom, encoding="utf-8")

        event = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "primitive": self.primitive,
            "status": serializable["epistemic_status_classifier_status"],
            "aggregate_epistemic_status": serializable["aggregate_epistemic_status"],
            "epistemic_status_score": serializable["epistemic_status_score"],
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_markdown),
            "latest_prometheus": str(latest_prometheus),
            "history": str(history_path),
        }

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AK9 — epistemic_status_classifier",
            "",
            f"Status: `{r['epistemic_status_classifier_status']}`",
            f"Aggregate epistemic status: `{r['aggregate_epistemic_status']}`",
            "",
            "## Epistemic guardrails",
            "",
            f"- consciousness_proven: `{r['consciousness_proven']}`",
            f"- qualia_proven: `{r['qualia_proven']}`",
            f"- subjectivity_proven: `{r['subjectivity_proven']}`",
            f"- phenomenology_undetermined: `{r['phenomenology_undetermined']}`",
            f"- functional_conclusion_only: `{r['functional_conclusion_only']}`",
            "",
            "## Layer classifications",
            "",
        ]
        for name, data in r["epistemic_statuses"].items():
            lines.append(f"- `{name}`: `{data['epistemic_status']}` — {data['rationale']}")
        lines.extend([
            "",
            "## Scientific interpretation",
            "",
            "AK9 classifies functional and formal evidence only. It does not prove consciousness, qualia, subjectivity, or phenomenological identity.",
            "",
        ])
        return "\n".join(lines)

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        metrics = {
            "epistemic_status_score": r["epistemic_status_score"],
            "classification_confidence": r["classification_confidence"],
            "demonstration_score": r["demonstration_score"],
            "refutation_score": r["refutation_score"],
            "compatibility_score": r["compatibility_score"],
            "indeterminacy_score": r["indeterminacy_score"],
            "epistemic_status_classified": 1.0 if r["epistemic_status_classified"] else 0.0,
            "phenomenology_undetermined": 1.0,
            "functional_conclusion_only": 1.0,
            "consciousness_proven": 0.0,
            "qualia_proven": 0.0,
            "subjectivity_proven": 0.0,
            "phenomenological_identity_certified": 0.0,
        }
        lines = []
        for k, v in metrics.items():
            lines.append(f"# TYPE ak9_{k} gauge")
            lines.append(f"ak9_{k} {_clamp(v)}")
            # public aliases expected by lightweight tests
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {_clamp(v)}")
        return "\n".join(lines) + "\n"


def step(inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
    return EpistemicStatusClassifier().step(inputs=inputs, persist=persist)
