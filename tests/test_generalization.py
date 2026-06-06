from ontology.generalization import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Generalization,
)


def test_constants():
    assert PRIMITIVE_NAME == "GENERALIZATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Generalization()
    result = primitive.evaluate()

    assert abs(result["pattern_abstraction"] - 0.0) < 1e-12
    assert abs(result["transfer_effectiveness"] - 0.0) < 1e-12
    assert abs(result["novel_context_adaptation"] - 0.0) < 1e-12
    assert abs(result["generalization_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Generalization()
    result = primitive.evaluate(
        abstractions=[1.0, 0.8],
        transfers=[1.0, 0.9],
        novel_adaptations=[0.7, 1.0],
    )

    assert result["generalization_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Generalization()
    result = primitive.evaluate(
        abstractions=[0.0],
        transfers=[0.0],
        novel_adaptations=[0.0],
    )

    assert abs(result["generalization_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Generalization()
    result = primitive.evaluate(
        abstractions=[10.0, -5.0],
        transfers=[2.0],
        novel_adaptations=[3.0],
    )

    for key in (
        "pattern_abstraction",
        "transfer_effectiveness",
        "novel_context_adaptation",
        "generalization_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Generalization()
    kwargs = {
        "abstractions": [1.0, 0.5],
        "transfers": [1.0],
        "novel_adaptations": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["generalization_index"]
            - evaluation["generalization_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = Generalization()
    kwargs = {
        "abstractions": [1.0, 0.5],
        "transfers": [1.0],
        "novel_adaptations": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["generalization_index"]
            - evaluation["generalization_index"]
        )
        < 1e-12
    )
