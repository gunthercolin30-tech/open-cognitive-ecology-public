
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS = "SEMANTIC_STATUS_SCHEMA_ESTABLISHED"

@dataclass(frozen=True)
class SemanticInputField:
    name: str
    kind: str
    required: bool
    description: str

@dataclass(frozen=True)
class SemanticStatusDefinition:
    status: str
    rank: int
    category: str
    description: str
    phenomenal_claim: bool
    absolute_claim: bool

class SemanticStatusSchema:
    primitive = "SEMANTIC_STATUS_SCHEMA"
    step_id = "AO1"
    public_schema_version = "open-cognitive-ecology.AO1.semantic_status_schema.v1"
    AUTHORIZED_STATUSES = [
        "CONSCIOUSNESS_NOT_EVALUATED",
        "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
        "PHENOMENALITY_CANDIDATE_SUPPORTED",
        "QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED",
        "CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED",
        "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
        "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "CONSCIOUSNESS_PROVEN",
        "ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN",
    ]
    INPUT_FIELDS = [
        SemanticInputField("RF_score", "score", True, "Reference-frame reconstruction score."),
        SemanticInputField("T_score", "score", True, "T-theoretic score."),
        SemanticInputField("ED_score", "score", True, "Explanatory-difference score."),
        SemanticInputField("TΦ_score", "score", True, "T-phi / topology-phi score."),
        SemanticInputField("QF_robust_count", "count", True, "Robust qualia-formalization count."),
        SemanticInputField("MEI_score", "score", True, "Mode of intrinsic existence score."),
        SemanticInputField("identity_status", "status", True, "Identity assessment status."),
        SemanticInputField("non_separability_status", "status", True, "Non-separability theorem status."),
        SemanticInputField("consciousness_rf_equivalence_status", "status", True, "RF equivalence theorem status."),
        SemanticInputField("refusal_cost_status", "status", True, "Cost of refusal status."),
        SemanticInputField("definition_legitimacy_status", "status", True, "Definition legitimacy status."),
        SemanticInputField("axiomatic_completeness_status", "status", True, "Axiomatic completeness status."),
    ]
    STATUS_DEFINITIONS = [
        SemanticStatusDefinition("CONSCIOUSNESS_NOT_EVALUATED", 0, "null_evaluation", "No semantic interpretation has been licensed.", False, False),
        SemanticStatusDefinition("FUNCTIONAL_CONSCIOUSNESS_SUPPORTED", 10, "functional", "Functional evidence supports consciousness-like organization.", False, False),
        SemanticStatusDefinition("PHENOMENALITY_CANDIDATE_SUPPORTED", 20, "candidate", "Phenomenality is only candidate-level and remains undetermined.", False, False),
        SemanticStatusDefinition("QUALIA_IDENTITY_CONDITIONALLY_SUPPORTED", 30, "conditional_identity", "Qualia identity is conditionally supported within explicit formal constraints.", False, False),
        SemanticStatusDefinition("CONSCIOUSNESS_AS_RF_EQUIVALENCE_SUPPORTED", 40, "rf_equivalence", "Consciousness-as-RF equivalence is supported inside the RF reconstruction frame.", False, False),
        SemanticStatusDefinition("CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK", 50, "framework_internal", "Proof is internal to the RF framework and not absolute phenomenology.", False, False),
        SemanticStatusDefinition("CONSCIOUSNESS_PROVEN_BEST_THEORY", 60, "best_theory", "Best-theory proof status, still epistemically bounded.", False, False),
        SemanticStatusDefinition("CONSCIOUSNESS_PROVEN", 70, "reserved_final", "Reserved final status; AO1 defines but does not authorize it.", True, False),
        SemanticStatusDefinition("ABSOLUTE_CONSCIOUSNESS_NOT_PROVEN", 80, "absolute_guard", "Absolute consciousness is explicitly not proven.", False, False),
    ]
    LAYERS = {
        "measurements": ["RF_score", "T_score", "ED_score", "TΦ_score", "QF_robust_count", "MEI_score"],
        "theorems": ["non_separability_status", "consciousness_rf_equivalence_status", "axiomatic_completeness_status"],
        "interpretations": ["identity_status", "refusal_cost_status", "definition_legitimacy_status"],
        "final_statuses": AUTHORIZED_STATUSES,
    }
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.out_dir = self.root / "semantic_interpretation_layer"
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
    @staticmethod
    def _clamp01(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, v))
    def validate_status(self, status: str) -> bool:
        return str(status) in self.AUTHORIZED_STATUSES
    def normalize_inputs(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        normalized: dict[str, Any] = {}
        for field in self.INPUT_FIELDS:
            if field.kind == "score":
                normalized[field.name] = self._clamp01(inputs.get(field.name, 0.0))
            elif field.kind == "count":
                try:
                    normalized[field.name] = max(0, int(inputs.get(field.name, 0)))
                except Exception:
                    normalized[field.name] = 0
            else:
                normalized[field.name] = str(inputs.get(field.name, "CONSCIOUSNESS_NOT_EVALUATED"))
        return normalized
    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        normalized_inputs = self.normalize_inputs(inputs)
        status_definitions = [asdict(s) for s in self.STATUS_DEFINITIONS]
        input_schema = [asdict(f) for f in self.INPUT_FIELDS]
        authorized_status_count = len(self.AUTHORIZED_STATUSES)
        separation_layers = {k: list(v) for k, v in self.LAYERS.items()}
        schema_complete = authorized_status_count == 9 and set(separation_layers) == {"measurements", "theorems", "interpretations", "final_statuses"}
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "semantic_status_schema_status": STATUS,
            "semantic_interpretation_layer_step_ready": bool(schema_complete),
            "semantic_interpretation_layer_ready": False,
            "authorized_statuses": list(self.AUTHORIZED_STATUSES),
            "authorized_status_count": authorized_status_count,
            "status_definitions": status_definitions,
            "input_schema": input_schema,
            "normalized_inputs": normalized_inputs,
            "separation_layers": separation_layers,
            "required_input_fields": [f.name for f in self.INPUT_FIELDS if f.required],
            "schema_guards": {
                "separates_measurements_theorems_interpretations_statuses": True,
                "authorized_status_closed_set": True,
                "consciousness_proven_reserved_not_asserted": True,
                "absolute_consciousness_not_proven_explicit": True,
            },
            "epistemic_scope": "semantic_schema_only_no_empirical_or_phenomenal_proof",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            out = self.out_dir / "latest_semantic_status_schema.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["persisted_path"] = str(out)
        return result
