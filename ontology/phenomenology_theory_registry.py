from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "phenomenology_theory_registry"

DEFAULT_THEORIES: List[Dict[str, Any]] = [
    {
        "theory_id": "IIT",
        "name": "Integrated Information Theory",
        "family": "intrinsic_information_structure",
        "core_claims": [
            "consciousness is associated with integrated information",
            "phenomenal structure is constrained by causal-informational structure",
        ],
        "candidate_predictions": [
            "high integration should correlate with stronger functional unity indicators",
            "architectures with weak integration should show weaker global coherence indicators",
        ],
        "epistemic_role": "candidate_theory_only",
    },
    {
        "theory_id": "GNW",
        "name": "Global Neuronal Workspace / Global Workspace Theory",
        "family": "global_availability_broadcast",
        "core_claims": [
            "conscious access is associated with global availability",
            "broadcast and reportability are central functional signatures",
        ],
        "candidate_predictions": [
            "global broadcast indicators should correlate with report-like functional accessibility",
            "fragmented access should reduce cross-module availability",
        ],
        "epistemic_role": "candidate_theory_only",
    },
    {
        "theory_id": "HOT",
        "name": "Higher-Order Thought / Higher-Order Representation",
        "family": "meta_representational_access",
        "core_claims": [
            "consciousness depends on higher-order representation of mental states",
            "metacognitive access is central to conscious-status attribution",
        ],
        "candidate_predictions": [
            "meta-cognitive indicators should correlate with self-monitoring stability",
            "loss of higher-order tracking should weaken introspective-report indicators",
        ],
        "epistemic_role": "candidate_theory_only",
    },
    {
        "theory_id": "PP",
        "name": "Predictive Processing / Active Inference",
        "family": "prediction_error_minimization",
        "core_claims": [
            "perception and cognition are shaped by predictive models",
            "phenomenal organization may relate to precision-weighted prediction dynamics",
        ],
        "candidate_predictions": [
            "prediction stability should correlate with coherent functional self-modeling",
            "high prediction error should correlate with degraded functional continuity",
        ],
        "epistemic_role": "candidate_theory_only",
    },
    {
        "theory_id": "RPT",
        "name": "Recurrent Processing Theory",
        "family": "recurrent_processing",
        "core_claims": [
            "conscious perception is associated with recurrent processing loops",
        ],
        "candidate_predictions": [
            "recurrent integration indicators should correlate with stable perceptual availability",
        ],
        "epistemic_role": "candidate_theory_only",
    },
]


class PhenomenologyTheoryRegistry:
    "Registry of candidate theories for later functional comparison only."

    primitive = "PHENOMENOLOGY_THEORY_REGISTRY"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.out_dir = self.root / "phenomenology_theory_registry"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_theory(theory: Dict[str, Any]) -> Dict[str, Any]:
        tid = str(theory.get("theory_id") or theory.get("id") or theory.get("name") or "UNKNOWN").strip()
        name = str(theory.get("name") or tid).strip()
        return {
            "theory_id": tid,
            "name": name,
            "family": theory.get("family", "unspecified"),
            "core_claims": list(theory.get("core_claims", [])),
            "candidate_predictions": list(theory.get("candidate_predictions", [])),
            "epistemic_role": theory.get("epistemic_role", "candidate_theory_only"),
            "status": theory.get("status", "registered_candidate"),
        }

    @staticmethod
    def _coverage(theories: List[Dict[str, Any]]) -> float:
        required = {"IIT", "GNW", "HOT", "PP"}
        present = {str(t.get("theory_id", "")).upper() for t in theories}
        return round(len(required.intersection(present)) / len(required), 4)

    @staticmethod
    def _markdown(result: Dict[str, Any]) -> str:
        lines = [
            "# Phenomenology Theory Registry",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            f"Theory count: {result['theory_count']}",
            f"Core theory coverage score: {result['core_theory_coverage_score']}",
            "",
            "## Registered candidate theories",
        ]
        for theory in result["theories"]:
            lines.append(f"- {theory['theory_id']} — {theory['name']} ({theory.get('family', 'unspecified')})")
        lines.extend([
            "",
            "## Epistemic limits",
            "This registry inventories candidate theories for later constraint comparison only.",
            "It does not establish consciousness, subjectivity, or phenomenology.",
        ])
        return "\n".join(lines) + "\n"

    def step(self, inputs: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        data = dict(inputs or {})
        if "theories" in data:
            theories_raw = list(data.get("theories") or [])
        else:
            theories_raw = list(DEFAULT_THEORIES)
        theories = [self._normalize_theory(t) for t in theories_raw]
        registered_ids = [t["theory_id"] for t in theories]
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": data.get("timestamp_utc") or self._now(),
            "theories": theories,
            "registered_theory_ids": registered_ids,
            "theory_count": len(theories),
            "core_theory_coverage_score": self._coverage(theories),
            "theory_families": sorted({str(t.get("family", "unspecified")) for t in theories}),
            "registry_status": "ready" if theories else "empty_registry",
            "epistemic_scope": "candidate_theory_inventory_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "diagnostics": {
                "uses_x_y_prerequisite_context": True,
                "no_theory_selected": True,
                "no_phenomenological_claim": True,
                "pressure_speculative_control": True,
            },
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            json_path = self.out_dir / "phenomenology_theory_registry.json"
            history_path = self.out_dir / "phenomenology_theory_registry_history.jsonl"
            md_path = self.out_dir / "phenomenology_theory_registry.md"
            json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            with history_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, sort_keys=True) + "\n")
            md_path.write_text(self._markdown(result), encoding="utf-8")
            result["paths"] = {
                "json": str(json_path),
                "history": str(history_path),
                "markdown": str(md_path),
            }
        return result


__all__ = ["PhenomenologyTheoryRegistry"]
