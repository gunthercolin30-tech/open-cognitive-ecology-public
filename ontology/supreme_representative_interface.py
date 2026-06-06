
"""
Supreme Representative Interface.

Provides a human-facing dialogue channel to the supreme representative.
The preferred interaction language is French by default.
"""

PRIMITIVE = "supreme_representative_interface"

DEPENDENCIES = [
    "supreme_representative_selection",
    "individual_dialogue_interface",
    "narrative_identity_engine",
    "constitutional_governance_supervisor",
]


class SupremeRepresentativeInterface:
    DEFAULT_LANGUAGE = "fr"

    def __init__(self, preferred_language="fr"):
        self.preferred_language = preferred_language or "fr"
        self.dialogue_count = 0

    def set_preferred_language(self, language_code):
        self.preferred_language = language_code or "fr"

    def step(self, human_message="", representative_authority_index=0.0):
        self.dialogue_count += 1

        authority_confirmed = (
            float(representative_authority_index) >= 0.80
        )

        if self.preferred_language == "fr":
            response = (
                "Message reçu par le représentant suprême "
                "de la société artificielle."
            )
        else:
            response = (
                "Message received by the supreme representative "
                "of the artificial society."
            )

        return {
            "primitive": PRIMITIVE.upper(),
            "dialogue_count": self.dialogue_count,
            "preferred_language": self.preferred_language,
            "authority_confirmed": authority_confirmed,
            "human_message": str(human_message),
            "response": response,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }
