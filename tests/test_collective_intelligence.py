from ontology.collective_intelligence import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    CollectiveIntelligence,
)


def test_metadata():
    assert PRIMITIVE_NAME == "COLLECTIVE_INTELLIGENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CollectiveIntelligence()
    result = primitive.evaluate({})
    assert abs(result["collective_intelligence_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CollectiveIntelligence()
    state = {
        "communication_efficiency": 0.8,
        "task_coordination": 0.6,
        "role_differentiation": 0.9,
        "collective_performance": 0.7,
    }

    result = primitive.evaluate(state)

    expected_coordination = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(result["coordination_efficiency"] - expected_coordination) < 1e-12
    assert abs(result["functional_specialization"] - 0.9) < 1e-12
    assert abs(result["emergent_problem_solving"] - 0.7) < 1e-12
    assert abs(
        result["collective_intelligence_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = CollectiveIntelligence()
    state = {
        "communication_efficiency": 0.1,
        "task_coordination": 0.0,
        "role_differentiation": 0.1,
        "collective_performance": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["collective_intelligence_index"] < 0.5


def test_bounding():
    primitive = CollectiveIntelligence()
    state = {
        "communication_efficiency": 5.0,
        "task_coordination": -2.0,
        "role_differentiation": 10.0,
        "collective_performance": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "coordination_efficiency",
        "functional_specialization",
        "emergent_problem_solving",
        "collective_intelligence_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = CollectiveIntelligence()
    state = {
        "communication_efficiency": 0.7,
        "task_coordination": 0.8,
        "role_differentiation": 0.6,
        "collective_performance": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["collective_intelligence_index"]
        - step_result["collective_intelligence_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = CollectiveIntelligence()
    state = {
        "communication_efficiency": 0.9,
        "task_coordination": 0.9,
        "role_differentiation": 0.9,
        "collective_performance": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["collective_intelligence_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
