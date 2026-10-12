from acee6_k1_property_domains import permutation_cases
from acee6_k1_property_oracles import sha
canonical=lambda items: sorted(items)
hashes={sha(canonical(case)) for case in permutation_cases()}
assert len(hashes)==1
print("ACEE6_K1_PERMUTATION_PROPERTIES_OK")
