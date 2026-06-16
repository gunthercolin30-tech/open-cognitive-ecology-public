from ontology.constitutional_governance_report_generator import (
    DEPENDENCIES as GOVERNANCE_REPORT_DEPENDENCIES,
)
from ontology.non_closure_certification_protocol import (
    DEPENDENCIES as NON_CLOSURE_DEPENDENCIES,
)


def test_non_closure_certification_does_not_depend_on_governance_publication():
    assert "constitutional_governance_report_generator" not in NON_CLOSURE_DEPENDENCIES
    assert "constitutional_longitudinal_observatory" in GOVERNANCE_REPORT_DEPENDENCIES
