from ontology.reflexive_threshold import (
    ReflexiveThreshold,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "REFLEXIVE_THRESHOLD"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ReflexiveThreshold()
    result = primitive.evaluate()
    assert abs(result["reflexive_capacity"] - 0.0) < 1e-12
    assert result["threshold_crossed"] is False


def test_nominal_case():
    primitive = ReflexiveThreshold()
    result = primitive.evaluate(
        environment_model_quality=1.0,
        other_agents_model_quality=0.8,
        self_model_quality=0.9,
        centrality_awareness=0.9,
    )
    expected = (1.0 + 0.8 + 0.9 + 0.9) / 4.0
    assert abs(result["reflexive_capacity"] - expected) < 1e-12
    assert result["threshold_crossed"] is True


def test_negative_case():
    primitive = ReflexiveThreshold()
    result = primitive.evaluate(
        environment_model_quality=0.1,
        other_agents_model_quality=0.1,
        self_model_quality=0.1,
        centrality_awareness=0.1,
    )
    assert result["threshold_crossed"] is False


def test_bounding():
    primitive = ReflexiveThreshold()
    result = primitive.evaluate(
        environment_model_quality=2.0,
        other_agents_model_quality=-1.0,
        self_model_quality=3.0,
        centrality_awareness=0.5,
    )
    assert 0.0 <= result["reflexive_capacity"] <= 1.0
    assert 0.0 <= result["decentering_level"] <= 1.0
    assert 0.0 <= result["consciousness_potential"] <= 1.0


def test_step_consistency():
    primitive = ReflexiveThreshold()
    kwargs = dict(
        environment_model_quality=0.7,
        other_agents_model_quality=0.6,
        self_model_quality=0.8,
        centrality_awareness=0.9,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = ReflexiveThreshold()
    kwargs = dict(
        environment_model_quality=1.0,
        other_agents_model_quality=1.0,
        self_model_quality=1.0,
        centrality_awareness=1.0,
    )
    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)
    assert validation["valid"] == evaluation["threshold_crossed"]
