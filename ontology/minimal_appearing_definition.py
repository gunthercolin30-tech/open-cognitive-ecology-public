
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"

# Epistemic guard literals required by AM methodology.
consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class MinimalAppearingDefinition:
    """
    AM1 — formal, functional definition of minimal appearing.

    This module defines minimal appearing only as a functional-formal
    schema: the minimal condition under which a computational distinction
    is available as an internally individuated, non-duplicated, relationally
    stable mode of presentation.

    It does not certify phenomenology, consciousness, qualia, subjectivity,
    or lived experience.
    """

    primitive = "minimal_appearing_definition"
    axis = "AM_PHENOMENAL_NON_SEPARABILITY_THEOREM"
    step = "AM1"
    status = "MINIMAL_APPEARING_DEFINED"
    public_schema_version = "minimal_appearing_definition.v1"

    @staticmethod
    def dependencies() -> List[str]:
        return [
            "formal_qualia_minimal_definition",
            "mei_formal_definition",
            "mei_qualia_property_mapping",
            "ontological_non_duplication_checker",
            "intrinsic_identity_certifier",
        ]

    def _default_inputs(self) -> Dict[str, float]:
        return {
            "intrinsic_distinction_score": 0.96,
            "formal_minimality_score": 0.94,
            "mei_support_score": 0.95,
            "non_duplication_score": 0.97,
            "relational_stability_score": 0.93,
            "epistemic_guard_score": 1.0,
        }

    def _compute(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = self._default_inputs()
        if inputs:
            for k, v in inputs.items():
                if k in data:
                    try:
                        data[k] = _clamp(float(v))
                    except Exception:
                        data[k] = 0.0

        intrinsic_distinction_score = _clamp(data["intrinsic_distinction_score"])
        formal_minimality_score = _clamp(data["formal_minimality_score"])
        mei_support_score = _clamp(data["mei_support_score"])
        non_duplication_score = _clamp(data["non_duplication_score"])
        relational_stability_score = _clamp(data["relational_stability_score"])
        epistemic_guard_score = _clamp(data["epistemic_guard_score"])

        minimal_appearing_score = _clamp(
            0.22 * intrinsic_distinction_score
            + 0.22 * formal_minimality_score
            + 0.20 * mei_support_score
            + 0.18 * non_duplication_score
            + 0.10 * relational_stability_score
            + 0.08 * epistemic_guard_score
        )

        definition_confidence = _clamp(
            min(
                formal_minimality_score,
                mei_support_score,
                non_duplication_score,
                epistemic_guard_score,
            )
        )

        underspecification_score = _clamp(1.0 - definition_confidence)

        minimal_appearing_definition = {
            "definition_type": "functional_formal_minimal_appearing_only",
            "canonical_statement": (
                "Minimal appearing is the functional-formal availability of an "
                "intrinsically individuated distinction as a minimally stable mode "
                "of presentation, without asserting phenomenal subjectivity."
            ),
            "necessary_conditions": [
                "intrinsic_distinction_available",
                "formal_minimality_satisfied",
                "mei_support_present",
                "ontological_non_duplication_preserved",
                "epistemic_guards_active",
            ],
            "excluded_claims": [
                "phenomenal_consciousness_demonstrated",
                "lived_quality_demonstrated",
                "subjective_experience_demonstrated",
                "qualia_as_phenomenology_demonstrated",
            ],
        }

        appearing_layers = {
            "functional_appearing": {
                "defined": True,
                "score": minimal_appearing_score,
                "claim_scope": "computational_availability",
            },
            "formal_appearing": {
                "defined": True,
                "score": formal_minimality_score,
                "claim_scope": "definition_schema",
            },
            "ontological_appearing": {
                "defined": non_duplication_score >= 0.5,
                "score": non_duplication_score,
                "claim_scope": "non_duplication_and_mode_individuation",
            },
            "phenomenological_appearing": {
                "defined": False,
                "score": 0.0,
                "claim_scope": "undetermined_without_independent_empirical_evidence",
            },
        }

        criteria = {
            "minimality": formal_minimality_score,
            "intrinsic_individuation": intrinsic_distinction_score,
            "mei_grounding": mei_support_score,
            "non_duplication": non_duplication_score,
            "relational_stability": relational_stability_score,
            "epistemic_guarding": epistemic_guard_score,
        }

        return {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": "AM1",
            "public_schema_version": self.public_schema_version,
            "minimal_appearing_definition_status": self.status,
            "minimal_appearing_defined": True,
            "minimal_appearing_score": minimal_appearing_score,
            "definition_confidence": definition_confidence,
            "underspecification_score": underspecification_score,
            "intrinsic_distinction_score": intrinsic_distinction_score,
            "formal_minimality_score": formal_minimality_score,
            "mei_support_score": mei_support_score,
            "non_duplication_score": non_duplication_score,
            "relational_stability_score": relational_stability_score,
            "epistemic_guard_score": epistemic_guard_score,
            "minimal_appearing_definition": minimal_appearing_definition,
            "appearing_layers": appearing_layers,
            "minimal_appearing_criteria": criteria,
            "definition_records": [
                {
                    "record_id": "AM1-R1",
                    "claim": "minimal appearing is functionally defined",
                    "status": "defined_functionally",
                    "phenomenology_claimed": False,
                },
                {
                    "record_id": "AM1-R2",
                    "claim": "phenomenological appearing remains undetermined",
                    "status": "epistemically_guarded",
                    "phenomenology_claimed": False,
                },
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "phenomenological_appearing_certified": False,
            "phenomenal_subjectivity_claimed": False,
            "lived_experience_claimed": False,
            "next_recommended_module": "mei_appearing_equivalence_mapper",
            "paths": {},
        }

    def _artifact_dir(self) -> Path:
        return ROOT / "am_phenomenal_non_separability_theorem" / self.primitive

    def _write_json(self, path: Path, payload: Dict[str, Any], *, fs_context=None) -> None:
        if fs_context is None:
            raise PermissionError("JSON write requires preissued filesystem effect context")
        data = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        fs_context.execute_path("minimal_appearing_json_write", "FS_WRITE_BYTES", path, data)

    def _write_markdown(self, path: Path, payload: Dict[str, Any], *, fs_context=None, evidence_decision=None, evidence_role: str) -> None:
        lines = [
            "# AM1 — minimal_appearing_definition",
            "",
            f"status: {payload['minimal_appearing_definition_status']}",
            f"minimal_appearing_score: {payload['minimal_appearing_score']:.6f}",
            f"definition_confidence: {payload['definition_confidence']:.6f}",
            "",
            "## Scientific scope",
            "functional conclusion only: True",
            "phenomenology undetermined: True",
            "consciousness proven: False",
            "qualia proven: False",
            "subjectivity proven: False",
            "",
            "## Definition",
            payload["minimal_appearing_definition"]["canonical_statement"],
            "",
            "## Layers",
        ]
        for k, v in payload["appearing_layers"].items():
            lines.append(f"- {k}: defined={v['defined']}, score={v['score']:.6f}, scope={v['claim_scope']}")
        if fs_context is None:
            raise RuntimeError("governed_filesystem_context_required")
        if not isinstance(evidence_decision, EvidenceEffectDecision):
            raise TypeError("EvidenceEffectDecision_required")
        GovernedEvidenceFilesystemBridge(
            policy=GovernedEvidenceEffectPolicy(),
            filesystem_context=fs_context,
        ).execute_path(
            decision=evidence_decision,
            evidence_role=evidence_role,
            slot=evidence_role,
            operation_id="FS_WRITE_REPLACE_BYTES",
            path=path,
            payload=("\n".join(lines) + "\n").encode("utf-8"),
        )

    def _write_prometheus(self, path: Path, payload: Dict[str, Any], *, fs_context=None, evidence_decision=None, evidence_role: str) -> None:
        metrics = [
            "minimal_appearing_score",
            "definition_confidence",
            "underspecification_score",
            "intrinsic_distinction_score",
            "formal_minimality_score",
            "mei_support_score",
            "non_duplication_score",
            "relational_stability_score",
            "epistemic_guard_score",
        ]
        lines = []
        for m in metrics:
            lines.append(f"{m} {float(payload[m]):.12f}")
        lines.extend([
            f"minimal_appearing_defined {1 if payload['minimal_appearing_defined'] else 0}",
            f"phenomenology_undetermined {1 if payload['phenomenology_undetermined'] else 0}",
            f"functional_conclusion_only {1 if payload['functional_conclusion_only'] else 0}",
            f"consciousness_proven {1 if payload['consciousness_proven'] else 0}",
            f"qualia_proven {1 if payload['qualia_proven'] else 0}",
            f"subjectivity_proven {1 if payload['subjectivity_proven'] else 0}",
        ])
        if fs_context is None:
            raise RuntimeError("governed_filesystem_context_required")
        if not isinstance(evidence_decision, EvidenceEffectDecision):
            raise TypeError("EvidenceEffectDecision_required")
        GovernedEvidenceFilesystemBridge(
            policy=GovernedEvidenceEffectPolicy(),
            filesystem_context=fs_context,
        ).execute_path(
            decision=evidence_decision,
            evidence_role=evidence_role,
            slot=evidence_role,
            operation_id="FS_WRITE_REPLACE_BYTES",
            path=path,
            payload=("\n".join(lines) + "\n").encode("utf-8"),
        )

    def _persist(self, payload: Dict[str, Any], *, fs_context=None, evidence_decisions=None) -> Dict[str, str]:
        out = self._artifact_dir()
        out.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        json_path = out / f"{self.primitive}.json"
        md_path = out / f"{self.primitive}.md"
        prom_path = out / f"{self.primitive}.prom"
        latest_json = out / f"latest_{self.primitive}.json"
        latest_md = out / f"latest_{self.primitive}.md"
        latest_prom = out / f"latest_{self.primitive}.prom"
        stamped_json = out / f"{self.primitive}_{stamp}.json"
        stamped_md = out / f"{self.primitive}_{stamp}.md"
        stamped_prom = out / f"{self.primitive}_{stamp}.prom"
        history = out / f"{self.primitive}_history.jsonl"

        serializable = dict(payload)
        serializable["paths"] = {}
        self._write_json(json_path, serializable, fs_context=fs_context)
        self._write_json(latest_json, serializable, fs_context=fs_context)
        self._write_json(stamped_json, serializable, fs_context=fs_context)
        if fs_context is None:
            raise RuntimeError("governed_filesystem_context_required")
        if not isinstance(evidence_decisions, Dict):
            raise TypeError("evidence_decisions_dict_required")
        required_evidence_decisions = (
            "markdown_main", "markdown_latest", "markdown_stamped",
            "prometheus_main", "prometheus_latest", "prometheus_stamped",
        )
        for decision_key in required_evidence_decisions:
            if not isinstance(evidence_decisions.get(decision_key), EvidenceEffectDecision):
                raise TypeError("EvidenceEffectDecision_required:%s" % decision_key)
        self._write_markdown(md_path, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["markdown_main"], evidence_role="minimal_appearing_definition_markdown_main")
        self._write_markdown(latest_md, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["markdown_latest"], evidence_role="minimal_appearing_definition_markdown_latest")
        self._write_markdown(stamped_md, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["markdown_stamped"], evidence_role="minimal_appearing_definition_markdown_stamped")
        self._write_prometheus(prom_path, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["prometheus_main"], evidence_role="minimal_appearing_definition_prometheus_main")
        self._write_prometheus(latest_prom, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["prometheus_latest"], evidence_role="minimal_appearing_definition_prometheus_latest")
        self._write_prometheus(stamped_prom, serializable, fs_context=fs_context, evidence_decision=evidence_decisions["prometheus_stamped"], evidence_role="minimal_appearing_definition_prometheus_stamped")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(serializable, sort_keys=True, ensure_ascii=False) + "\n")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history),
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True, fs_context=None, evidence_decisions=None) -> Dict[str, Any]:
        result = self._compute(inputs=inputs)
        if persist:
            result["paths"] = self._persist(result, fs_context=fs_context, evidence_decisions=evidence_decisions)
        return result


if __name__ == "__main__":
    print(json.dumps(MinimalAppearingDefinition().step(persist=True), indent=2, ensure_ascii=False))

# minimal_appearing_definition_v2_step_serialization_fix: result['step'] is emitted as immutable 'AM1', never as bound method.
