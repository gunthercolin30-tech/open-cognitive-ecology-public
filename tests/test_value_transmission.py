
from ontology.value_transmission import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ValueTransmission,
)


def test_metadata():
    assert PRIMITIVE_NAME == "VALUE_TRANSMISSION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ValueTransmission()
    result = primitive.evaluate([], [])

    assert abs(result["value_transmission_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = ValueTransmission()

    current = [1.0, 0.8, 0.6]
    transmitted = [1.0, 0.7, 0.5]

    result = primitive.evaluate(current, transmitted)

    assert 0.0 <= result["value_preservation"] <= 1.0
    assert 0.0 <= result["intergenerational_value_alignment"] <= 1.0
    assert 0.0 <= result["normative_fidelity"] <= 1.0
    assert 0.0 <= result["value_transmission_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = ValueTransmission()

    current = [0.0, 0.0]
    transmitted = [0.0, 0.0]

    result = primitive.evaluate(current, transmitted)

    # preservation = 0.0
    # alignment = 1.0
    # fidelity = 1.0
    # transmission_index = (0.0 + 1.0 + 1.0) / 3 = 2/3
    expected = 2.0 / 3.0

    assert abs(result["value_transmission_index"] - expected) < 1e-12


def test_bounding():
    primitive = ValueTransmission()

    result = primitive.evaluate(
        [2.0, -1.0],
        [3.0, -2.0],
    )

    assert 0.0 <= result["value_preservation"] <= 1.0
    assert 0.0 <= result["intergenerational_value_alignment"] <= 1.0
    assert 0.0 <= result["normative_fidelity"] <= 1.0
    assert 0.0 <= result["value_transmission_index"] <= 1.0


def test_step_consistency():
    primitive = ValueTransmission()

    current = [0.9, 0.8]
    transmitted = [0.9, 0.7]

    result_evaluate = primitive.evaluate(current, transmitted)
    result_step = primitive.step(current, transmitted)

    assert abs(
        result_evaluate["value_transmission_index"]
        - result_step["value_transmission_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ValueTransmission()

    current = [0.9, 0.8]
    transmitted = [0.9, 0.7]

    evaluation = primitive.evaluate(current, transmitted)
    validation = primitive.validate(current, transmitted)

    assert abs(
        evaluation["value_transmission_index"]
        - validation["value_transmission_index"]
    ) < 1e-12

    assert validation["is_valid"] is True


