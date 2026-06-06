from ontology.earth_system_stability import (
    EarthSystemStability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "EARTH_SYSTEM_STABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EarthSystemStability()
    result = primitive.evaluate({})
    assert abs(result["earth_system_stability_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = EarthSystemStability()
    result = primitive.evaluate(
        {
            "boundary_integrity": 0.8,
            "biosphere_integrity": 0.7,
            "climate_regulation": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(result["earth_system_stability_index"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "stable"


def test_negative_case():
    primitive = EarthSystemStability()
    result = primitive.evaluate(
        {
            "boundary_integrity": 0.1,
            "biosphere_integrity": 0.2,
            "climate_regulation": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "destabilized"


def test_bounding():
    primitive = EarthSystemStability()
    result = primitive.evaluate(
        {
            "boundary_integrity": 2.0,
            "biosphere_integrity": -1.0,
            "climate_regulation": 5.0,
        }
    )
    assert abs(result["boundary_integrity"] - 1.0) < 1e-12
    assert abs(result["biosphere_integrity"] - 0.0) < 1e-12
    assert abs(result["climate_regulation"] - 1.0) < 1e-12
    assert 0.0 <= result["earth_system_stability_index"] <= 1.0


def test_step_consistency():
    primitive = EarthSystemStability()
    inputs = {
        "boundary_integrity": 0.6,
        "biosphere_integrity": 0.6,
        "climate_regulation": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = EarthSystemStability()
    inputs = {
        "boundary_integrity": 0.4,
        "biosphere_integrity": 0.5,
        "climate_regulation": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["earth_system_stability_index"]
            - evaluation["earth_system_stability_index"]
        )
        < 1e-12
    )
