"""
tests/test_neutral_network.py
"""

from ontology.neutral_network import (
    NeutralNetwork,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "NEUTRAL_NETWORK"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = NeutralNetwork()
    result = primitive.evaluate()

    assert abs(result["neutral_connectivity"] - 0.0) < 1e-12
    assert abs(result["fitness_equivalence"] - 0.0) < 1e-12
    assert abs(result["exploration_capacity"] - 0.0) < 1e-12
    assert abs(result["neutral_network_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = NeutralNetwork(
        neutral_connectivity=0.9,
        fitness_equivalence=0.6,
        exploration_capacity=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["neutral_network_index"] - expected) < 1e-12


def test_negative_case():
    primitive = NeutralNetwork(
        neutral_connectivity=-1.0,
        fitness_equivalence=-2.0,
        exploration_capacity=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["neutral_network_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = NeutralNetwork(
        neutral_connectivity=2.0,
        fitness_equivalence=1.5,
        exploration_capacity=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["neutral_connectivity"] - 1.0) < 1e-12
    assert abs(result["fitness_equivalence"] - 1.0) < 1e-12
    assert abs(result["exploration_capacity"] - 1.0) < 1e-12
    assert abs(result["neutral_network_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = NeutralNetwork(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["neutral_network_index"]
        - result_step["neutral_network_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = NeutralNetwork(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["neutral_network_index"]
        - result["neutral_network_index"]
    ) < 1e-12
