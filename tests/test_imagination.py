from ontology.imagination import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Imagination,
)


def test_constants():
    assert PRIMITIVE_NAME == "IMAGINATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Imagination()
    result = primitive.evaluate()

    assert abs(
        result["novel_configuration_generation"] - 0.0
    ) < 1e-12
    assert abs(result["structural_coherence"] - 0.0) < 1e-12
    assert abs(result["exploratory_diversity"] - 0.0) < 1e-12
    assert abs(result["imagination_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Imagination()
    result = primitive.evaluate(
        novel_configurations=[1.0, 0.8],
        coherence_signals=[1.0, 0.9],
        diversity_signals=[0.7, 1.0],
    )

    assert result["imagination_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Imagination()
    result = primitive.evaluate(
        novel_configurations=[0.0],
        coherence_signals=[0.0],
        diversity_signals=[0.0],
    )

    assert abs(result["imagination_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Imagination()
    result = primitive.evaluate(
        novel_configurations=[10.0, -5.0],
        coherence_signals=[2.0],
        diversity_signals=[3.0],
    )

    for key in (
        "novel_configuration_generation",
        "structural_coherence",
        "exploratory_diversity",
        "imagination_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Imagination()
    kwargs = {
        "novel_configurations": [1.0, 0.5],
        "coherence_signals": [1.0],
        "diversity_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(
        stepped["imagination_index"]
        - evaluation["imagination_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Imagination()
    kwargs = {
        "novel_configurations": [1.0, 0.5],
        "coherence_signals": [1.0],
        "diversity_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(
        validation["imagination_index"]
        - evaluation["imagination_index"]
    ) < 1e-12
