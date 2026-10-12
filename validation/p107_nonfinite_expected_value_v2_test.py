from math import inf,nan
from ontology import constitutional_cognitive_economy as p
def opt(v):
    return {"option_id":"x","expected_value":v,"provenance":{"source":"P107-v2-test"},
    "constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}
for v in (nan,inf,-inf,float("nan"),float("inf"),float("-inf")):
    r=p.evaluate_option(opt(v))
    assert r["status"]=="UNDETERMINED" and r["admissible"] is False
    assert r["reason"]=="nonfinite_expected_value"
assert p.evaluate_option(opt(0.0))["status"]=="PASS"
assert p.evaluate_option(opt(1e300))["status"]=="PASS"
bad=opt(1000); bad["option_id"]="bad"; bad["constraints"]["constitution"]="FAIL"
assert p.select([opt(10),bad])["selected_option_id"]=="x"
print("P107_NONFINITE_EXPECTED_VALUE_V2_OK")
print("nan_rejected=True")
print("positive_infinity_rejected=True")
print("negative_infinity_rejected=True")
print("finite_extreme_value_preserved=True")
print("functional_conclusion_only=True")
print("phenomenology_undetermined=True")
print("p108_opened=False")
