from ontology import dna_inheritance as d

assert d.validate_inheritance_model()
m = d.inheritance_manifest()
assert m["scope"] == "P020_ONLY"
assert m["levels"] == d.INHERITANCE_LEVELS
assert m["edges"] == d.INHERITANCE_EDGES
assert m["transversal_referentials"]["world_models_dependency"] is None
print("P020_DNA_INHERITANCE_OK")
