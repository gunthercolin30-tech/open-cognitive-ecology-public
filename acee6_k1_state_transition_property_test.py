from acee6_k1_property_domains import structured_cases, TERMINAL_STATES
from acee6_k1_property_oracles import evaluate_case, verify_case
for case in structured_cases(limit=256):
    result=evaluate_case(case)
    assert result["terminal_state"] in TERMINAL_STATES
    assert not verify_case(case,result)
    assert result["partial_success"] is False
print("ACEE6_K1_STATE_TRANSITION_PROPERTIES_OK")
