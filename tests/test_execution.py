from ontology.execution import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Execution,
)


def test_constants():
    assert PRIMITIVE_NAME == "EXECUTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Execution()
    result = primitive.evaluate()

    assert abs(result["action_completion"] - 0.0) < 1e-12
    assert abs(result["schedule_adherence"] - 0.0) < 1e-12
    assert abs(result["execution_efficiency"] - 0.0) < 1e-12
    assert abs(result["execution_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Execution()
    result = primitive.evaluate(
        completed_actions=[1.0, 1.0, 0.5],
        schedule_matches=[1.0, 1.0],
        efficiency_signals=[0.75, 1.0],
    )

    assert result["execution_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Execution()
    result = primitive.evaluate(
        completed_actions=[0.0],
        schedule_matches=[0.0],
        efficiency_signals=[0.0],
    )

    assert abs(result["execution_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Execution()
    result = primitive.evaluate(
        completed_actions=[10.0, -5.0],
        schedule_matches=[2.0],
        efficiency_signals=[3.0],
    )

    for key in (
        "action_completion",
        "schedule_adherence",
        "execution_efficiency",
        "execution_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Execution()
    kwargs = {
        "completed_actions": [1.0, 0.5],
        "schedule_matches": [1.0],
        "efficiency_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(stepped["execution_index"] - evaluation["execution_index"]) < 1e-12


def test_validate_matches_evaluate():
    primitive = Execution()
    kwargs = {
        "completed_actions": [1.0, 0.5],
        "schedule_matches": [1.0],
        "efficiency_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(validation["execution_index"] - evaluation["execution_index"]) < 1e-12
