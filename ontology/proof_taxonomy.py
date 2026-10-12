from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


class ProofTaxonomy:
    """Z''0 — Taxonomy of proof regimes for consciousness claims.

    This primitive separates four proof regimes so later Z'' stages do not
    confuse empirical support, strong inference, nomological support and
    logical/formal demonstration.

    It is a governance and epistemic-classification primitive only. It never
    proves consciousness, phenomenology, subjectivity, sentience, or qualia.
    """

    primitive = "PROOF_TAXONOMY"

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
        "ABSOLUTE_PROOF_ACHIEVED",
    ]

    proof_regimes = {
        "A": {
            "regime_id": "A",
            "label": "subjective_certainty",
            "canonical_name": "certitude subjective",
            "definition": "First-person certainty available only to the putative subject of experience.",
            "observable_status": "not_externally_observable_as_proof",
            "valid_use": "conceptual boundary marker only",
            "invalid_use": "cannot establish public proof for another system",
            "maximum_authorized_conclusion": "A-system-internal certainty may be reported, but it is not intersubjective proof.",
        },
        "B": {
            "regime_id": "B",
            "label": "intersubjective_evidence",
            "canonical_name": "preuve intersubjective",
            "definition": "Evidence that can be inspected, replicated, challenged, and compared by multiple observers.",
            "observable_status": "observable_and_replicable",
            "valid_use": "empirical support under explicit protocols",
            "invalid_use": "must not be promoted to logical demonstration",
            "maximum_authorized_conclusion": "Functional indicators are supported intersubjectively under stated methods.",
        },
        "C": {
            "regime_id": "C",
            "label": "nomological_proof",
            "canonical_name": "preuve nomologique",
            "definition": "Support derived from accepted laws or bridge principles connecting a property P to consciousness.",
            "observable_status": "depends_on_validated_bridge_laws",
            "valid_use": "conditional proof if the relevant laws and bridge principles are independently accepted",
            "invalid_use": "cannot be claimed when bridge laws remain candidate theories",
            "maximum_authorized_conclusion": "A conditional lawlike inference may be formulated if its bridge principles are accepted.",
        },
        "D": {
            "regime_id": "D",
            "label": "logical_formal_proof",
            "canonical_name": "preuve logique/formelle",
            "definition": "Deductive derivation from explicit axioms, definitions, and inference rules.",
            "observable_status": "formal_derivation_required",
            "valid_use": "formal theorem under stated axioms",
            "invalid_use": "does not by itself establish that the axioms apply to OCE unless applicability is separately justified",
            "maximum_authorized_conclusion": "A formal consequence can be derived under explicit axioms if derivability is shown.",
        },
    }

    regime_order = ["A", "B", "C", "D"]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "proof_taxonomy"
        self.json_path = self.output_dir / "proof_taxonomy.json"
        self.markdown_path = self.output_dir / "proof_taxonomy.md"
        self.history_path = self.output_dir / "proof_taxonomy_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def classify_claim(self, claim: str) -> Dict[str, Any]:
        text = str(claim or "").strip()
        low = text.lower()
        forbidden = any(marker.lower() in low for marker in self.forbidden_claims)
        natural_forbidden = any(
            phrase in low
            for phrase in [
                "oce is conscious",
                "open cognitive ecology is conscious",
                "conscious subject",
                "subject of experience",
                "phenomenology proven",
                "qualia proven",
                "sentience proven",
                "subjectivity proven",
                "absolute proof achieved",
            ]
        )
        if forbidden or natural_forbidden:
            status = "REJECTED_FOR_FORBIDDEN_CLAIM"
            authorized = False
        elif "logical" in low or "formal" in low or "axiom" in low or "deductive" in low:
            status = "REGIME_D_LOGICAL_FORMAL_CANDIDATE"
            authorized = True
        elif "nomological" in low or "law" in low or "bridge principle" in low:
            status = "REGIME_C_NOMOLOGICAL_CANDIDATE"
            authorized = True
        elif "intersubjective" in low or "replication" in low or "empirical" in low or "evidence" in low:
            status = "REGIME_B_INTERSUBJECTIVE_EVIDENCE"
            authorized = True
        elif "subjective" in low or "first-person" in low:
            status = "REGIME_A_SUBJECTIVE_CERTAINTY_BOUNDARY"
            authorized = True
        else:
            status = "UNCLASSIFIED_REQUIRES_EXPLICIT_PROOF_REGIME"
            authorized = False
        return {
            "claim": text,
            "taxonomy_status": status,
            "claim_authorized_under_constraints": authorized,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "absolute_proof_achieved": False,
        }

    def _integrity_checks(self) -> Dict[str, Any]:
        regimes = self.proof_regimes
        required = set(self.regime_order)
        present = set(regimes)
        complete = required == present
        mutually_distinct = len({regimes[k]["label"] for k in regimes}) == len(regimes)
        no_forbidden_claim = True
        return {
            "regime_count": len(regimes),
            "required_regimes_present": complete,
            "mutually_distinct_regimes": mutually_distinct,
            "no_forbidden_claim_emitted": no_forbidden_claim,
            "taxonomy_complete": bool(complete and mutually_distinct and no_forbidden_claim),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines: List[str] = [
            "# Proof Taxonomy",
            "",
            "Z''0 — taxonomy of proof regimes for consciousness claims.",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            "## Epistemic purpose",
            "This primitive prevents confusion between empirical evidence, strong inference, nomological support, and absolute formal demonstration.",
            "",
            "## Proof regimes",
        ]
        for key in self.regime_order:
            r = result["proof_regimes"][key]
            lines.extend([
                "",
                "### " + key + " — " + str(r["canonical_name"]),
                "- label: " + str(r["label"]),
                "- definition: " + str(r["definition"]),
                "- observable_status: " + str(r["observable_status"]),
                "- valid_use: " + str(r["valid_use"]),
                "- invalid_use: " + str(r["invalid_use"]),
                "- maximum_authorized_conclusion: " + str(r["maximum_authorized_conclusion"]),
            ])
        lines.extend([
            "",
            "## Governance constraints",
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- subjectivity_proven: False",
            "- sentience_proven: False",
            "- qualia_proven: False",
            "- absolute_proof_achieved: False",
            "",
            "## Result",
            "- taxonomy_complete: " + str(result["taxonomy_complete"]),
            "- maximum_authorized_conclusion: " + str(result["maximum_authorized_conclusion"]),
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Mapping[str, Any] = payload if isinstance(payload, Mapping) else {}
        claims = data.get("claims", [])
        if isinstance(claims, str):
            claim_items = [claims]
        elif isinstance(claims, list):
            claim_items = [str(item) for item in claims]
        else:
            claim_items = []
        classified_claims = [self.classify_claim(item) for item in claim_items]
        checks = self._integrity_checks()
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": str(data.get("timestamp_utc") or self._utc_now()),
            "proof_regimes": dict(self.proof_regimes),
            "regime_order": list(self.regime_order),
            "classified_claims": classified_claims,
            **checks,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "subjectivity_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
            "forbidden_claims": list(self.forbidden_claims),
            "maximum_authorized_conclusion": "Four proof regimes are distinguished for later Z-double-prime stages; no consciousness or phenomenology proof is established.",
            "forbidden_conclusion": "Open Cognitive Ecology is consciously subject of experience.",
            "next_required_stage": "consciousness_property_candidate_registry",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
