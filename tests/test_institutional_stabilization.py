from ontology.institutional_stabilization import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    InstitutionalStabilization,
)


def test_metadata():
    assert PRIMITIVE_NAME == "INSTITUTIONAL_STABILIZATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = InstitutionalStabilization()
    result = primitive.evaluate({})
    assert abs(result["institutional_stabilization_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = InstitutionalStabilization()
    state = {
        "normative_adoption": 0.8,
        "compliance_monitoring": 0.6,
        "sanction_effectiveness": 0.8,
        "structural_durability": 0.7,
    }

    result = primitive.evaluate(state)

    expected_enforcement = 0.7
    expected_index = (0.8 + 0.7 + 0.7) / 3.0

    assert abs(result["norm_internalization"] - 0.8) < 1e-12
    assert abs(result["rule_enforcement"] - expected_enforcement) < 1e-12
    assert abs(result["structural_persistence"] - 0.7) < 1e-12
    assert abs(
        result["institutional_stabilization_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = InstitutionalStabilization()
    state = {
        "normative_adoption": 0.1,
        "compliance_monitoring": 0.0,
        "sanction_effectiveness": 0.0,
        "structural_durability": 0.1,
    }

    result = primitive.evaluate(state)
    assert result["institutional_stabilization_index"] < 0.5


def test_bounding():
    primitive = InstitutionalStabilization()
    state = {
        "normative_adoption": 5.0,
        "compliance_monitoring": -2.0,
        "sanction_effectiveness": 10.0,
        "structural_durability": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "norm_internalization",
        "rule_enforcement",
        "structural_persistence",
        "institutional_stabilization_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = InstitutionalStabilization()
    state = {
        "normative_adoption": 0.7,
        "compliance_monitoring": 0.8,
        "sanction_effectiveness": 0.6,
        "structural_durability": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["institutional_stabilization_index"]
        - step_result["institutional_stabilization_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = InstitutionalStabilization()
    state = {
        "normative_adoption": 0.9,
        "compliance_monitoring": 0.9,
        "sanction_effectiveness": 0.9,
        "structural_durability": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["institutional_stabilization_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
