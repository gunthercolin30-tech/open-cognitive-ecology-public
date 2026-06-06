from ontology.existential_wisdom import (
    ExistentialWisdom,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "EXISTENTIAL_WISDOM"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ExistentialWisdom()
    result = primitive.evaluate({})
    assert abs(
        result["existential_wisdom_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = ExistentialWisdom()
    result = primitive.evaluate(
        {
            "ontological_discernment": 0.8,
            "continuity_preservation": 0.7,
            "openness_commitment": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(
        result["existential_wisdom_index"] - expected
    ) < 1e-12
    assert (
        result["diagnostics"]["status"]
        == "existentially_wise"
    )


def test_negative_case():
    primitive = ExistentialWisdom()
    result = primitive.evaluate(
        {
            "ontological_discernment": 0.1,
            "continuity_preservation": 0.2,
            "openness_commitment": 0.1,
        }
    )
    assert (
        result["diagnostics"]["status"]
        == "ontologically_myopic"
    )


def test_bounding():
    primitive = ExistentialWisdom()
    result = primitive.evaluate(
        {
            "ontological_discernment": 2.0,
            "continuity_preservation": -1.0,
            "openness_commitment": 5.0,
        }
    )
    assert abs(result["ontological_discernment"] - 1.0) < 1e-12
    assert abs(result["continuity_preservation"] - 0.0) < 1e-12
    assert abs(result["openness_commitment"] - 1.0) < 1e-12
    assert 0.0 <= result["existential_wisdom_index"] <= 1.0


def test_step_consistency():
    primitive = ExistentialWisdom()
    inputs = {
        "ontological_discernment": 0.6,
        "continuity_preservation": 0.6,
        "openness_commitment": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = ExistentialWisdom()
    inputs = {
        "ontological_discernment": 0.4,
        "continuity_preservation": 0.5,
        "openness_commitment": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["existential_wisdom_index"]
            - evaluation["existential_wisdom_index"]
        )
        < 1e-12
    )
