from ontology.meta_adaptation import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    MetaAdaptation,
)


def test_metadata():
    assert PRIMITIVE_NAME == "META_ADAPTATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = MetaAdaptation()
    result = primitive.evaluate()

    assert abs(result["meta_adaptive_potential"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "static"


def test_nominal_case():
    primitive = MetaAdaptation(
        self_modification_capacity=0.9,
        strategy_revision_rate=0.6,
        adaptive_reflexivity=0.8,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.8) / 3.0

    assert abs(result["meta_adaptive_potential"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "meta_adaptive"


def test_negative_inputs_are_clamped():
    primitive = MetaAdaptation(
        self_modification_capacity=-1.0,
        strategy_revision_rate=-2.0,
        adaptive_reflexivity=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["meta_adaptive_potential"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = MetaAdaptation(
        self_modification_capacity=10.0,
        strategy_revision_rate=10.0,
        adaptive_reflexivity=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "self_modification_capacity",
        "strategy_revision_rate",
        "adaptive_reflexivity",
        "meta_adaptive_potential",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = MetaAdaptation(
        self_modification_capacity=0.3,
        strategy_revision_rate=0.5,
        adaptive_reflexivity=0.7,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "self_modification_capacity",
        "strategy_revision_rate",
        "adaptive_reflexivity",
        "meta_adaptive_potential",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = MetaAdaptation(
        self_modification_capacity=0.8,
        strategy_revision_rate=0.4,
        adaptive_reflexivity=0.9,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["meta_adaptive_potential"]
            - evaluation["meta_adaptive_potential"]
        )
        < 1e-12
    )
