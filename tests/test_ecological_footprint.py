from ontology.ecological_footprint import (
    EcologicalFootprint,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ECOLOGICAL_FOOTPRINT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EcologicalFootprint()
    result = primitive.evaluate({})
    expected = (0.0 + 0.0 + (1.0 - 0.0)) / 3.0
    assert abs(result["ecological_footprint_index"] - expected) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = EcologicalFootprint()
    result = primitive.evaluate(
        {
            "resource_consumption": 0.8,
            "waste_generation": 0.7,
            "biocapacity_ratio": 0.2,
        }
    )
    expected = (0.8 + 0.7 + 0.8) / 3.0
    assert abs(result["ecological_footprint_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "overshoot"


def test_negative_case():
    primitive = EcologicalFootprint()
    result = primitive.evaluate(
        {
            "resource_consumption": 0.1,
            "waste_generation": 0.1,
            "biocapacity_ratio": 0.9,
        }
    )
    assert result["diagnostics"]["status"] == "sustainable"


def test_bounding():
    primitive = EcologicalFootprint()
    result = primitive.evaluate(
        {
            "resource_consumption": 2.0,
            "waste_generation": -1.0,
            "biocapacity_ratio": 5.0,
        }
    )
    assert abs(result["resource_consumption"] - 1.0) < 1e-12
    assert abs(result["waste_generation"] - 0.0) < 1e-12
    assert abs(result["biocapacity_ratio"] - 1.0) < 1e-12
    assert 0.0 <= result["ecological_footprint_index"] <= 1.0


def test_step_consistency():
    primitive = EcologicalFootprint()
    inputs = {
        "resource_consumption": 0.6,
        "waste_generation": 0.6,
        "biocapacity_ratio": 0.4,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = EcologicalFootprint()
    inputs = {
        "resource_consumption": 0.4,
        "waste_generation": 0.5,
        "biocapacity_ratio": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["ecological_footprint_index"]
            - evaluation["ecological_footprint_index"]
        )
        < 1e-12
    )
