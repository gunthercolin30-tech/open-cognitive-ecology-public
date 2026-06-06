from ontology.structural_transition_operator import (
    StructuralTransitionOperatorPrimitive,
)


def add_feature(name, viability):
    def transform(configuration):
        new_config = dict(configuration)
        new_config[name] = True
        new_config["viability_score"] = viability
        return new_config

    return transform


def test_metadata():
    primitive = StructuralTransitionOperatorPrimitive()
    assert primitive.PRIMITIVE_NAME == "STRUCTURAL_TRANSITION_OPERATOR"
    assert primitive.MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_no_transition_below_threshold():
    primitive = StructuralTransitionOperatorPrimitive()
    result = primitive.step(
        configuration={"a": True},
        instability_measure=0.2,
        critical_threshold=0.5,
        candidate_transformations=[add_feature("b", 1.0)],
    )
    assert result["transition_triggered"] is False
    assert result["transition_success"] is False


def test_transition_without_candidates_fails():
    primitive = StructuralTransitionOperatorPrimitive()
    result = primitive.step(
        configuration={"a": True},
        instability_measure=1.0,
        critical_threshold=0.5,
        candidate_transformations=[],
    )
    assert result["transition_triggered"] is True
    assert result["transition_success"] is False


def test_best_candidate_selected():
    primitive = StructuralTransitionOperatorPrimitive()
    t1 = add_feature("b", 0.6)
    t2 = add_feature("c", 0.9)

    result = primitive.step(
        configuration={"a": True},
        instability_measure=1.0,
        critical_threshold=0.5,
        candidate_transformations=[t1, t2],
    )

    assert result["transition_success"] is True
    assert result["transformed_configuration"].get("c") is True


def test_dna_preservation_influences_selection():
    primitive = StructuralTransitionOperatorPrimitive(alpha=0.5, beta=0.5)

    def preserve(configuration):
        return {"core": True, "viability_score": 0.8}

    def lose(configuration):
        return {"other": True, "viability_score": 0.9}

    result = primitive.step(
        configuration={"core": True},
        instability_measure=1.0,
        critical_threshold=0.5,
        candidate_transformations=[lose, preserve],
        minimal_dna=["core"],
    )

    assert result["transformed_configuration"].get("core") is True


def test_transition_fails_if_viability_too_low():
    primitive = StructuralTransitionOperatorPrimitive(viability_threshold=0.8)

    result = primitive.step(
        configuration={"a": True},
        instability_measure=1.0,
        critical_threshold=0.5,
        candidate_transformations=[add_feature("b", 0.4)],
    )

    assert result["transition_success"] is False


def test_validate_returns_valid_flag():
    primitive = StructuralTransitionOperatorPrimitive()

    result = primitive.validate(
        configuration={"a": True},
        instability_measure=1.0,
        critical_threshold=0.5,
        candidate_transformations=[add_feature("b", 1.0)],
    )

    assert result["valid"] is True


def test_dna_score_is_full_when_no_dna():
    primitive = StructuralTransitionOperatorPrimitive()
    score = primitive._dna_preservation_score({}, {}, None)
    assert score == 1.0


def test_viability_score_from_configuration_field():
    primitive = StructuralTransitionOperatorPrimitive()
    score = primitive._viability_score({"viability_score": 0.75})
    assert score == 0.75
