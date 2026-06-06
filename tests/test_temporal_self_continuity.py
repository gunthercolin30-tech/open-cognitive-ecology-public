from ontology.temporal_self_continuity import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    TemporalSelfContinuity,
)


def test_metadata():
    assert PRIMITIVE_NAME == "TEMPORAL_SELF_CONTINUITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = TemporalSelfContinuity()
    result = primitive.evaluate({})
    assert abs(result["temporal_self_continuity_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = TemporalSelfContinuity()
    state = {
        "autobiographical_memory": 0.8,
        "narrative_coherence": 0.6,
        "episodic_linkage": 0.9,
        "future_simulation": 0.7,
    }
    result = primitive.evaluate(state)

    expected_autobiographical = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(result["autobiographical_coherence"] - expected_autobiographical) < 1e-12
    assert abs(result["memory_linkage"] - 0.9) < 1e-12
    assert abs(result["future_projection"] - 0.7) < 1e-12
    assert abs(result["temporal_self_continuity_index"] - expected_index) < 1e-12


def test_negative_case():
    primitive = TemporalSelfContinuity()
    state = {
        "autobiographical_memory": 0.0,
        "narrative_coherence": 0.1,
        "episodic_linkage": 0.0,
        "future_simulation": 0.0,
    }
    result = primitive.evaluate(state)
    assert result["temporal_self_continuity_index"] < 0.5


def test_bounding():
    primitive = TemporalSelfContinuity()
    state = {
        "autobiographical_memory": 5.0,
        "narrative_coherence": -2.0,
        "episodic_linkage": 10.0,
        "future_simulation": -1.0,
    }
    result = primitive.evaluate(state)

    for key in (
        "autobiographical_coherence",
        "memory_linkage",
        "future_projection",
        "temporal_self_continuity_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = TemporalSelfContinuity()
    state = {
        "autobiographical_memory": 0.5,
        "narrative_coherence": 0.8,
        "episodic_linkage": 0.7,
        "future_simulation": 0.9,
    }
    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["temporal_self_continuity_index"]
        - step_result["temporal_self_continuity_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = TemporalSelfContinuity()
    state = {
        "autobiographical_memory": 0.9,
        "narrative_coherence": 0.9,
        "episodic_linkage": 0.9,
        "future_simulation": 0.9,
    }
    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["temporal_self_continuity_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
