from ontology.consciousness_readiness_index import (
    DEPENDENCIES as READINESS_DEPENDENCIES,
)
from ontology.constitutional_scientific_observatory_suite import (
    DEPENDENCIES as OBSERVATORY_DEPENDENCIES,
)
from ontology.reflexive_threshold import DEPENDENCIES, ReflexiveThreshold
from ontology.unified_consciousness_composite_index import (
    DEPENDENCIES as COMPOSITE_DEPENDENCIES,
)


def test_reflexive_threshold_consumes_prior_cycle_snapshots():
    result = ReflexiveThreshold().step(
        observatory_result={"constitutional_scientific_observatory_score": 0.8},
        consciousness_result={"unified_consciousness_composite_index": 0.9},
    )

    assert "constitutional_scientific_observatory_suite" not in DEPENDENCIES
    assert "unified_consciousness_composite_index" not in DEPENDENCIES
    assert "unified_consciousness_composite_index" in OBSERVATORY_DEPENDENCIES
    assert "consciousness_readiness_index" in COMPOSITE_DEPENDENCIES
    assert "reflexive_threshold" in READINESS_DEPENDENCIES
    assert result["diagnostics"]["observatory_input_contract"] == "prior_cycle_snapshot"
    assert result["diagnostics"]["consciousness_input_contract"] == "prior_cycle_snapshot"
