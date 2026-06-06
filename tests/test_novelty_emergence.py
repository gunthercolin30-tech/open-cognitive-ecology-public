from ontology.novelty_emergence import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    NoveltyEmergence,
)


def test_metadata():
    assert PRIMITIVE_NAME == "NOVELTY_EMERGENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = NoveltyEmergence()
    result = primitive.evaluate()

    assert abs(result["novelty_probability"] - 0.0) < 1e-12
    assert abs(result["emergence_intensity"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "static"


def test_nominal_case():
    primitive = NoveltyEmergence(
        recombination_potential=0.8,
        surprise_factor=0.6,
        openness_support=0.4,
    )
    result = primitive.evaluate()

    expected_probability = 0.7
    expected_intensity = 0.55

    assert abs(result["novelty_probability"] - expected_probability) < 1e-12
    assert abs(result["emergence_intensity"] - expected_intensity) < 1e-12
    assert result["diagnostics"]["status"] == "emergent"


def test_negative_inputs_are_clamped():
    primitive = NoveltyEmergence(
        recombination_potential=-1.0,
        surprise_factor=-1.0,
        openness_support=-1.0,
    )
    result = primitive.evaluate()

    assert abs(result["novelty_probability"] - 0.0) < 1e-12
    assert abs(result["emergence_intensity"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = NoveltyEmergence(
        recombination_potential=10.0,
        surprise_factor=10.0,
        openness_support=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "recombination_potential",
        "surprise_factor",
        "novelty_probability",
        "emergence_intensity",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = NoveltyEmergence(
        recombination_potential=0.3,
        surprise_factor=0.5,
        openness_support=0.7,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "recombination_potential",
        "surprise_factor",
        "novelty_probability",
        "emergence_intensity",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = NoveltyEmergence(
        recombination_potential=0.9,
        surprise_factor=0.4,
        openness_support=0.8,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["emergence_intensity"]
            - evaluation["emergence_intensity"]
        )
        < 1e-12
    )
