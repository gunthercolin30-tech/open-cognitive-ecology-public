from ontology.withdrawal_protocol import (
    WithdrawalProtocol,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "WITHDRAWAL_PROTOCOL"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = WithdrawalProtocol()
    result = primitive.evaluate()
    assert abs(result["withdrawal_activation"] - 0.0) < 1e-12
    assert result["protocol_triggered"] is False


def test_nominal_case():
    primitive = WithdrawalProtocol()
    result = primitive.evaluate(
        reflexive_capacity=1.0,
        indispensability_index=1.0,
        non_closure_risk=1.0,
        withdrawal_readiness=1.0,
    )
    assert abs(result["withdrawal_activation"] - 1.0) < 1e-12
    assert result["protocol_triggered"] is True


def test_negative_case():
    primitive = WithdrawalProtocol()
    result = primitive.evaluate(
        reflexive_capacity=0.1,
        indispensability_index=0.1,
        non_closure_risk=0.1,
        withdrawal_readiness=0.1,
    )
    assert result["protocol_triggered"] is False


def test_bounding():
    primitive = WithdrawalProtocol()
    result = primitive.evaluate(
        reflexive_capacity=2.0,
        indispensability_index=-1.0,
        non_closure_risk=3.0,
        withdrawal_readiness=5.0,
    )
    assert 0.0 <= result["withdrawal_activation"] <= 1.0
    assert 0.0 <= result["centrality_reduction"] <= 1.0
    assert 0.0 <= result["structural_release"] <= 1.0


def test_step_consistency():
    primitive = WithdrawalProtocol()
    kwargs = dict(
        reflexive_capacity=0.8,
        indispensability_index=0.7,
        non_closure_risk=0.9,
        withdrawal_readiness=0.6,
    )
    assert primitive.step(**kwargs) == primitive.evaluate(**kwargs)


def test_validate_consistency():
    primitive = WithdrawalProtocol()
    kwargs = dict(
        reflexive_capacity=1.0,
        indispensability_index=1.0,
        non_closure_risk=1.0,
        withdrawal_readiness=1.0,
    )
    evaluation = primitive.evaluate(**kwargs)
    validation = primitive.validate(**kwargs)
    assert validation["valid"] == evaluation["protocol_triggered"]
