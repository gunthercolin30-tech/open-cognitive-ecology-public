PRIMITIVE = "theory_of_non_representability"
DESCRIPTION = "Theory of non representability."
DEPENDENCIES = []

"""Auto-generated ontology module for theory_of_non_representability."""

PRIMITIVE_NAME = "theory_of_non_representability"
IS_ACTIVE = True
DESCRIPTION = "Ontology primitive 'theory_of_non_representability' automatically generated from dependency registry."

def get_metadata():
    return {
        "name": PRIMITIVE_NAME,
        "active": IS_ACTIVE,
        "description": DESCRIPTION,
    }


class TheoryOfNonRepresentability:
    """Auto-generated activation class for theory_of_non_representability."""

    PRIMITIVE = "theory_of_non_representability"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

