from ontology.insight import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Insight,
)


def test_constants():
    assert PRIMITIVE_NAME == "INSIGHT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Insight()
    result = primitive.evaluate()

    assert abs(result["restructuring_intensity"] - 0.0) < 1e-12
    assert abs(result["solution_compactness"] - 0.0) < 1e-12
    assert abs(result["understanding_gain"] - 0.0) < 1e-12
    assert abs(result["insight_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Insight()
    result = primitive.evaluate(
        restructuring_signals=[1.0, 0.8],
        compactness_signals=[1.0, 0.9],
        understanding_signals=[0.7, 1.0],
    )

    assert result["insight_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Insight()
    result = primitive.evaluate(
        restructuring_signals=[0.0],
        compactness_signals=[0.0],
        understanding_signals=[0.0],
    )

    assert abs(result["insight_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Insight()
    result = primitive.evaluate(
        restructuring_signals=[10.0, -5.0],
        compactness_signals=[2.0],
        understanding_signals=[3.0],
    )

    for key in (
        "restructuring_intensity",
        "solution_compactness",
        "understanding_gain",
        "insight_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Insight()
    kwargs = {
        "restructuring_signals": [1.0, 0.5],
        "compactness_signals": [1.0],
        "understanding_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["insight_index"]
        - evaluation["insight_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Insight()
    kwargs = {
        "restructuring_signals": [1.0, 0.5],
        "compactness_signals": [1.0],
        "understanding_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["insight_index"]
        - evaluation["insight_index"]
    ) < 1e-12
