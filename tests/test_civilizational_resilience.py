from ontology.civilizational_resilience import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    CivilizationalResilience,
)


def test_metadata():
    assert PRIMITIVE_NAME == "CIVILIZATIONAL_RESILIENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CivilizationalResilience()
    result = primitive.evaluate({})
    assert abs(result["civilizational_resilience_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CivilizationalResilience()
    state = {
        "redundancy_level": 0.8,
        "institutional_stability": 0.6,
        "restoration_speed": 0.9,
        "adaptive_capacity": 0.7,
    }

    result = primitive.evaluate(state)

    expected_recovery = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["shock_absorption"] - 0.8) < 1e-12
    assert abs(result["functional_preservation"] - 0.6) < 1e-12
    assert abs(result["recovery_capacity"] - expected_recovery) < 1e-12
    assert abs(
        result["civilizational_resilience_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = CivilizationalResilience()
    state = {
        "redundancy_level": 0.1,
        "institutional_stability": 0.0,
        "restoration_speed": 0.1,
        "adaptive_capacity": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["civilizational_resilience_index"] < 0.5


def test_bounding():
    primitive = CivilizationalResilience()
    state = {
        "redundancy_level": 5.0,
        "institutional_stability": -2.0,
        "restoration_speed": 10.0,
        "adaptive_capacity": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "shock_absorption",
        "functional_preservation",
        "recovery_capacity",
        "civilizational_resilience_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = CivilizationalResilience()
    state = {
        "redundancy_level": 0.7,
        "institutional_stability": 0.8,
        "restoration_speed": 0.6,
        "adaptive_capacity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["civilizational_resilience_index"]
        - step_result["civilizational_resilience_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = CivilizationalResilience()
    state = {
        "redundancy_level": 0.9,
        "institutional_stability": 0.9,
        "restoration_speed": 0.9,
        "adaptive_capacity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["civilizational_resilience_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
