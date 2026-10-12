import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c3/semantic_residual_process_rescan.json"
def d(): return json.loads(R.read_text())
def test_partition_is_total():
 x=d(); assert x["syntactic_calls"]==x["already_mediated_calls"]+x["direct_residual_calls"]
def test_mediated_requires_governed_origin():
 for r in d()["calls"]:
  if r["classification"]=="ALREADY_MEDIATED":
   assert r["origin"].startswith("ontology.governed_git_")
def test_direct_never_marked_zero():
 x=d(); assert x["direct_residual_calls"]>0
 assert x["process_bypass_zero_claimed"] is False
 assert x["process_migration_complete"] is False
def test_no_execution_or_authorization_claim():
 x=d(); assert x["authorization_created"] is False and x["execution_performed"] is False
def test_no_p162g_closure():
 x=d(); assert x["p162g_closure_not_claimed"] is True and x["p162h_opened"] is False
