from ontology.ecological_niche_construction import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    EcologicalNicheConstruction,
)


def test_metadata():
    assert PRIMITIVE_NAME == "ECOLOGICAL_NICHE_CONSTRUCTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EcologicalNicheConstruction()
    result = primitive.evaluate()

    assert abs(result["construction_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "passive"


def test_nominal_case():
    primitive = EcologicalNicheConstruction(
        environment_modification=0.8,
        feedback_strength=0.6,
        niche_stability=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["construction_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "constructive"


def test_negative_inputs_are_clamped():
    primitive = EcologicalNicheConstruction(
        environment_modification=-1.0,
        feedback_strength=-2.0,
        niche_stability=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["construction_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = EcologicalNicheConstruction(
        environment_modification=10.0,
        feedback_strength=10.0,
        niche_stability=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "environment_modification",
        "feedback_strength",
        "niche_stability",
        "construction_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = EcologicalNicheConstruction(
        environment_modification=0.4,
        feedback_strength=0.5,
        niche_stability=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "environment_modification",
        "feedback_strength",
        "niche_stability",
        "construction_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = EcologicalNicheConstruction(
        environment_modification=0.7,
        feedback_strength=0.8,
        niche_stability=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["construction_potential"]
            - evaluation["construction_potential"]
        )
        < 1e-12
    )
