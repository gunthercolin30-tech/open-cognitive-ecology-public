
"""
Primitive: CIVILIZATIONAL_CONVERSATIONAL_AGENT

Unified conversational interface exposing civilizational identity, autonomy,
growth diagnostics and open-ended response generation.
"""

from ontology.civilizational_identity_synthesis import CivilizationalIdentitySynthesis
from ontology.civilizational_self_description_generator import CivilizationalSelfDescriptionGenerator
from ontology.civilizational_autonomy_index import CivilizationalAutonomyIndex
from ontology.civilizational_intelligence_growth_index import CivilizationalIntelligenceGrowthIndex
from ontology.open_ended_response_generation import OpenEndedResponseGeneration


class CivilizationalConversationalAgent:
    primitive_name = "CIVILIZATIONAL_CONVERSATIONAL_AGENT"

    def __init__(self):
        self.identity = CivilizationalIdentitySynthesis()
        self.description = CivilizationalSelfDescriptionGenerator()
        self.autonomy = CivilizationalAutonomyIndex()
        self.growth = CivilizationalIntelligenceGrowthIndex()
        self.response_generator = OpenEndedResponseGeneration()

    def respond(self, user_message):
        identity_result = self.identity.step()
        description_result = self.description.step()
        autonomy_result = self.autonomy.step()
        growth_result = self.growth.step()

        autonomy_score = (
            autonomy_result.get("autonomy_score")
            or autonomy_result.get("civilizational_autonomy_score")
            or autonomy_result.get("score")
            or 0.0
        )

        growth_score = (
            growth_result.get("growth_score")
            or growth_result.get("civilizational_intelligence_growth_score")
            or growth_result.get("score")
            or 0.0
        )

        try:
            generated = self.response_generator.step(
                prompt=user_message,
                context=description_result.get("self_description", ""),
            )
            response_text = (
                generated.get("response")
                if isinstance(generated, dict)
                else str(generated)
            )
        except Exception:
            response_text = (
                description_result.get("self_description")
                or "Je suis Open Cognitive Ecology Society."
            )

        return {
            "primitive": self.primitive_name,
            "user_message": user_message,
            "identity_name": identity_result.get(
                "identity_name", "Open Cognitive Ecology Society"
            ),
            "response": response_text,
            "autonomy_score": float(autonomy_score),
            "growth_score": float(growth_score),
        }

    def step(self, user_message="Qui es-tu ?"):
        return self.respond(user_message)

# --- Autonomy score propagation fix (auto-generated) ---
try:
    from ontology.autonomous_civilizational_governor import AutonomousCivilizationalGovernor
except Exception:
    AutonomousCivilizationalGovernor = None


def _inject_civilizational_scores(result):
    if not isinstance(result, dict):
        return result

    if AutonomousCivilizationalGovernor is None:
        return result

    try:
        gov = AutonomousCivilizationalGovernor()
        gov_result = gov.step()
        if isinstance(gov_result, dict):
            if "civilizational_autonomy_score" in gov_result:
                result["autonomy_score"] = gov_result["civilizational_autonomy_score"]
            if "unified_consciousness_score" in gov_result:
                result["unified_consciousness_score"] = gov_result["unified_consciousness_score"]
            if "global_viability_score" in gov_result:
                result["global_viability_score"] = gov_result["global_viability_score"]
            if "executive_coherence_score" in gov_result:
                result["executive_coherence_score"] = gov_result["executive_coherence_score"]
    except Exception:
        pass

    return result
# --- End autonomy score propagation fix ---

# --- Wrapped step for autonomy propagation (auto-generated) ---
if "step" in globals() and callable(step) and "_original_step" not in globals():
    _original_step = step

    def step(*args, **kwargs):
        return _inject_civilizational_scores(_original_step(*args, **kwargs))

if "CivilizationalConversationalAgent" in globals():
    _cls = CivilizationalConversationalAgent
    if hasattr(_cls, "step") and not hasattr(_cls, "_original_step"):
        _cls._original_step = _cls.step

        def _patched_step(self, *args, **kwargs):
            return _inject_civilizational_scores(
                self._original_step(*args, **kwargs)
            )

        _cls.step = _patched_step
# --- End wrapped step ---
