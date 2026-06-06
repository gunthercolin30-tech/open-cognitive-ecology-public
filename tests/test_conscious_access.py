from ontology.conscious_access import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    ConsciousAccess,
)


def test_constants():
    assert PRIMITIVE_NAME == "CONSCIOUS_ACCESS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ConsciousAccess()
    result = primitive.evaluate()

    assert abs(result["global_availability"] - 0.0) < 1e-12
    assert abs(result["broadcast_coherence"] - 0.0) < 1e-12
    assert abs(result["access_stability"] - 0.0) < 1e-12
    assert abs(result["conscious_access_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = ConsciousAccess()
    result = primitive.evaluate(
        availability_signals=[1.0, 0.8],
        coherence_signals=[1.0, 0.9],
        stability_signals=[0.7, 1.0],
    )

    assert result["conscious_access_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = ConsciousAccess()
    result = primitive.evaluate(
        availability_signals=[0.0],
        coherence_signals=[0.0],
        stability_signals=[0.0],
    )

    assert abs(result["conscious_access_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = ConsciousAccess()
    result = primitive.evaluate(
        availability_signals=[10.0, -5.0],
        coherence_signals=[2.0],
        stability_signals=[3.0],
    )

    for key in (
        "global_availability",
        "broadcast_coherence",
        "access_stability",
        "conscious_access_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = ConsciousAccess()
    kwargs = {
        "availability_signals": [1.0, 0.5],
        "coherence_signals": [1.0],
        "stability_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["conscious_access_index"]
        - evaluation["conscious_access_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = ConsciousAccess()
    kwargs = {
        "availability_signals": [1.0, 0.5],
        "coherence_signals": [1.0],
        "stability_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["conscious_access_index"]
        - evaluation["conscious_access_index"]
    ) < 1e-12
