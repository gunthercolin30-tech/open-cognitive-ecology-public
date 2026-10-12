from ontology.epistemic_guard import EpistemicGuard

r = EpistemicGuard().step(persist=False)

print("AO3_KEYS:")
for k in sorted(r.keys()):
    print("-", k)
