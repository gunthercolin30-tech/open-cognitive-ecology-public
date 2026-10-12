from ontology import dna_adversarial_regression as d
assert d.validate_adversarial_regression()
assert d.DEPENDENCIES==["dna_fitness_suite"]
assert d.P024_SCOPE=="P024_ONLY"
print("P024_DNA_ADVERSARIAL_REGRESSION_OK")
