from ontology import p160_norm_resolution as p

def main():
    m=p.manifest()
    assert m["scope"]=="P160-B_ONLY"
    assert m["artifacts"]==["norm_context","normative_applicability","norm_resolution_trace"]
    print("P160B_NORM_RESOLUTION_CONTRACT_OK")
    print("ARTIFACTS=3/3")
    print("CONSTITUTIVE_FILTER_PERFORMED=false")
    print("CONFLICT_ARBITRATION_PERFORMED=false")
    print("AUTHORITY_RESOLVED=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("P161_OPENED=false")
    print("P160_FINAL_LOCK=false")
if __name__=="__main__": main()
