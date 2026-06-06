from ontology.social_ecological_resilience import (
    SocialEcologicalResilience,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "SOCIAL_ECOLOGICAL_RESILIENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SocialEcologicalResilience()
    result = primitive.evaluate({})
    assert abs(
        result["social_ecological_resilience_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = SocialEcologicalResilience()
    result = primitive.evaluate(
        {
            "ecological_resilience": 0.8,
            "institutional_resilience": 0.7,
            "adaptive_governance": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(
        result["social_ecological_resilience_index"] - expected
    ) < 1e-12
    assert result["diagnostics"]["status"] == "resilient"


def test_negative_case():
    primitive = SocialEcologicalResilience()
    result = primitive.evaluate(
        {
            "ecological_resilience": 0.1,
            "institutional_resilience": 0.2,
            "adaptive_governance": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "fragile"


def test_bounding():
    primitive = SocialEcologicalResilience()
    result = primitive.evaluate(
        {
            "ecological_resilience": 2.0,
            "institutional_resilience": -1.0,
            "adaptive_governance": 5.0,
        }
    )
    assert abs(result["ecological_resilience"] - 1.0) < 1e-12
    assert abs(result["institutional_resilience"] - 0.0) < 1e-12
    assert abs(result["adaptive_governance"] - 1.0) < 1e-12
    assert 0.0 <= result["social_ecological_resilience_index"] <= 1.0


def test_step_consistency():
    primitive = SocialEcologicalResilience()
    inputs = {
        "ecological_resilience": 0.6,
        "institutional_resilience": 0.6,
        "adaptive_governance": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = SocialEcologicalResilience()
    inputs = {
        "ecological_resilience": 0.4,
        "institutional_resilience": 0.5,
        "adaptive_governance": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["social_ecological_resilience_index"]
            - evaluation["social_ecological_resilience_index"]
        )
        < 1e-12
    )
