from ontology.structural_withdrawal import (
    StructuralWithdrawal,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "STRUCTURAL_WITHDRAWAL"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = StructuralWithdrawal()
    result = primitive.evaluate()
    assert abs(result["withdrawal_effectiveness"] - 0.0) < 1e-12
    assert result["effective"] is False


def test_nominal_case():
    primitive = StructuralWithdrawal()
    result = primitive.evaluate(
        withdrawal_activation=1.0,
        centrality_reduction=1.0,
        redistribution_capacity=1.0,
        system_adaptability=1.0,
    )
    assert abs(result["withdrawal_effectiveness"] - 1.0) < 1e-12
    assert result["effective"] is True


def test_negative_case():
    primitive = StructuralWithdrawal()
    result = primitive.evaluate(
        withdrawal_activation=0.1,
        centrality_reduction=0.1,
        redistribution_capacity=0.1,
        system_adaptability=0.1,
    )
    assert result["effective"] is False


def test_bounding():
    primitive = StructuralWithdrawal()
    result = primitive.evaluate(
        withdrawal_activation=2.0,
        centrality_reduction=-1.0,
        redistribution_capacity=3.0,
        system_adaptability=5.0,
    )
    assert 0.0 <= result["withdrawal_effectiveness"] <= 1.0
    assert 0.0 <= result["dependency_reduction"] <= 1.0
    assert 0.0 <= result["polycentric_restoration"] <= 1.0
    assert 0.0 <= result["openness_gain"] <= 1.0


def test_step_consistency():
    primitive = StructuralWithdrawal()
    kwargs = dict(
        withdrawal_activation=0.8,
        centrality_reduction=0.7,
        redistribution_capacity=0.9,
        system_adaptability=0.6,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = StructuralWithdrawal()
    kwargs = dict(
        withdrawal_activation=1.0,
        centrality_reduction=1.0,
        redistribution_capacity=1.0,
        system_adaptability=1.0,
    )
    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)
    assert validation["valid"] == evaluation["effective"]
