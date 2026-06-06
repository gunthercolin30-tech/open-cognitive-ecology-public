from ontology.multi_scale_coupling import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    MultiScaleCoupling,
)


def test_metadata():
    assert PRIMITIVE_NAME == "MULTI_SCALE_COUPLING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MultiScaleCoupling()
    result = primitive.evaluate()

    assert abs(result["multi_scale_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "decoupled"


def test_nominal_case():
    primitive = MultiScaleCoupling(
        local_global_coupling=0.8,
        cross_scale_feedback=0.6,
        scale_coherence=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["multi_scale_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "coupled"


def test_negative_inputs_are_clamped():
    primitive = MultiScaleCoupling(
        local_global_coupling=-1.0,
        cross_scale_feedback=-2.0,
        scale_coherence=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["multi_scale_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = MultiScaleCoupling(
        local_global_coupling=10.0,
        cross_scale_feedback=10.0,
        scale_coherence=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "local_global_coupling",
        "cross_scale_feedback",
        "scale_coherence",
        "multi_scale_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = MultiScaleCoupling(
        local_global_coupling=0.4,
        cross_scale_feedback=0.5,
        scale_coherence=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "local_global_coupling",
        "cross_scale_feedback",
        "scale_coherence",
        "multi_scale_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = MultiScaleCoupling(
        local_global_coupling=0.7,
        cross_scale_feedback=0.8,
        scale_coherence=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["multi_scale_potential"]
            - evaluation["multi_scale_potential"]
        )
        < 1e-12
    )
