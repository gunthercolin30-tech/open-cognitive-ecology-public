from ontology.existential_risk_management import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ExistentialRiskManagement,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EXISTENTIAL_RISK_MANAGEMENT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ExistentialRiskManagement()
    result = primitive.evaluate({})
    assert abs(
        result["existential_risk_management_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = ExistentialRiskManagement()
    state = {
        "monitoring_coverage": 0.8,
        "forecasting_accuracy": 0.6,
        "mitigation_readiness": 0.9,
        "coordination_capacity": 0.7,
    }

    result = primitive.evaluate(state)

    expected_coordination = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["threat_detection"] - 0.8) < 1e-12
    assert abs(result["risk_assessment"] - 0.6) < 1e-12
    assert abs(
        result["preventive_coordination"] - expected_coordination
    ) < 1e-12
    assert abs(
        result["existential_risk_management_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = ExistentialRiskManagement()
    state = {
        "monitoring_coverage": 0.1,
        "forecasting_accuracy": 0.0,
        "mitigation_readiness": 0.1,
        "coordination_capacity": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["existential_risk_management_index"] < 0.5


def test_bounding():
    primitive = ExistentialRiskManagement()
    state = {
        "monitoring_coverage": 5.0,
        "forecasting_accuracy": -2.0,
        "mitigation_readiness": 10.0,
        "coordination_capacity": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "threat_detection",
        "risk_assessment",
        "preventive_coordination",
        "existential_risk_management_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = ExistentialRiskManagement()
    state = {
        "monitoring_coverage": 0.7,
        "forecasting_accuracy": 0.8,
        "mitigation_readiness": 0.6,
        "coordination_capacity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["existential_risk_management_index"]
        - step_result["existential_risk_management_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ExistentialRiskManagement()
    state = {
        "monitoring_coverage": 0.9,
        "forecasting_accuracy": 0.9,
        "mitigation_readiness": 0.9,
        "coordination_capacity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["existential_risk_management_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
