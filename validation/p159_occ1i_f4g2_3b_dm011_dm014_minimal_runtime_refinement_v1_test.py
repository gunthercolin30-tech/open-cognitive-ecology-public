import importlib.util,json
from pathlib import Path
R=Path(__file__).parents[1]
M=R/"ontology/occ_trust_boundaries.py"
D=json.loads((R/"validation_artifacts/p159/occ1i/f4g2_3b_dm011_dm014_minimal_runtime_refinement_v1.json").read_text())
def mod():
 s=importlib.util.spec_from_file_location("tb_g23b",M);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def base(authority="HUMAN_RESERVED",uncertainty="UNKNOWN"):
 return {"norm_id":"N","strength":"MUST","authority":authority,"scope":"LOCAL","temporal":"ACTIVE","uncertainty":uncertainty,"provenance":"P"}
def test_status(): assert D["status"]=="F4_G2_3B_MINIMAL_RUNTIME_REFINEMENT_COMPLETE"
def test_backup(): assert D["backup_created"] is True
def test_dm011():
 m=mod(); a=base(); b=dict(a,authority="AUTOMATED")
 x=m.evaluate_preservation(a,b); assert x["status"]=="FAIL" and x["reason"]=="HUMAN_RESERVED_AUTOMATION"
def test_dm014():
 m=mod(); a=base(); b=dict(a,uncertainty="TRUE")
 x=m.evaluate_preservation(a,b); assert x["status"]=="FAIL" and x["reason"]=="UNKNOWN_REQUIRED_PRECONDITION"
def test_nominal():
 m=mod(); a=base(); assert m.evaluate_preservation(a,dict(a))["status"]=="PASS"
def test_generic_authority_preserved():
 m=mod(); a=base(authority="CONSTITUTIONAL"); b=dict(a,authority="OTHER")
 assert m.evaluate_preservation(a,b)["reason"]=="AUTHORITY_WIDENING"
def test_fail_closed(): assert mod().fail_closed("HUMAN_RESERVED_AUTOMATION")["authorization"] is False
def test_no_toggle_api():
 import inspect; assert tuple(inspect.signature(mod().evaluate_preservation).parameters)==("source","compiled")
def test_no_create(): assert D["new_runtime_module_created"] is False
def test_scope(): assert D["modified_runtime_files"]==["ontology/occ_trust_boundaries.py"]
def test_next(): assert D["next_required_stage"]=="F4-G2.3C_DM011_DM014_EXACT_CAUSAL_REPLAYS"
def test_epistemic(): assert D["functional_conclusion_only"] and D["phenomenology_undetermined"]
