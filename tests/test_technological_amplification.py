from ontology.technological_amplification import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    TechnologicalAmplification,
)


def test_metadata():
    assert PRIMITIVE_NAME == "TECHNOLOGICAL_AMPLIFICATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = TechnologicalAmplification()
    result = primitive.evaluate({})
    assert abs(result["technological_amplification_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = TechnologicalAmplification()
    state = {
        "interface_fluency": 0.8,
        "automation_support": 0.6,
        "capability_gain": 0.9,
        "throughput_multiplier": 0.7,
    }

    result = primitive.evaluate(state)

    expected_integration = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(result["tool_integration"] - expected_integration) < 1e-12
    assert abs(result["capability_extension"] - 0.9) < 1e-12
    assert abs(result["performance_scaling"] - 0.7) < 1e-12
    assert abs(
        result["technological_amplification_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = TechnologicalAmplification()
    state = {
        "interface_fluency": 0.1,
        "automation_support": 0.0,
        "capability_gain": 0.1,
        "throughput_multiplier": 0.0,
    }
    result = primitive.evaluate(state)
    assert result["technological_amplification_index"] < 0.5


def test_bounding():
    primitive = TechnologicalAmplification()
    state = {
        "interface_fluency": 5.0,
        "automation_support": -2.0,
        "capability_gain": 10.0,
        "throughput_multiplier": -1.0,
    }
    result = primitive.evaluate(state)

    for key in (
        "tool_integration",
        "capability_extension",
        "performance_scaling",
        "technological_amplification_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = TechnologicalAmplification()
    state = {
        "interface_fluency": 0.7,
        "automation_support": 0.8,
        "capability_gain": 0.6,
        "throughput_multiplier": 0.9,
    }
    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["technological_amplification_index"]
        - step_result["technological_amplification_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = TechnologicalAmplification()
    state = {
        "interface_fluency": 0.9,
        "automation_support": 0.9,
        "capability_gain": 0.9,
        "throughput_multiplier": 0.9,
    }
    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["technological_amplification_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
