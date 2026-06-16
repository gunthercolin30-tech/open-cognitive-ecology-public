from ontology.civilizational_notification_engine import (
    DEPENDENCIES as NOTIFICATION_DEPENDENCIES,
)
from ontology.persistent_civilizational_conversational_agent import (
    DEPENDENCIES as AGENT_DEPENDENCIES,
)
from ontology.proactive_conversational_initiative import (
    DEPENDENCIES as INITIATIVE_DEPENDENCIES,
)


def test_persistent_agent_consumes_initiative_and_notification_results():
    assert "proactive_conversational_initiative" in AGENT_DEPENDENCIES
    assert "civilizational_notification_engine" in AGENT_DEPENDENCIES

    assert "persistent_civilizational_conversational_agent" not in INITIATIVE_DEPENDENCIES
    assert "persistent_civilizational_conversational_agent" not in NOTIFICATION_DEPENDENCIES
