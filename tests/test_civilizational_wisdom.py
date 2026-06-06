from ontology.civilizational_wisdom import (
    CivilizationalWisdom,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "CIVILIZATIONAL_WISDOM"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CivilizationalWisdom()
    result = primitive.evaluate({})
    assert abs(
        result["civilizational_wisdom_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CivilizationalWisdom()
    result = primitive.evaluate(
        {
            "collective_knowledge_integration": 0.8,
            "normative_discernment": 0.7,
            "long_term_civilizational_judgment": 0.9,
        }
    )
    expected = (0.8 + 0.7 + 0.9) / 3.0
    assert abs(
        result["civilizational_wisdom_index"] - expected
    ) < 1e-12
    assert result["diagnostics"]["status"] == "wise"


def test_negative_case():
    primitive = CivilizationalWisdom()
    result = primitive.evaluate(
        {
            "collective_knowledge_integration": 0.1,
            "normative_discernment": 0.2,
            "long_term_civilizational_judgment": 0.1,
        }
    )
    assert result["diagnostics"]["status"] == "myopic"


def test_bounding():
    primitive = CivilizationalWisdom()
    result = primitive.evaluate(
        {
            "collective_knowledge_integration": 2.0,
            "normative_discernment": -1.0,
            "long_term_civilizational_judgment": 5.0,
        }
    )
    assert abs(
        result["collective_knowledge_integration"] - 1.0
    ) < 1e-12
    assert abs(result["normative_discernment"] - 0.0) < 1e-12
    assert abs(
        result["long_term_civilizational_judgment"] - 1.0
    ) < 1e-12
    assert 0.0 <= result["civilizational_wisdom_index"] <= 1.0


def test_step_consistency():
    primitive = CivilizationalWisdom()
    inputs = {
        "collective_knowledge_integration": 0.6,
        "normative_discernment": 0.6,
        "long_term_civilizational_judgment": 0.6,
    }
    assert primitive.step(inputs) == primitive.evaluate(inputs)


def test_validate_consistency():
    primitive = CivilizationalWisdom()
    inputs = {
        "collective_knowledge_integration": 0.4,
        "normative_discernment": 0.5,
        "long_term_civilizational_judgment": 0.6,
    }
    evaluation = primitive.evaluate(inputs)
    validation = primitive.validate(inputs)
    assert validation["is_valid"] is True
    assert (
        abs(
            validation["civilizational_wisdom_index"]
            - evaluation["civilizational_wisdom_index"]
        )
        < 1e-12
    )
