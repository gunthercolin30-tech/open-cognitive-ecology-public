from ontology.planetary_boundaries import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    PlanetaryBoundaries,
)


def test_metadata():
    assert PRIMITIVE_NAME == "PLANETARY_BOUNDARIES"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = PlanetaryBoundaries()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    # safe_pressure = 1.0, boundary_integrity = 0.0, safe_risk = 1.0
    # index = (1 + 0 + 1) / 3 = 2/3
    assert abs(
        result["planetary_boundaries_index"] - (2.0 / 3.0)
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = PlanetaryBoundaries()

    result = primitive.evaluate(
        0.2,
        0.8,
        0.1,
    )

    assert 0.0 <= result["ecological_pressure"] <= 1.0
    assert 0.0 <= result["boundary_integrity"] <= 1.0
    assert 0.0 <= result["overshoot_risk"] <= 1.0
    assert 0.0 <= result["planetary_boundaries_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = PlanetaryBoundaries()

    result = primitive.evaluate(
        1.0,
        0.0,
        1.0,
    )

    assert abs(result["planetary_boundaries_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = PlanetaryBoundaries()

    result = primitive.evaluate(
        -5.0,
        3.0,
        2.0,
    )

    assert 0.0 <= result["planetary_boundaries_index"] <= 1.0


def test_step_consistency():
    primitive = PlanetaryBoundaries()

    a = primitive.evaluate(0.2, 0.8, 0.1)
    b = primitive.step(0.2, 0.8, 0.1)

    assert abs(
        a["planetary_boundaries_index"]
        - b["planetary_boundaries_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = PlanetaryBoundaries()

    evaluation = primitive.evaluate(0.2, 0.8, 0.1)
    validation = primitive.validate(0.2, 0.8, 0.1)

    assert abs(
        evaluation["planetary_boundaries_index"]
        - validation["planetary_boundaries_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
