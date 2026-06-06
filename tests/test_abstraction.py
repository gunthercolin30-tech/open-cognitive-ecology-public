from ontology.abstraction import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Abstraction,
)


def test_constants():
    assert PRIMITIVE_NAME == "ABSTRACTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Abstraction()
    result = primitive.evaluate()

    assert abs(result["invariant_extraction"] - 0.0) < 1e-12
    assert abs(result["complexity_reduction"] - 0.0) < 1e-12
    assert abs(result["representation_stability"] - 0.0) < 1e-12
    assert abs(result["abstraction_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Abstraction()
    result = primitive.evaluate(
        invariants=[1.0, 0.8],
        reductions=[1.0, 0.9],
        representations=[0.7, 1.0],
    )

    assert result["abstraction_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Abstraction()
    result = primitive.evaluate(
        invariants=[0.0],
        reductions=[0.0],
        representations=[0.0],
    )

    assert abs(result["abstraction_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Abstraction()
    result = primitive.evaluate(
        invariants=[10.0, -5.0],
        reductions=[2.0],
        representations=[3.0],
    )

    for key in (
        "invariant_extraction",
        "complexity_reduction",
        "representation_stability",
        "abstraction_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Abstraction()
    kwargs = {
        "invariants": [1.0, 0.5],
        "reductions": [1.0],
        "representations": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["abstraction_index"] - evaluation["abstraction_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Abstraction()
    kwargs = {
        "invariants": [1.0, 0.5],
        "reductions": [1.0],
        "representations": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["abstraction_index"] - evaluation["abstraction_index"]
    ) < 1e-12
