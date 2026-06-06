from ontology.distributed_agency import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    DistributedAgency,
)


def test_metadata():
    assert PRIMITIVE_NAME == "DISTRIBUTED_AGENCY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = DistributedAgency()
    result = primitive.evaluate({})
    assert abs(result["distributed_agency_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = DistributedAgency()
    state = {
        "communication_alignment": 0.8,
        "goal_consensus": 0.6,
        "delegation_balance": 0.9,
        "execution_synchronization": 0.7,
    }

    result = primitive.evaluate(state)

    expected_coherence = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(result["coordination_coherence"] - expected_coherence) < 1e-12
    assert abs(result["authority_distribution"] - 0.9) < 1e-12
    assert abs(result["action_integration"] - 0.7) < 1e-12
    assert abs(result["distributed_agency_index"] - expected_index) < 1e-12


def test_negative_case():
    primitive = DistributedAgency()
    state = {
        "communication_alignment": 0.1,
        "goal_consensus": 0.0,
        "delegation_balance": 0.1,
        "execution_synchronization": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["distributed_agency_index"] < 0.5


def test_bounding():
    primitive = DistributedAgency()
    state = {
        "communication_alignment": 5.0,
        "goal_consensus": -2.0,
        "delegation_balance": 10.0,
        "execution_synchronization": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "coordination_coherence",
        "authority_distribution",
        "action_integration",
        "distributed_agency_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = DistributedAgency()
    state = {
        "communication_alignment": 0.7,
        "goal_consensus": 0.8,
        "delegation_balance": 0.6,
        "execution_synchronization": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["distributed_agency_index"]
        - step_result["distributed_agency_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = DistributedAgency()
    state = {
        "communication_alignment": 0.9,
        "goal_consensus": 0.9,
        "delegation_balance": 0.9,
        "execution_synchronization": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["distributed_agency_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
