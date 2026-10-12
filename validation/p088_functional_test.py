from ontology import dna_fundamental as d
def main():
 m=d.fundamental_manifest()
 assert m["version"]=="P088-v1" and m["scope"]=="P088_ONLY"
 assert m["normative_order"]==("GENESIS",("DNA-H","DNA-L0"),"DNA-L1","CCAD","CONSTITUTION","GOVERNANCE","POLICY_PROCEDURE")
 assert m["boundaries"]["does_not_define_p089_values"] and m["boundaries"]["does_not_define_p090_meta_rules"]
 assert m["boundaries"]["does_not_grant_runtime_authority"]
 assert m["functional_conclusion_only"] and m["phenomenology_undetermined"]
 print("P088_FUNCTIONAL_OK")
if __name__=="__main__": main()
