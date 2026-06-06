"""
Unit tests for the AGENCY primitive.
"""

from ontology.agency import Agency, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "AGENCY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Agency()
    result = primitive.evaluate()

    assert abs(result["autonomous_initiation"] - 0.0) < 1e-12
    assert abs(result["self_modulation"] - 0.0) < 1e-12
    assert abs(result["intentional_persistence"] - 0.0) < 1e-12
    assert abs(result["agency_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "AGENCY"


def test_nominal_case():
    primitive = Agency()
    result = primitive.evaluate(
        goal_directedness=0.8,
        steerability=0.6,
        controllability=0.9,
        observability=0.3,
        reflexive_threshold=0.7,
    )

    assert 0.0 <= result["agency_index"] <= 1.0
    assert result["agency_index"] > 0.0


def test_negative_case():
    primitive = Agency()
    result = primitive.validate(
        goal_directedness=0.0,
        steerability=0.0,
        controllability=0.0,
        observability=0.0,
        reflexive_threshold=0.0,
    )

    assert result["valid"] is False
    assert abs(result["agency_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Agency()
    result = primitive.evaluate(
        goal_directedness=2.0,
        steerability=-1.0,
        controllability=3.0,
        observability=0.5,
        reflexive_threshold=10.0,
    )

    assert 0.0 <= result["autonomous_initiation"] <= 1.0
    assert 0.0 <= result["self_modulation"] <= 1.0
    assert 0.0 <= result["intentional_persistence"] <= 1.0
    assert 0.0 <= result["agency_index"] <= 1.0


def test_step_consistency():
    primitive = Agency()
    kwargs = dict(
        goal_directedness=0.75,
        steerability=0.5,
        controllability=0.6,
        observability=0.7,
        reflexive_threshold=0.8,
    )

    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)

    assert abs(stepped["agency_index"] - evaluated["agency_index"]) < 1e-12


def test_validate_consistency():
    primitive = Agency()
    kwargs = dict(
        goal_directedness=0.75,
        steerability=0.5,
        controllability=0.6,
        observability=0.7,
        reflexive_threshold=0.8,
    )

    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)

    assert validated["valid"] == (evaluated["agency_index"] > 0.0)
    assert abs(validated["agency_index"] - evaluated["agency_index"]) < 1e-12
