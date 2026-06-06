
from ontology.sustainability import (
    Sustainability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "SUSTAINABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Sustainability()
    result = primitive.evaluate({})
    assert abs(result["sustainability_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = Sustainability()
    result = primitive.evaluate(
        {
            "ecological_balance": 0.8,
            "resource_regeneration": 0.7,
            "long_term_viability": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["sustainability_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "sustainable"


def test_negative_case():
    primitive = Sustainability()
    result = primitive.evaluate(
        {
            "ecological_balance": 0.1,
            "resource_regeneration": 0.2,
            "long_term_viability": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "unsustainable"


def test_bounding():
    primitive = Sustainability()
    result = primitive.evaluate(
        {
            "ecological_balance": 2.0,
            "resource_regeneration": -1.0,
            "long_term_viability": 5.0,
        }
    )
    assert abs(result["ecological_balance"] - 1.0) < 1e-12
    assert abs(result["resource_regeneration"] - 0.0) < 1e-12
    assert abs(result["long_term_viability"] - 1.0) < 1e-12
    assert 0.0 <= result["sustainability_index"] <= 1.0


def test_step_consistency():
    primitive = Sustainability()
    inputs = {
        "ecological_balance": 0.6,
        "resource_regeneration": 0.6,
        "long_term_viability": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = Sustainability()
    inputs = {
        "ecological_balance": 0.4,
        "resource_regeneration": 0.5,
        "long_term_viability": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["sustainability_index"]
            - evaluation["sustainability_index"]
        )
        < 1e-12
    )
