from ontology.world_model import (
    MATURITY_LEVEL,
    PRIMITIVE_NAME,
    WorldModel,
)


def test_constants():
    assert PRIMITIVE_NAME == "WORLD_MODEL"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = WorldModel()
    result = primitive.evaluate()

    assert abs(result["model_coherence"] - 0.0) < 1e-12
    assert abs(result["predictive_accuracy"] - 0.0) < 1e-12
    assert abs(result["simulation_fidelity"] - 0.0) < 1e-12
    assert abs(result["world_model_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = WorldModel()
    result = primitive.evaluate(
        coherence_signals=[1.0, 0.8],
        prediction_signals=[1.0, 0.9],
        simulation_signals=[0.7, 1.0],
    )

    assert result["world_model_index"] > 0.0
    assert result["diagnostics"]["status"] == "nominal"


def test_negative_case():
    primitive = WorldModel()
    result = primitive.evaluate(
        coherence_signals=[0.0],
        prediction_signals=[0.0],
        simulation_signals=[0.0],
    )

    assert abs(result["world_model_index"] - 0.0) < 1e-12


def test_bounded_values():
    primitive = WorldModel()
    result = primitive.evaluate(
        coherence_signals=[10.0, -5.0],
        prediction_signals=[2.0],
        simulation_signals=[3.0],
    )

    for key in (
        "model_coherence",
        "predictive_accuracy",
        "simulation_fidelity",
        "world_model_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = WorldModel()
    kwargs = {
        "coherence_signals": [1.0, 0.5],
        "prediction_signals": [1.0],
        "simulation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert (
        abs(
            stepped["world_model_index"]
            - evaluation["world_model_index"]
        )
        < 1e-12
    )


def test_validate_matches_evaluate():
    primitive = WorldModel()
    kwargs = {
        "coherence_signals": [1.0, 0.5],
        "prediction_signals": [1.0],
        "simulation_signals": [0.75],
    }

    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)

    assert validation["is_valid"] is True
    assert (
        abs(
            validation["world_model_index"]
            - evaluation["world_model_index"]
        )
        < 1e-12
    )
