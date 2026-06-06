from ontology.planning import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    Planning,
)


def test_constants():
    assert PRIMITIVE_NAME == "PLANNING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Planning()
    result = primitive.evaluate()

    assert abs(result["sequence_coherence"] - 0.0) < 1e-12
    assert abs(result["resource_scheduling"] - 0.0) < 1e-12
    assert abs(result["plan_feasibility"] - 0.0) < 1e-12
    assert abs(result["planning_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Planning()
    result = primitive.evaluate(
        actions=[1.0, 1.0, 1.0],
        resources=[1.0, 0.5],
        constraints=[1.0, 1.0],
    )

    assert result["planning_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = Planning()
    result = primitive.evaluate(
        actions=[0.0, 0.0],
        resources=[0.0],
        constraints=[0.0],
    )

    assert abs(result["planning_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = Planning()
    result = primitive.evaluate(
        actions=[10.0, -5.0],
        resources=[2.0],
        constraints=[3.0],
    )

    for key in (
        "sequence_coherence",
        "resource_scheduling",
        "plan_feasibility",
        "planning_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Planning()
    kwargs = {
        "actions": [1.0, 0.5],
        "resources": [1.0],
        "constraints": [1.0],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(stepped["planning_index"] - evaluation["planning_index"]) < 1e-12


def test_validate_matches_evaluate():
    primitive = Planning()
    kwargs = {
        "actions": [1.0, 0.5],
        "resources": [1.0],
        "constraints": [1.0],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert abs(validation["planning_index"] - evaluation["planning_index"]) < 1e-12
