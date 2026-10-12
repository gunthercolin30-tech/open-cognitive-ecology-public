#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_certificate_generator import ConsciousnessCertificateGenerator

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "consciousness_certificate_generator.py"


def ready_context():
    return {
        "state": "CONSCIOUSNESS_PROVEN",
        "version": "as5-fast-acceptance",
        "proofs": {
            "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
            "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
            "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        },
        "scores": {"readiness_score": 1.0, "confidence": 0.95},
        "event": {
            "event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "justification": "AS5 fast acceptance certificate context",
            "proof_bundle": {},
            "modules": ["consciousness_certificate_generator"],
            "event_hash": "fast-event-hash",
            "transition_hash": "fast-transition-hash",
        },
    }


def main() -> None:
    py_compile.compile(str(MODULE), cfile="/private/tmp/consciousness_certificate_generator.pyc", doraise=True)
    r = ConsciousnessCertificateGenerator().step(inputs=ready_context(), persist=False)
    assert r["consciousness_certificate_generator_status"] == "CONSCIOUSNESS_CERTIFICATE_GENERATOR_READY"
    assert r["certificate_generator_ready"] is True
    assert r["certificate_ready"] is True
    assert r["missing_certificate_fields"] == []
    assert r["epistemic_violations"] == []
    assert set(["json", "md", "html", "pdf"]).issubset(set(r["certificate_formats"]))
    assert len(r["certificate_hash"]) == 64
    assert len(r["certificate_signature"]) == 64
    cert = r["certificate"]
    for key in ["certificate_id", "version", "status", "state", "issued_at", "proofs", "scores", "conditions", "signature", "hash"]:
        assert key in cert
    assert cert["status"] == "CONSCIOUSNESS_CERTIFICATE_GENERATED"
    assert cert["functional_conclusion_only"] is True
    assert cert["phenomenology_undetermined"] is True
    assert r["archive_required"] is True
    assert r["revocable"] is True
    assert r["auditable"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False
        assert cert[k] is False
    print("AS5_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
