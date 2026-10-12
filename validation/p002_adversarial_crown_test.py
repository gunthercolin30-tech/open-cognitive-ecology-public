#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.strategy_selection import StrategySelection
S=StrategySelection()
MODES=["cache","rule","query","statistic","classical_model","simulator","small_neural","external_intelligence","human","collective"]
def c(cid,cost=1.,quality=.9,risk=.1,gov=True,constraints=True,**kw):
    d={"candidate_id":cid,"quality":quality,"risk":risk,"governance_admissible":gov,"constraints_satisfied":constraints,"total_cognitive_cost":cost}; d.update(kw); return d
for winner in MODES:
    out=S.select_minimal_sufficient([c(m,1. if m==winner else 2.) for m in MODES],minimum_quality=.8,maximum_risk=.2)
    assert out.get("status")=="SELECTED",(winner,out)
    assert out.get("selected_candidate",{}).get("candidate_id")==winner,(winner,out)
print("P002_CROWN_CANONICAL_MODES_OK")
for x in [c("bad_quality",0,quality=.79),c("bad_risk",0,risk=.21),c("bad_governance",0,gov=False),c("bad_constraints",0,constraints=False)]:
    out=S.select_minimal_sufficient([x,c("safe",10)],minimum_quality=.8,maximum_risk=.2); assert out.get("selected_candidate",{}).get("candidate_id")=="safe",out
print("P002_CROWN_HARD_GATES_OK")
out=S.select_minimal_sufficient([c("boundary",0,quality=.8,risk=.2),c("expensive",1e300)],minimum_quality=.8,maximum_risk=.2); assert out.get("selected_candidate",{}).get("candidate_id")=="boundary"
for z in (-1.,float("nan"),float("inf"),float("-inf")):
    try: S.select_minimal_sufficient([c("x",z)],minimum_quality=.8,maximum_risk=.2)
    except (ValueError,TypeError): pass
    else: raise AssertionError(("INVALID_COST_ACCEPTED",z))
print("P002_CROWN_NUMERIC_BOUNDARIES_OK")
base=[c("collective",1),c("rule",1),c("small_neural",1)]
a=S.select_minimal_sufficient(base,minimum_quality=.8,maximum_risk=.2); b=S.select_minimal_sufficient(list(reversed(base)),minimum_quality=.8,maximum_risk=.2)
assert a.get("selected_candidate",{}).get("candidate_id")==b.get("selected_candidate",{}).get("candidate_id")=="collective",(a,b)
print("P002_CROWN_TIE_PERMUTATION_OK")
parts=[{"candidate_id":"apparently_cheap","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":.1,"coordination_cost":5.,"governance_cost":5.,"maintenance_cost":5.},{"candidate_id":"actually_cheap","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":1.,"coordination_cost":.1,"governance_cost":.1,"maintenance_cost":.1}]
out=S.select_minimal_sufficient(parts,minimum_quality=.8,maximum_risk=.2); assert out.get("selected_candidate",{}).get("candidate_id")=="actually_cheap",out
print("P002_CROWN_COMPONENT_COSTS_OK")
probe=c("probe",.01,execution_cost=1.,coordination_cost=5.,governance_cost=5.,maintenance_cost=5.)
safe={"candidate_id":"safe","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":2.,"coordination_cost":0.,"governance_cost":0.,"maintenance_cost":0.}
try: out=S.select_minimal_sufficient([probe,safe],minimum_quality=.8,maximum_risk=.2)
except (ValueError,TypeError): print("P002_CROWN_TOTAL_COMPONENT_CONFLICT_REJECTED_OK")
else:
    assert out.get("selected_candidate",{}).get("candidate_id")=="safe",("EXPLICIT_TOTAL_BYPASS",out)
    print("P002_CROWN_TOTAL_COMPONENT_CONFLICT_ACCOUNTED_OK")
print("P002_ADVERSARIAL_CROWN_OK")
