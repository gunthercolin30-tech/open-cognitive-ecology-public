from ontology.meta_institutional_adaptation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    MetaInstitutionalAdaptation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "META_INSTITUTIONAL_ADAPTATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MetaInstitutionalAdaptation()
    result = primitive.evaluate({})
    assert abs(result["meta_institutional_adaptation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = MetaInstitutionalAdaptation()
    state = {
        "audit_quality": 0.8,
        "reform_capacity": 0.6,
        "feedback_integration": 0.8,
        "implementation_effectiveness": 0.7,
    }

    result = primitive.evaluate(state)

    expected_revision = 0.7
    expected_index = (0.8 + 0.7 + 0.7) / 3.0

    assert abs(result["self_evaluation_capacity"] - 0.8) < 1e-12
    assert abs(result["rule_revision_capability"] - expected_revision) < 1e-12
    assert abs(result["corrective_effectiveness"] - 0.7) < 1e-12
    assert abs(
        result["meta_institutional_adaptation_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = MetaInstitutionalAdaptation()
    state = {
        "audit_quality": 0.1,
        "reform_capacity": 0.0,
        "feedback_integration": 0.0,
        "implementation_effectiveness": 0.1,
    }

    result = primitive.evaluate(state)
    assert result["meta_institutional_adaptation_index"] < 0.5


def test_bounding():
    primitive = MetaInstitutionalAdaptation()
    state = {
        "audit_quality": 5.0,
        "reform_capacity": -2.0,
        "feedback_integration": 10.0,
        "implementation_effectiveness": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "self_evaluation_capacity",
        "rule_revision_capability",
        "corrective_effectiveness",
        "meta_institutional_adaptation_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = MetaInstitutionalAdaptation()
    state = {
        "audit_quality": 0.7,
        "reform_capacity": 0.8,
        "feedback_integration": 0.6,
        "implementation_effectiveness": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["meta_institutional_adaptation_index"]
        - step_result["meta_institutional_adaptation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = MetaInstitutionalAdaptation()
    state = {
        "audit_quality": 0.9,
        "reform_capacity": 0.9,
        "feedback_integration": 0.9,
        "implementation_effectiveness": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["meta_institutional_adaptation_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
