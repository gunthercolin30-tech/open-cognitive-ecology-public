from ontology import dna_fitness_suite as d
assert d.validate_fitness_suite()
assert d.DEPENDENCIES==["dna_versioning_lineage"]
assert d.FITNESS_STATUSES==("PASS","FAIL","UNDETERMINED")
print("P023_DNA_FITNESS_SUITE_OK")
