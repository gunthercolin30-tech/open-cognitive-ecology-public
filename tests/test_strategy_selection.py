"""
Unit tests for STRATEGY_SELECTION.
"""

from ontology.strategy_selection import (
    StrategySelection,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "STRATEGY_SELECTION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = StrategySelection()
    result = primitive.evaluate()
    assert abs(result["strategy_selection_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "STRATEGY_SELECTION"


def test_nominal_case():
    primitive = StrategySelection()
    result = primitive.evaluate(
        prioritization=0.85,
        decision_making=0.80,
        goal_directedness=0.75,
        controllability=0.90,
    )
    assert 0.0 <= result["strategy_selection_index"] <= 1.0
    assert result["strategy_selection_index"] > 0.0


def test_negative_case():
    primitive = StrategySelection()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["strategy_selection_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = StrategySelection()
    result = primitive.evaluate(
        prioritization=2.0,
        decision_making=-1.0,
        goal_directedness=10.0,
        controllability=5.0,
    )
    assert 0.0 <= result["plan_coherence"] <= 1.0
    assert 0.0 <= result["resource_alignment"] <= 1.0
    assert 0.0 <= result["strategy_commitment"] <= 1.0
    assert 0.0 <= result["strategy_selection_index"] <= 1.0


def test_step_consistency():
    primitive = StrategySelection()
    kwargs = dict(
        prioritization=0.7,
        decision_making=0.8,
        goal_directedness=0.6,
        controllability=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(
        evaluated["strategy_selection_index"]
        - stepped["strategy_selection_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = StrategySelection()
    kwargs = dict(
        prioritization=0.7,
        decision_making=0.8,
        goal_directedness=0.6,
        controllability=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (
        evaluated["strategy_selection_index"] > 0.0
    )
    assert abs(
        evaluated["strategy_selection_index"]
        - validated["strategy_selection_index"]
    ) < 1e-12
