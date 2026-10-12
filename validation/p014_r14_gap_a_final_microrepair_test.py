#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ontology.dependency_registry import *
records=[
 {"dependency_id":"a","provider":"P1","criticality":"DC4","strategic":True,"evidence_state":"VERIFIED"},
 {"dependency_id":"b","provider":"P2","criticality":"DC2","strategic":False,"evidence_state":"VERIFIED"},
]
assert p014_r14_canonical_dependency_artifact(records,"1")["complete"]
assert p014_r14_complete_graph_contract(records,[("a","b")])["complete"]
assert p014_r14_assign_criticality(records)["complete"]
print("P014_R14_GAP_A_FINAL_MICROREPAIR_FUNCTIONAL_OK")
assert not p014_r14_complete_graph_contract(records,[("a","missing")])["complete"]
assert not p014_r14_assign_criticality([{"dependency_id":"x","criticality":"DC9"}])["complete"]
print("P014_R14_GAP_A_FINAL_MICROREPAIR_DEGRADATION_OK")
s=p014_r14_sovereignty_closure(records,[("a","b")])
assert isinstance(s["sovereignty_vectors"], list) and len(s["sovereignty_vectors"]) == len(records)
assert "PROVIDER_INDEPENDENCE_UNPROVEN" in s["closure_blockers"]
assert s["canonical_ready"] is False
print("P014_R14_GAP_A_FINAL_MICROREPAIR_NON_REGRESSION_OK")
