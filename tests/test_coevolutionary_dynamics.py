from ontology.coevolutionary_dynamics import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    CoevolutionaryDynamics,
)


def test_metadata():
    assert PRIMITIVE_NAME == "COEVOLUTIONARY_DYNAMICS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CoevolutionaryDynamics()
    result = primitive.evaluate()

    assert abs(result["coevolutionary_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "isolated"


def test_nominal_case():
    primitive = CoevolutionaryDynamics(
        interaction_intensity=0.8,
        mutual_adaptation_rate=0.6,
        coupling_strength=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["coevolutionary_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "coevolving"


def test_negative_inputs_are_clamped():
    primitive = CoevolutionaryDynamics(
        interaction_intensity=-1.0,
        mutual_adaptation_rate=-2.0,
        coupling_strength=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["coevolutionary_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = CoevolutionaryDynamics(
        interaction_intensity=10.0,
        mutual_adaptation_rate=10.0,
        coupling_strength=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "interaction_intensity",
        "mutual_adaptation_rate",
        "coupling_strength",
        "coevolutionary_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = CoevolutionaryDynamics(
        interaction_intensity=0.4,
        mutual_adaptation_rate=0.5,
        coupling_strength=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "interaction_intensity",
        "mutual_adaptation_rate",
        "coupling_strength",
        "coevolutionary_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = CoevolutionaryDynamics(
        interaction_intensity=0.7,
        mutual_adaptation_rate=0.8,
        coupling_strength=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["coevolutionary_potential"]
            - evaluation["coevolutionary_potential"]
        )
        < 1e-12
    )
