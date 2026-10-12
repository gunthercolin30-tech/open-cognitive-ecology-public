#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_governance_certifier import ConsciousnessGovernanceCertifier


def ready_or_synthetic_context():
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
    result = ConsciousnessGovernanceCertifier().step(inputs=ready_or_synthetic_context(), persist=False)
    assert result["public_schema_version"] == "AS20.v1"
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
    print("AS20_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
