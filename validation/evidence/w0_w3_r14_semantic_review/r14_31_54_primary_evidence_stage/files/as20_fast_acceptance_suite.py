#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_governance_certifier import ConsciousnessGovernanceCertifier

ROOT = Path.home() / "open-cognitive-ecology"


def ready_inputs():
    engine = ConsciousnessGovernanceCertifier()
    return {
        "module_presence": {name: True for name in engine.required_modules},
        "criteria": {name: True for name in engine.certification_criteria},
        "stability_score": 1.0,
        "explanation_score": 1.0,
        "public_dashboard_score": 1.0,
        "prediction_score": 1.0,
        "auditability_score": 1.0,
    }


def main() -> None:
    py_compile.compile(str(ROOT / "ontology" / "consciousness_governance_certifier.py"), cfile="/private/tmp/consciousness_governance_certifier.pyc", doraise=True)
    engine = ConsciousnessGovernanceCertifier()
    result = engine.step(inputs=ready_inputs(), persist=False)
    assert result["primitive"] == "CONSCIOUSNESS_GOVERNANCE_CERTIFIER"
    assert result["step"] == "AS20"
    assert result["status"] == "CONSCIOUSNESS_GOVERNANCE_COMPLETE"
    assert result["consciousness_governance_complete"] is True
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["missing_modules"] == []
    assert result["missing_criteria"] == []
    assert 0.95 <= result["governance_completion_score"] <= 1.0

    degraded_inputs = ready_inputs()
    degraded_inputs["criteria"]["revocation"] = False
    degraded = engine.step(inputs=degraded_inputs, persist=False)
    assert degraded["status"] == "CONSCIOUSNESS_GOVERNANCE_INCOMPLETE"
    assert degraded["consciousness_governance_complete"] is False
    assert "revocation" in degraded["missing_criteria"]

    print("AS20_FAST_ACCEPTANCE_ALL_OK")


if __name__ == "__main__":
    main()
