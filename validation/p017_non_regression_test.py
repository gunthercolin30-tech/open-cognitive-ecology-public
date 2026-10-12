from ontology import minimal_dna,dna_stack
from ontology.dna_registry import P017_BOUNDARIES
def main():
    assert minimal_dna.OCE_DNA_DEFINITION_VERSION=="P015-v3"
    assert minimal_dna.OCE_DNA_EPISTEMIC_STATUS["native_end_to_end_civilizational_enforcement"]=="UNKNOWN"
    assert minimal_dna.OCE_DNA_EPISTEMIC_STATUS["functional_conclusion_only"] is True
    assert dna_stack.P016_VERSION=="P016-v1"
    assert dna_stack.P016_BOUNDARIES["does_not_grant_runtime_authority"] is True
    assert dna_stack.P016_BOUNDARIES["does_not_define_registry"] is True
    assert P017_BOUNDARIES["does_not_grant_runtime_authority"] is True
    assert P017_BOUNDARIES["does_not_define_p018_rule_contract"] is True
    print("P017_NON_REGRESSION_TEST_OK")
if __name__=="__main__": main()
