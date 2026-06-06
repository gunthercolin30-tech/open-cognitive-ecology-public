from ontology.knowledge_accumulation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    KnowledgeAccumulation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "KNOWLEDGE_ACCUMULATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = KnowledgeAccumulation()
    result = primitive.evaluate({})
    assert abs(result["knowledge_accumulation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = KnowledgeAccumulation()
    state = {
        "discovery_rate": 0.8,
        "preservation_quality": 0.6,
        "synthesis_capacity": 0.9,
        "interoperability": 0.7,
    }

    result = primitive.evaluate(state)

    expected_integration = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["knowledge_growth"] - 0.8) < 1e-12
    assert abs(result["retention_efficiency"] - 0.6) < 1e-12
    assert abs(result["integration_capacity"] - expected_integration) < 1e-12
    assert abs(
        result["knowledge_accumulation_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = KnowledgeAccumulation()
    state = {
        "discovery_rate": 0.1,
        "preservation_quality": 0.0,
        "synthesis_capacity": 0.1,
        "interoperability": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["knowledge_accumulation_index"] < 0.5


def test_bounding():
    primitive = KnowledgeAccumulation()
    state = {
        "discovery_rate": 5.0,
        "preservation_quality": -2.0,
        "synthesis_capacity": 10.0,
        "interoperability": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "knowledge_growth",
        "retention_efficiency",
        "integration_capacity",
        "knowledge_accumulation_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = KnowledgeAccumulation()
    state = {
        "discovery_rate": 0.7,
        "preservation_quality": 0.8,
        "synthesis_capacity": 0.6,
        "interoperability": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["knowledge_accumulation_index"]
        - step_result["knowledge_accumulation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = KnowledgeAccumulation()
    state = {
        "discovery_rate": 0.9,
        "preservation_quality": 0.9,
        "synthesis_capacity": 0.9,
        "interoperability": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["knowledge_accumulation_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
