PRIMITIVE = "changes_of_status_of_concepts"
DESCRIPTION = "Changes of status of concepts."
DEPENDENCIES = []

"""Auto-generated ontology module for changes_of_status_of_concepts."""

PRIMITIVE_NAME = "changes_of_status_of_concepts"
IS_ACTIVE = True
DESCRIPTION = (
    "Context-dependent transitions in the theoretical role and status of concepts."
)

def get_metadata():
    return {
        "name": PRIMITIVE_NAME,
        "active": IS_ACTIVE,
        "description": DESCRIPTION,
    }


class ChangesOfStatusOfConcepts:
    """Auto-generated activation class for changes_of_status_of_concepts."""

    PRIMITIVE = "changes_of_status_of_concepts"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

