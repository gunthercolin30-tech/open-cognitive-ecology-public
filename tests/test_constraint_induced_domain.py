from ontology.constraint_induced_domain import (
    ConstraintInducedDomainPrimitive,
)


def test_zero_compatibility_without_constraints():
    primitive = ConstraintInducedDomainPrimitive()
    assert primitive.compatibility_measure([]) == 0.0


def test_maximum_compatibility():
    primitive = ConstraintInducedDomainPrimitive()
    constraints = [
        {"compatibility": 1.0, "tension": 0.0},
        {"compatibility": 1.0, "tension": 0.0},
    ]
    assert primitive.compatibility_measure(constraints) == 1.0


def test_no_emergence_below_threshold():
    primitive = ConstraintInducedDomainPrimitive(compatibility_threshold=0.8)
    constraints = [
        {"compatibility": 0.6, "tension": 0.0},
    ]
    assert primitive.domain_emergence(constraints) is False


def test_emergence_above_threshold():
    primitive = ConstraintInducedDomainPrimitive(compatibility_threshold=0.5)
    constraints = [
        {"compatibility": 0.9, "tension": 0.1},
    ]
    assert primitive.domain_emergence(constraints) is True


def test_validate_positive():
    primitive = ConstraintInducedDomainPrimitive()
    result = primitive.validate(
        {
            "constraints": [
                {"compatibility": 1.0, "tension": 0.0},
            ]
        }
    )
    assert result["valid"] is True
    assert result["domain_emerged"] is True
    assert result["diagnostics"]["status"] == "domain_emerged"


def test_validate_negative():
    primitive = ConstraintInducedDomainPrimitive(
        compatibility_threshold=0.9
    )
    result = primitive.validate(
        {
            "constraints": [
                {"compatibility": 0.5, "tension": 0.0},
            ]
        }
    )
    assert result["valid"] is False
    assert result["domain_emerged"] is False
    assert result["diagnostics"]["status"] == "domain_not_emerged"


def test_robustness_to_missing_fields():
    primitive = ConstraintInducedDomainPrimitive()
    constraints = [
        {},
        {"compatibility": 1.0},
        {"tension": 0.2},
        {"weight": 2.0},
    ]
    score = primitive.compatibility_measure(constraints)
    assert 0.0 <= score <= 1.0


def test_step_returns_expected_keys():
    primitive = ConstraintInducedDomainPrimitive()
    result = primitive.step({"constraints": []})
    assert "compatibility_score" in result
    assert "domain_emerged" in result
    assert "compatibility_threshold" in result
