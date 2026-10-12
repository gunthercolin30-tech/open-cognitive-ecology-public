from ontology import p160_runtime_context_contract as p


def main():
    m=p.manifest()
    assert m["scope"]=="P160-A_ONLY"
    assert m["boundaries"]["authorization_created"] is False
    assert m["boundaries"]["execution_performed"] is False
    assert m["boundaries"]["p161_opened"] is False
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    print("P160A_RUNTIME_CONTEXT_CONTRACT_OK")
    print("P160A_SCOPE=P160-A_ONLY")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("P161_OPENED=false")

if __name__=="__main__": main()
