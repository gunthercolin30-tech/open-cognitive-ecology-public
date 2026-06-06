from ontology.constraint_genesis import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ConstraintGenesis,
)


def test_metadata():
    assert PRIMITIVE_NAME == "CONSTRAINT_GENESIS"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ConstraintGenesis()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(
        result["constraint_genesis_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = ConstraintGenesis()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["novel_constraint_emergence"] <= 1.0
    assert 0.0 <= result["structural_stabilization"] <= 1.0
    assert 0.0 <= result["possibility_reconfiguration"] <= 1.0
    assert 0.0 <= result["constraint_genesis_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = ConstraintGenesis()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(
        result["constraint_genesis_index"] - 0.0
    ) < 1e-12


def test_bounding():
    primitive = ConstraintGenesis()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert 0.0 <= result["constraint_genesis_index"] <= 1.0


def test_step_consistency():
    primitive = ConstraintGenesis()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["constraint_genesis_index"]
        - b["constraint_genesis_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ConstraintGenesis()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["constraint_genesis_index"]
        - validation["constraint_genesis_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
