"""Unit tests for the ATTRACTOR_BASIN primitive."""

from ontology.attractor_basin import AttractorBasin


def test_empty_input():
    primitive = AttractorBasin()

    result = primitive.evaluate({})

    assert result["basin_membership"] == {}
    assert result["basin_size"] == 0.0
    assert result["significant_basin_exists"] is False
    assert result["diagnostics"]["configuration_count"] == 0


def test_significant_basin():
    primitive = AttractorBasin(basin_threshold=0.5)

    result = primitive.evaluate({"a": 0.8, "b": 0.6})

    assert abs(result["basin_size"] - 0.7) < 1e-12
    assert result["significant_basin_exists"] is True
    assert result["diagnostics"]["status"] == "significant_basin"


def test_insignificant_basin():
    primitive = AttractorBasin(basin_threshold=0.5)

    result = primitive.evaluate({"a": 0.2, "b": 0.4})

    assert abs(result["basin_size"] - 0.3) < 1e-12
    assert result["significant_basin_exists"] is False
    assert result["diagnostics"]["status"] == "insignificant_basin"


def test_mean_computation():
    primitive = AttractorBasin()

    result = primitive.evaluate({"a": 0.2, "b": 0.4, "c": 0.9})

    expected = (0.2 + 0.4 + 0.9) / 3.0
    assert abs(result["basin_size"] - expected) < 1e-12


def test_value_clamping():
    primitive = AttractorBasin()

    result = primitive.evaluate({"a": -1.0, "b": 2.0})

    assert result["basin_membership"]["a"] == 0.0
    assert result["basin_membership"]["b"] == 1.0
    assert abs(result["basin_size"] - 0.5) < 1e-12


def test_step_matches_evaluate():
    primitive = AttractorBasin()

    data = {"a": 0.9, "b": 0.1}

    assert primitive.step(data) == primitive.evaluate(data)


def test_validate_matches_evaluate():
    primitive = AttractorBasin()

    data = {"a": 0.8, "b": 0.6}

    evaluation = primitive.evaluate(data)
    validation = primitive.validate(data)

    assert validation["valid"] == evaluation["significant_basin_exists"]
    assert (
        validation["significant_basin_exists"]
        == evaluation["significant_basin_exists"]
    )
    assert abs(validation["basin_size"] - evaluation["basin_size"]) < 1e-12
    assert validation["diagnostics"] == evaluation["diagnostics"]