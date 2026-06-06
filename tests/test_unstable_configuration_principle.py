
from ontology.unstable_configuration_principle import (
    UnstableConfigurationPrinciplePrimitive,
)


def test_instability_zero_without_source():
    p = UnstableConfigurationPrinciplePrimitive()
    assert p.instability_measure({"sources": []}) == 0.0


def test_instability_maximum_for_critical_sources():
    p = UnstableConfigurationPrinciplePrimitive()
    score = p.instability_measure({
        "sources": [{"instability": 1.0, "tension": 1.0, "amplification": 2.0}]
    })
    assert score == 1.0


def test_configuration_stable_under_threshold():
    p = UnstableConfigurationPrinciplePrimitive()
    result = p.step({
        "sources": [{"instability": 0.2}],
        "instability_threshold": 0.5,
    })
    assert result["unstable"] is False


def test_configuration_unstable_above_threshold():
    p = UnstableConfigurationPrinciplePrimitive()
    result = p.step({
        "sources": [{"instability": 0.8}],
        "instability_threshold": 0.5,
    })
    assert result["unstable"] is True


def test_active_modes_detection():
    p = UnstableConfigurationPrinciplePrimitive()
    modes = p.instability_modes({
        "sources": [
            {"name": "mode_a", "instability": 0.2},
            {"name": "mode_b", "instability": 0.8},
        ]
    })
    assert modes == ["mode_b"]


def test_validation_positive():
    p = UnstableConfigurationPrinciplePrimitive()
    result = p.validate({"sources": [{"instability": 0.8}]})
    assert result["valid"] is True


def test_validation_negative():
    p = UnstableConfigurationPrinciplePrimitive()
    result = p.validate({"sources": []})
    assert result["valid"] is False


def test_missing_fields_robustness():
    p = UnstableConfigurationPrinciplePrimitive()
    score = p.instability_measure({"sources": [{}]})
    assert score == 0.0


def test_step_returns_expected_keys():
    p = UnstableConfigurationPrinciplePrimitive()
    result = p.step({"sources": []})
    assert set(result.keys()) >= {
        "instability_score",
        "unstable",
        "instability_threshold",
        "active_modes",
    }
