from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier

r = AxiomaticCompletenessCertifier().step(persist=False)

print("AN7_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
