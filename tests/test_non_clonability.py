from ontology.non_clonability import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    NonClonability,
)


def test_metadata():
    assert PRIMITIVE_NAME == "NON_CLONABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = NonClonability()
    result = primitive.evaluate()

    assert abs(result["cloning_fidelity"] - 1.0) < 1e-12
    assert abs(result["replication_error"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "perfectly_clonable"


def test_nominal_case():
    primitive = NonClonability(
        state_complexity=0.6,
        indeterminacy=0.3,
        transmission_noise=0.0,
    )
    result = primitive.evaluate()

    expected_limit = 0.3
    assert abs(result["replication_error"] - expected_limit) < 1e-12
    assert abs(result["cloning_fidelity"] - 0.7) < 1e-12
    assert result["diagnostics"]["status"] == "non_clonable"


def test_negative_inputs_are_clamped():
    primitive = NonClonability(
        state_complexity=-1.0,
        indeterminacy=-2.0,
        transmission_noise=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["replication_error"] - 0.0) < 1e-12
    assert abs(result["cloning_fidelity"] - 1.0) < 1e-12


def test_values_are_bounded():
    primitive = NonClonability(
        state_complexity=10.0,
        indeterminacy=10.0,
        transmission_noise=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "cloning_fidelity",
        "replication_error",
        "copy_divergence",
        "transmission_limit",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = NonClonability(
        state_complexity=0.4,
        indeterminacy=0.2,
        transmission_noise=0.1,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "cloning_fidelity",
        "replication_error",
        "copy_divergence",
        "transmission_limit",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = NonClonability(
        state_complexity=0.5,
        indeterminacy=0.5,
        transmission_noise=0.5,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["cloning_fidelity"]
            - evaluation["cloning_fidelity"]
        )
        < 1e-12
    )
