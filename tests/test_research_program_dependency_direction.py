from ontology.collective_research_program_manager import (
    DEPENDENCIES as RESEARCH_PROGRAM_DEPENDENCIES,
)
from ontology.web_dashboard_exporter import (
    DEPENDENCIES as DASHBOARD_EXPORTER_DEPENDENCIES,
)


def test_research_program_generation_does_not_depend_on_presentation_export():
    assert "web_dashboard_exporter" not in RESEARCH_PROGRAM_DEPENDENCIES
    assert "civilizational_dashboard" in DASHBOARD_EXPORTER_DEPENDENCIES
