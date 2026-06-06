from ontology.evolutionary_drift import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    EvolutionaryDrift,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EVOLUTIONARY_DRIFT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EvolutionaryDrift()
    result = primitive.evaluate()

    assert abs(result["drift_rate"] - 0.0) < 1e-12
    assert abs(result["evolutionary_distance"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "stable"


def test_nominal_case():
    primitive = EvolutionaryDrift(
        replication_error=0.4,
        stochastic_fluctuation=0.2,
        generational_depth=0.5,
    )
    result = primitive.evaluate()

    expected_drift = 0.3
    expected_distance = 0.15

    assert abs(result["drift_rate"] - expected_drift) < 1e-12
    assert abs(result["evolutionary_distance"] - expected_distance) < 1e-12
    assert result["diagnostics"]["status"] == "drifting"


def test_negative_inputs_are_clamped():
    primitive = EvolutionaryDrift(
        replication_error=-1.0,
        stochastic_fluctuation=-1.0,
        generational_depth=-1.0,
    )
    result = primitive.evaluate()

    assert abs(result["drift_rate"] - 0.0) < 1e-12
    assert abs(result["evolutionary_distance"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = EvolutionaryDrift(
        replication_error=10.0,
        stochastic_fluctuation=10.0,
        generational_depth=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "drift_rate",
        "cumulative_variation",
        "lineage_dispersion",
        "evolutionary_distance",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = EvolutionaryDrift(
        replication_error=0.5,
        stochastic_fluctuation=0.3,
        generational_depth=0.7,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "drift_rate",
        "cumulative_variation",
        "lineage_dispersion",
        "evolutionary_distance",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = EvolutionaryDrift(
        replication_error=0.6,
        stochastic_fluctuation=0.4,
        generational_depth=0.8,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["evolutionary_distance"]
            - evaluation["evolutionary_distance"]
        )
        < 1e-12
    )
