PRIMITIVE = "meta_theoretical_reflexivity"
DESCRIPTION = "Meta theoretical reflexivity."
DEPENDENCIES = []

"""Auto-generated ontology module for meta_theoretical_reflexivity."""

PRIMITIVE_NAME = "meta_theoretical_reflexivity"
IS_ACTIVE = True
DESCRIPTION = "Ontology primitive 'meta_theoretical_reflexivity' automatically generated from dependency registry."

def get_metadata():
    return {
        "name": PRIMITIVE_NAME,
        "active": IS_ACTIVE,
        "description": DESCRIPTION,
    }


class MetaTheoreticalReflexivity:
    """Auto-generated activation class for meta_theoretical_reflexivity."""

    PRIMITIVE = "meta_theoretical_reflexivity"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

