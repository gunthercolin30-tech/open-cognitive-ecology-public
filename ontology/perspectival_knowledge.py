PRIMITIVE = "perspectival_knowledge"
DESCRIPTION = "Perspectival knowledge."
DEPENDENCIES = []

"""Auto-generated ontology module for perspectival_knowledge."""

PRIMITIVE_NAME = "perspectival_knowledge"
IS_ACTIVE = True
DESCRIPTION = "Ontology primitive 'perspectival_knowledge' automatically generated from dependency registry."

def get_metadata():
    return {
        "name": PRIMITIVE_NAME,
        "active": IS_ACTIVE,
        "description": DESCRIPTION,
    }


class PerspectivalKnowledge:
    """Auto-generated activation class for perspectival_knowledge."""

    PRIMITIVE = "perspectival_knowledge"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

