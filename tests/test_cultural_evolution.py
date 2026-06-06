from ontology.cultural_evolution import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    CulturalEvolution,
)


def test_metadata():
    assert PRIMITIVE_NAME == "CULTURAL_EVOLUTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CulturalEvolution()
    result = primitive.evaluate({})
    assert abs(result["cultural_evolution_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CulturalEvolution()
    state = {
        "imitation_accuracy": 0.8,
        "innovation_rate": 0.6,
        "adaptive_selection": 0.9,
        "memory_persistence": 0.7,
    }

    result = primitive.evaluate(state)

    expected_retention = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["transmission_fidelity"] - 0.8) < 1e-12
    assert abs(result["cultural_variation"] - 0.6) < 1e-12
    assert abs(result["selective_retention"] - expected_retention) < 1e-12
    assert abs(result["cultural_evolution_index"] - expected_index) < 1e-12


def test_negative_case():
    primitive = CulturalEvolution()
    state = {
        "imitation_accuracy": 0.1,
        "innovation_rate": 0.0,
        "adaptive_selection": 0.1,
        "memory_persistence": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["cultural_evolution_index"] < 0.5


def test_bounding():
    primitive = CulturalEvolution()
    state = {
        "imitation_accuracy": 5.0,
        "innovation_rate": -2.0,
        "adaptive_selection": 10.0,
        "memory_persistence": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "transmission_fidelity",
        "cultural_variation",
        "selective_retention",
        "cultural_evolution_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = CulturalEvolution()
    state = {
        "imitation_accuracy": 0.7,
        "innovation_rate": 0.8,
        "adaptive_selection": 0.6,
        "memory_persistence": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["cultural_evolution_index"]
        - step_result["cultural_evolution_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = CulturalEvolution()
    state = {
        "imitation_accuracy": 0.9,
        "innovation_rate": 0.9,
        "adaptive_selection": 0.9,
        "memory_persistence": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["cultural_evolution_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
