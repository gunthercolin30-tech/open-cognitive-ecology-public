from ontology.open_endedness import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    OpenEndedness,
)


def test_metadata():
    assert PRIMITIVE_NAME == "OPEN_ENDEDNESS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = OpenEndedness()
    result = primitive.evaluate()

    assert abs(result["open_ended_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "closed"


def test_nominal_case():
    primitive = OpenEndedness(
        novelty_generation=0.9,
        innovation_capacity=0.6,
        closure_resistance=0.8,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.8) / 3.0

    assert abs(result["open_ended_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "open_ended"


def test_negative_inputs_are_clamped():
    primitive = OpenEndedness(
        novelty_generation=-1.0,
        innovation_capacity=-2.0,
        closure_resistance=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["open_ended_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = OpenEndedness(
        novelty_generation=10.0,
        innovation_capacity=10.0,
        closure_resistance=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "novelty_generation",
        "innovation_capacity",
        "closure_resistance",
        "open_ended_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = OpenEndedness(
        novelty_generation=0.4,
        innovation_capacity=0.5,
        closure_resistance=0.6,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "novelty_generation",
        "innovation_capacity",
        "closure_resistance",
        "open_ended_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = OpenEndedness(
        novelty_generation=0.7,
        innovation_capacity=0.8,
        closure_resistance=0.9,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["open_ended_potential"]
            - evaluation["open_ended_potential"]
        )
        < 1e-12
    )
