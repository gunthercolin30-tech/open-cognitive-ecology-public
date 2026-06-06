from ontology.stewardship import (
    Stewardship,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "STEWARDSHIP"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Stewardship()
    result = primitive.evaluate({})
    assert abs(result["stewardship_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = Stewardship()
    result = primitive.evaluate(
        {
            "responsibility_commitment": 0.8,
            "regenerative_care": 0.7,
            "intergenerational_orientation": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["stewardship_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "stewardship"


def test_negative_case():
    primitive = Stewardship()
    result = primitive.evaluate(
        {
            "responsibility_commitment": 0.1,
            "regenerative_care": 0.2,
            "intergenerational_orientation": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "neglect"


def test_bounding():
    primitive = Stewardship()
    result = primitive.evaluate(
        {
            "responsibility_commitment": 2.0,
            "regenerative_care": -1.0,
            "intergenerational_orientation": 5.0,
        }
    )
    assert abs(result["responsibility_commitment"] - 1.0) < 1e-12
    assert abs(result["regenerative_care"] - 0.0) < 1e-12
    assert abs(
        result["intergenerational_orientation"] - 1.0
    ) < 1e-12
    assert 0.0 <= result["stewardship_index"] <= 1.0


def test_step_consistency():
    primitive = Stewardship()
    inputs = {
        "responsibility_commitment": 0.6,
        "regenerative_care": 0.6,
        "intergenerational_orientation": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = Stewardship()
    inputs = {
        "responsibility_commitment": 0.4,
        "regenerative_care": 0.5,
        "intergenerational_orientation": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["stewardship_index"]
            - evaluation["stewardship_index"]
        )
        < 1e-12
    )
