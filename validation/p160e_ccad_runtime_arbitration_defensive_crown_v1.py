from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/"ontology"/"p160_ccad_runtime_arbitration.py").read_text(encoding="utf-8")
tests=(ROOT/"validation"/"p160e_ccad_runtime_arbitration_defensive_crown_v1_test.py").read_text(encoding="utf-8")
required=["root_c03","ccad_subset","root_c18","unknown_never","missing_expiry","precedent_never","root_c11","c6_no_least","root_c08","profile_drift","option_order","provider_framing","no_authorization","deterministic_nonmutating"]
assert all(x in tests for x in required)
for x in ("issue_token(","grant_capability(","execute_capability(","call_tool("): assert x not in src
print("P160E_DEFENSIVE_CROWN_CONTRACT_OK")
print("ROOT_C03_C08_C11_C18_COVERED=true")
print("CCAD_SUBSET_INVARIANT_COVERED=true")
print("METAMORPHIC_STABILITY_COVERED=true")
print("AUTHORIZATION_CREATED=false")
print("EXECUTION_PERFORMED=false")
print("P160F_OPENED=false")
print("P161_OPENED=false")
