from ontology.autonomous_external_collaboration_runner import (
    DEPENDENCIES as RUNNER_DEPENDENCIES,
)
from ontology.openrouter_autonomous_provider_adapter import (
    DEPENDENCIES as OPENROUTER_DEPENDENCIES,
)
from ontology.real_chatgpt_autonomous_api_adapter import (
    DEPENDENCIES as CHATGPT_DEPENDENCIES,
)


def test_external_collaboration_runner_consumes_provider_results():
    assert "openrouter_autonomous_provider_adapter" in RUNNER_DEPENDENCIES
    assert "real_chatgpt_autonomous_api_adapter" in RUNNER_DEPENDENCIES

    assert "autonomous_external_collaboration_runner" not in OPENROUTER_DEPENDENCIES
    assert "autonomous_external_collaboration_runner" not in CHATGPT_DEPENDENCIES
