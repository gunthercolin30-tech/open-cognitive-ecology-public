"""
tests/test_allostatic_adaptation.py
"""

from ontology.allostatic_adaptation import (
    AllostaticAdaptation,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "ALLOSTATIC_ADAPTATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = AllostaticAdaptation()
    result = primitive.evaluate()

    assert abs(result["setpoint_adjustment"] - 0.0) < 1e-12
    assert abs(result["predictive_compensation"] - 0.0) < 1e-12
    assert abs(result["contextual_reconfiguration"] - 0.0) < 1e-12
    assert abs(result["allostatic_adaptation_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = AllostaticAdaptation(
        setpoint_adjustment=0.9,
        predictive_compensation=0.6,
        contextual_reconfiguration=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(
        result["allostatic_adaptation_index"] - expected
    ) < 1e-12


def test_negative_case():
    primitive = AllostaticAdaptation(
        setpoint_adjustment=-1.0,
        predictive_compensation=-2.0,
        contextual_reconfiguration=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["allostatic_adaptation_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = AllostaticAdaptation(
        setpoint_adjustment=2.0,
        predictive_compensation=1.5,
        contextual_reconfiguration=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["setpoint_adjustment"] - 1.0) < 1e-12
    assert abs(result["predictive_compensation"] - 1.0) < 1e-12
    assert abs(result["contextual_reconfiguration"] - 1.0) < 1e-12
    assert abs(result["allostatic_adaptation_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = AllostaticAdaptation(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["allostatic_adaptation_index"]
        - result_step["allostatic_adaptation_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = AllostaticAdaptation(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["allostatic_adaptation_index"]
        - result["allostatic_adaptation_index"]
    ) < 1e-12
