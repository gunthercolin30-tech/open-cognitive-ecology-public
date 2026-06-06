from ontology.concept_formation import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    ConceptFormation,
)


def test_constants():
    assert PRIMITIVE_NAME == "CONCEPT_FORMATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ConceptFormation()
    result = primitive.evaluate()

    assert abs(result["concept_coherence"] - 0.0) < 1e-12
    assert abs(result["boundary_definition"] - 0.0) < 1e-12
    assert abs(result["reusability"] - 0.0) < 1e-12
    assert abs(result["concept_formation_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = ConceptFormation()
    result = primitive.evaluate(
        coherence_signals=[1.0, 0.8],
        boundary_signals=[1.0, 0.9],
        reuse_signals=[0.7, 1.0],
    )

    assert result["concept_formation_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = ConceptFormation()
    result = primitive.evaluate(
        coherence_signals=[0.0],
        boundary_signals=[0.0],
        reuse_signals=[0.0],
    )

    assert abs(result["concept_formation_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = ConceptFormation()
    result = primitive.evaluate(
        coherence_signals=[10.0, -5.0],
        boundary_signals=[2.0],
        reuse_signals=[3.0],
    )

    for key in (
        "concept_coherence",
        "boundary_definition",
        "reusability",
        "concept_formation_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = ConceptFormation()
    kwargs = {
        "coherence_signals": [1.0, 0.5],
        "boundary_signals": [1.0],
        "reuse_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["concept_formation_index"]
            - evaluation["concept_formation_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = ConceptFormation()
    kwargs = {
        "coherence_signals": [1.0, 0.5],
        "boundary_signals": [1.0],
        "reuse_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["concept_formation_index"]
            - evaluation["concept_formation_index"]
        )
        < 1e-12
    )
