from ontology.computational_irreducibility import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ComputationalIrreducibility,
)


def test_metadata():
    assert PRIMITIVE_NAME == "COMPUTATIONAL_IRREDUCIBILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ComputationalIrreducibility()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    # irreducible_compression = 1.0
    # index = (1 + 0 + 0) / 3 = 1/3
    assert abs(
        result["computational_irreducibility_index"]
        - (1.0 / 3.0)
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = ComputationalIrreducibility()

    result = primitive.evaluate(
        0.2,
        0.8,
        0.9,
    )

    assert 0.0 <= result["predictive_compressibility"] <= 1.0
    assert 0.0 <= result["simulation_necessity"] <= 1.0
    assert 0.0 <= result["forecast_limit"] <= 1.0
    assert (
        0.0
        <= result["computational_irreducibility_index"]
        <= 1.0
    )
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = ComputationalIrreducibility()

    result = primitive.evaluate(
        1.0,
        0.0,
        0.0,
    )

    assert abs(
        result["computational_irreducibility_index"] - 0.0
    ) < 1e-12


def test_bounding():
    primitive = ComputationalIrreducibility()

    result = primitive.evaluate(
        -5.0,
        3.0,
        2.0,
    )

    assert (
        0.0
        <= result["computational_irreducibility_index"]
        <= 1.0
    )


def test_step_consistency():
    primitive = ComputationalIrreducibility()

    a = primitive.evaluate(0.2, 0.8, 0.9)
    b = primitive.step(0.2, 0.8, 0.9)

    assert abs(
        a["computational_irreducibility_index"]
        - b["computational_irreducibility_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ComputationalIrreducibility()

    evaluation = primitive.evaluate(0.2, 0.8, 0.9)
    validation = primitive.validate(0.2, 0.8, 0.9)

    assert abs(
        evaluation["computational_irreducibility_index"]
        - validation["computational_irreducibility_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
