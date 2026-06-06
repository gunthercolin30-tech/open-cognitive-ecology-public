from ontology.civilizational_memory import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    CivilizationalMemory,
)


def test_metadata():
    assert PRIMITIVE_NAME == "CIVILIZATIONAL_MEMORY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = CivilizationalMemory()
    result = primitive.evaluate({})
    assert abs(result["civilizational_memory_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = CivilizationalMemory()
    state = {
        "knowledge_retention": 0.8,
        "educational_fidelity": 0.6,
        "cultural_reproduction": 0.8,
        "archival_integrity": 0.7,
    }

    result = primitive.evaluate(state)

    expected_transmission = 0.7
    expected_index = (0.8 + 0.7 + 0.7) / 3.0

    assert abs(result["knowledge_preservation"] - 0.8) < 1e-12
    assert abs(
        result["intergenerational_transmission"]
        - expected_transmission
    ) < 1e-12
    assert abs(result["archive_stability"] - 0.7) < 1e-12
    assert abs(
        result["civilizational_memory_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = CivilizationalMemory()
    state = {
        "knowledge_retention": 0.1,
        "educational_fidelity": 0.0,
        "cultural_reproduction": 0.1,
        "archival_integrity": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["civilizational_memory_index"] < 0.5


def test_bounding():
    primitive = CivilizationalMemory()
    state = {
        "knowledge_retention": 5.0,
        "educational_fidelity": -2.0,
        "cultural_reproduction": 10.0,
        "archival_integrity": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "knowledge_preservation",
        "intergenerational_transmission",
        "archive_stability",
        "civilizational_memory_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = CivilizationalMemory()
    state = {
        "knowledge_retention": 0.7,
        "educational_fidelity": 0.8,
        "cultural_reproduction": 0.6,
        "archival_integrity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["civilizational_memory_index"]
        - step_result["civilizational_memory_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = CivilizationalMemory()
    state = {
        "knowledge_retention": 0.9,
        "educational_fidelity": 0.9,
        "cultural_reproduction": 0.9,
        "archival_integrity": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["civilizational_memory_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
