from ontology.flourishing import (
    Flourishing,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "FLOURISHING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Flourishing()
    result = primitive.evaluate({})
    assert abs(result["flourishing_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = Flourishing()
    result = primitive.evaluate(
        {
            "well_being": 0.8,
            "capability_realization": 0.7,
            "systemic_harmony": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["flourishing_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "flourishing"


def test_negative_case():
    primitive = Flourishing()
    result = primitive.evaluate(
        {
            "well_being": 0.1,
            "capability_realization": 0.2,
            "systemic_harmony": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "constrained"


def test_bounding():
    primitive = Flourishing()
    result = primitive.evaluate(
        {
            "well_being": 2.0,
            "capability_realization": -1.0,
            "systemic_harmony": 5.0,
        }
    )
    assert abs(result["well_being"] - 1.0) < 1e-12
    assert abs(result["capability_realization"] - 0.0) < 1e-12
    assert abs(result["systemic_harmony"] - 1.0) < 1e-12
    assert 0.0 <= result["flourishing_index"] <= 1.0


def test_step_consistency():
    primitive = Flourishing()
    inputs = {
        "well_being": 0.6,
        "capability_realization": 0.6,
        "systemic_harmony": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = Flourishing()
    inputs = {
        "well_being": 0.4,
        "capability_realization": 0.5,
        "systemic_harmony": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["flourishing_index"]
            - evaluation["flourishing_index"]
        )
        < 1e-12
    )
