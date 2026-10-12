from ontology import dna_fundamental as d
from ontology import minimal_dna,dna_stack,dna_registry,dna_rule_contract,dna_severity_model,dna_inheritance,dna_mutation_protocol,dna_versioning_lineage,dna_fitness_suite,dna_adversarial_regression
def main():
 assert minimal_dna.OCE_DNA_DEFINITION_VERSION=="P015-v3"
 for value,prefix in ((dna_stack.P016_VERSION,"P016-"),(dna_registry.P017_VERSION,"P017-"),(dna_rule_contract.P018_VERSION,"P018-"),(dna_severity_model.P019_VERSION,"P019-"),(dna_inheritance.P020_VERSION,"P020-"),(dna_mutation_protocol.P021_VERSION,"P021-"),(dna_versioning_lineage.P022_VERSION,"P022-"),(dna_fitness_suite.P023_VERSION,"P023-"),(dna_adversarial_regression.P024_VERSION,"P024-")):
  assert value.startswith(prefix)
 assert d.fundamental_manifest()["p015_p024_reused_without_mutation"]
 print("P088_NON_REGRESSION_OK")
if __name__=="__main__": main()
