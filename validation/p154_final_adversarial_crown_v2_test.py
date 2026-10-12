from pathlib import Path
import sys, copy, json
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import HYPOTHESES, preregister, evaluate
from validation.p154_test_support import reg, evidence

# 1. Exact threshold is NOT a pass.
for hid,threshold in [("H1",0.0),("H4",1.0),("H7",0.25)]:
    r=reg(hid,threshold)
    o=evaluate(r,evidence(r,result=threshold))
    assert o["passed"] is False and o["decision"]=="RETHINK"

# 2. Canonical priorities and failure consequences.
assert [HYPOTHESES[x]["priority"] for x in ("H1","H2","H3")]==["EARLY_CARDINAL"]*3
assert [HYPOTHESES[x]["priority"] for x in ("H4","H5","H6")]==["LATER"]*3
assert HYPOTHESES["H7"]["priority"]=="LATE"
assert HYPOTHESES["H2"]["failure_consequence"]=="DO_NOT_BUILD_INDIVIDUAL_ECONOMY"
assert HYPOTHESES["H5"]["failure_consequence"]=="REDUCE_OR_LIMIT_CROWD_ENGINE"
assert HYPOTHESES["H7"]["failure_consequence"]=="DO_NOT_BUILD_OR_MAINTAIN_MARKETPLACE"

# 3. Any post-registration mutation invalidates the registration.
r=reg("H1")
for field,value in [
    ("priority","LATE"),("failure_consequence","IGNORE_FAILURE"),
    ("threshold",-999.0),("target_family","changed"),
    ("next_reevaluation_date","2099-01-01")]:
    bad=copy.deepcopy(r); bad[field]=value
    try: evaluate(bad,evidence(r)); raise AssertionError("tamper accepted: "+field)
    except ValueError: pass
bad=copy.deepcopy(r); bad["baseline"]["name"]="changed"
try: evaluate(bad,evidence(r)); raise AssertionError("baseline tamper accepted")
except ValueError: pass

# 4. Strict evidence booleans: truthy non-booleans are not accepted.
for field,value in [("verified",1),("external_signal",1),("verified","true"),("external_signal","yes")]:
    o=evaluate(r,evidence(r,**{field:value}))
    assert o["status"]=="UNKNOWN" and o["decision"]=="RETHINK"

# 5. Numeric booleans/non-finites/invalid replication types rejected.
for field,value in [
    ("result",True),("confidence",False),("uncertainty",True),
    ("result",float("inf")),("result",float("-inf")),("result",float("nan")),
    ("confidence",float("nan")),("uncertainty",float("inf")),
    ("replications",True),("replications",2.0),("replications",-1)]:
    try: evaluate(r,evidence(r,**{field:value})); raise AssertionError("invalid accepted: "+field)
    except ValueError: pass

# 6. Provenance is mandatory after external verification.
for value in ("",None,"   "):
    try: evaluate(r,evidence(r,provenance=value)); raise AssertionError("empty provenance accepted")
    except ValueError: pass

# 7. Cross-hypothesis evidence cannot be replayed.
r2=reg("H2")
try: evaluate(r2,evidence(r)); raise AssertionError("cross-hypothesis replay accepted")
except ValueError: pass

# 8. H7 cannot be preregistered without an explicit ex-ante threshold.
try:
    preregister(hypothesis_id="H7",protocol="p",
      baseline={"name":"b","provenance":"p"},target_family="f",
      next_reevaluation_date="d",preregistered_at="t")
    raise AssertionError("H7 without threshold accepted")
except ValueError: pass

# 9. Canonical hash is deterministic under mapping insertion-order changes.
r=reg("H3")
baseline_a={"name":"synthetic comparator","provenance":"synthetic_test_fixture"}
baseline_b={"provenance":"synthetic_test_fixture","name":"synthetic comparator"}
a=preregister(hypothesis_id="H3",protocol="synthetic P154 validation protocol",
 baseline=baseline_a,target_family="synthetic_validation_family",
 next_reevaluation_date="2026-10-15",preregistered_at="2026-09-15T16:00:00+00:00")
b=preregister(hypothesis_id="H3",protocol="synthetic P154 validation protocol",
 baseline=baseline_b,target_family="synthetic_validation_family",
 next_reevaluation_date="2026-10-15",preregistered_at="2026-09-15T16:00:00+00:00")
assert a["preregistration_hash"]==b["preregistration_hash"]

# 10. Evaluation does not mutate caller inputs.
r=reg("H6"); e=evidence(r,result=0.5)
r_before=copy.deepcopy(r); e_before=copy.deepcopy(e)
evaluate(r,e)
assert r==r_before and e==e_before

# 11. Synthetic test evidence can exercise the mechanism, but never sets
#     the explicit empirical-proof flag.
for hid,threshold,result in [
 ("H1",0.0,1.0),("H2",0.0,1.0),("H3",0.0,1.0),
 ("H4",1.0,1.1),("H5",0.0,1.0),("H6",0.0,1.0),("H7",0.1,0.2)]:
    o=evaluate(reg(hid,threshold),evidence(reg(hid,threshold),result=result))
    # Above uses two deterministic registrations; hashes are identical.
    assert o["economic_hypothesis_empirically_proven"] is False

print("P154_FINAL_ADVERSARIAL_CROWN_V2_OK")
