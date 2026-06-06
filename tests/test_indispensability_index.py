from ontology.indispensability_index import (
    IndispensabilityIndex,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "INDISPENSABILITY_INDEX"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = IndispensabilityIndex()
    result = primitive.evaluate(
        dependency_level=0.0,
        functional_substitutability=1.0,
        coordination_centrality=0.0,
        removal_impact=0.0,
    )
    assert abs(result["indispensability_index"] - 0.0) < 1e-12
    assert result["critical_status"] is False


def test_nominal_case():
    primitive = IndispensabilityIndex()
    result = primitive.evaluate(
        dependency_level=1.0,
        functional_substitutability=0.0,
        coordination_centrality=1.0,
        removal_impact=1.0,
    )
    assert abs(result["indispensability_index"] - 1.0) < 1e-12
    assert result["critical_status"] is True


def test_negative_case():
    primitive = IndispensabilityIndex()
    result = primitive.evaluate(
        dependency_level=0.1,
        functional_substitutability=0.9,
        coordination_centrality=0.1,
        removal_impact=0.1,
    )
    assert result["critical_status"] is False


def test_bounding():
    primitive = IndispensabilityIndex()
    result = primitive.evaluate(
        dependency_level=2.0,
        functional_substitutability=-1.0,
        coordination_centrality=3.0,
        removal_impact=5.0,
    )
    assert 0.0 <= result["indispensability_index"] <= 1.0
    assert 0.0 <= result["systemic_dependency"] <= 1.0
    assert 0.0 <= result["withdrawal_pressure"] <= 1.0


def test_step_consistency():
    primitive = IndispensabilityIndex()
    kwargs = dict(
        dependency_level=0.6,
        functional_substitutability=0.2,
        coordination_centrality=0.7,
        removal_impact=0.8,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = IndispensabilityIndex()
    kwargs = dict(
        dependency_level=1.0,
        functional_substitutability=0.0,
        coordination_centrality=1.0,
        removal_impact=1.0,
    )
    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)
    assert validation["valid"] == evaluation["critical_status"]
