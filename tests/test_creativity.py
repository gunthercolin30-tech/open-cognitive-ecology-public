from ontology.creativity import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Creativity,
)


def test_constants():
    assert PRIMITIVE_NAME == "CREATIVITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Creativity()
    result = primitive.evaluate()

    assert abs(result["novelty"] - 0.0) < 1e-12
    assert abs(result["usefulness"] - 0.0) < 1e-12
    assert abs(result["structural_originality"] - 0.0) < 1e-12
    assert abs(result["creativity_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Creativity()
    result = primitive.evaluate(
        novelty_signals=[1.0, 0.8],
        usefulness_signals=[1.0, 0.9],
        originality_signals=[0.7, 1.0],
    )

    assert result["creativity_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Creativity()
    result = primitive.evaluate(
        novelty_signals=[0.0],
        usefulness_signals=[0.0],
        originality_signals=[0.0],
    )

    assert abs(result["creativity_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Creativity()
    result = primitive.evaluate(
        novelty_signals=[10.0, -5.0],
        usefulness_signals=[2.0],
        originality_signals=[3.0],
    )

    for key in (
        "novelty",
        "usefulness",
        "structural_originality",
        "creativity_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Creativity()
    kwargs = {
        "novelty_signals": [1.0, 0.5],
        "usefulness_signals": [1.0],
        "originality_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["creativity_index"]
        - evaluation["creativity_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Creativity()
    kwargs = {
        "novelty_signals": [1.0, 0.5],
        "usefulness_signals": [1.0],
        "originality_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["creativity_index"]
        - evaluation["creativity_index"]
    ) < 1e-12
