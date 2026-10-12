#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.strategy_selection import StrategySelection
S=StrategySelection()
def base(cid,**kw):
    d={"candidate_id":cid,"quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True}; d.update(kw); return d
def selected(o): return o.get("selected_candidate",{}).get("candidate_id")
x=base("equal",total_cognitive_cost=3.,execution_cost=1.,coordination_cost=2.)
o=S.select_minimal_sufficient([x],minimum_quality=.8,maximum_risk=.2)
assert selected(o)=="equal" and o["selected_candidate"]["cost_basis"]=="declared_total_validated_against_components",o
print("P002_BOUNDARY_EQUAL_FLOOR_OK")
x=base("over",total_cognitive_cost=5.,execution_cost=1.,maintenance_cost=1.)
o=S.select_minimal_sufficient([x],minimum_quality=.8,maximum_risk=.2)
assert selected(o)=="over" and o["selected_candidate"]["total_cognitive_cost"]==5.,o
print("P002_BOUNDARY_ABOVE_FLOOR_OK")
try: S.select_minimal_sufficient([base("epsilon",total_cognitive_cost=1.999999999999,execution_cost=1.,coordination_cost=1.)],minimum_quality=.8,maximum_risk=.2)
except ValueError: pass
else: raise AssertionError("declared total below component floor accepted")
print("P002_BOUNDARY_EPSILON_BELOW_REJECTED_OK")
try: S.select_minimal_sufficient([base("one",total_cognitive_cost=.5,governance_cost=1.)],minimum_quality=.8,maximum_risk=.2)
except ValueError: pass
else: raise AssertionError("single-component floor bypass accepted")
print("P002_BOUNDARY_SINGLE_COMPONENT_REJECTED_OK")
x=base("zero",total_cognitive_cost=.25,execution_cost=0.,coordination_cost=0.,governance_cost=0.,maintenance_cost=0.)
assert selected(S.select_minimal_sufficient([x],minimum_quality=.8,maximum_risk=.2))=="zero"
print("P002_BOUNDARY_ZERO_COMPONENTS_OK")
for field,value in (("execution_cost",-1.),("coordination_cost",float("nan")),("governance_cost",float("inf")),("maintenance_cost",float("-inf"))):
    x=base("invalid",total_cognitive_cost=100.); x[field]=value
    try: S.select_minimal_sufficient([x],minimum_quality=.8,maximum_risk=.2)
    except (ValueError,TypeError): pass
    else: raise AssertionError(("INVALID_COMPONENT_HIDDEN_BY_TOTAL",field,value))
print("P002_BOUNDARY_INVALID_COMPONENTS_REJECTED_OK")
a=base("ordered",total_cognitive_cost=4.,execution_cost=1.,coordination_cost=1.,governance_cost=1.,maintenance_cost=1.)
b=dict(reversed(list(a.items())))
oa=S.select_minimal_sufficient([a],minimum_quality=.8,maximum_risk=.2); ob=S.select_minimal_sufficient([b],minimum_quality=.8,maximum_risk=.2)
assert oa["selected_candidate"]==ob["selected_candidate"],(oa,ob)
print("P002_BOUNDARY_FIELD_ORDER_OK")
o=S.select_minimal_sufficient([base("legacy",total_cognitive_cost=.125)],minimum_quality=.8,maximum_risk=.2)
assert selected(o)=="legacy" and o["selected_candidate"]["cost_basis"]=="declared_total",o
print("P002_BOUNDARY_DECLARED_TOTAL_ONLY_OK")
print("P002_COST_INTEGRITY_BOUNDARY_CROWN_OK")
