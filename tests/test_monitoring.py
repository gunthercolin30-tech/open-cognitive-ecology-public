from ontology.monitoring import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Monitoring,
)


def test_constants():
    assert PRIMITIVE_NAME == "MONITORING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Monitoring()
    result = primitive.evaluate()

    assert abs(result["state_tracking"] - 0.0) < 1e-12
    assert abs(result["deviation_detection"] - 0.0) < 1e-12
    assert abs(result["signal_reliability"] - 0.0) < 1e-12
    assert abs(result["monitoring_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Monitoring()
    result = primitive.evaluate(
        observed_states=[1.0, 0.8],
        deviations=[1.0, 1.0],
        signal_quality=[0.9, 1.0],
    )

    assert result["monitoring_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Monitoring()
    result = primitive.evaluate(
        observed_states=[0.0],
        deviations=[0.0],
        signal_quality=[0.0],
    )

    assert abs(result["monitoring_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Monitoring()
    result = primitive.evaluate(
        observed_states=[10.0, -5.0],
        deviations=[2.0],
        signal_quality=[3.0],
    )

    for key in (
        "state_tracking",
        "deviation_detection",
        "signal_reliability",
        "monitoring_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Monitoring()
    kwargs = {
        "observed_states": [1.0, 0.5],
        "deviations": [1.0],
        "signal_quality": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(stepped["monitoring_index"] - evaluation["monitoring_index"]) < 1e-12


def test_validate_matches_evaluate():
    primitive = Monitoring()
    kwargs = {
        "observed_states": [1.0, 0.5],
        "deviations": [1.0],
        "signal_quality": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(validation["monitoring_index"] - evaluation["monitoring_index"]) < 1e-12
