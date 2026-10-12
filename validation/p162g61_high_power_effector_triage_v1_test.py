import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/"validation_artifacts/p162/p162g/g6"
R=json.loads((A/"g61_high_power_triage.json").read_text())
def test_all_53_occurrences_accounted_for():
 assert sum(R["primitive_occurrence_counts"].values())==53
 assert R["primitive_occurrence_counts"]=={"DATABASE":5,"NETWORK":7,"PROCESS":41}
def test_42_modules_accounted_for(): assert R["source_module_count"]==42
def test_real_network_paths_are_bypass():
 for p in ["ontology/github_publication_connector.py","ontology/openrouter_autonomous_provider_adapter.py","ontology/real_chatgpt_autonomous_api_adapter.py"]:
  e=next(x for x in R["entries"] if x["path"]==p);assert e["classification"]=="DIRECT_BYPASS_CONFIRMED" and e["migration_required"] is True
def test_live_ssh_scp_is_bypass():
 e=next(x for x in R["entries"] if x["path"]=="ontology/live_state_synchronizer.py");assert e["classification"]=="DIRECT_BYPASS_CONFIRMED"
def test_read_only_git_context_is_not_migration_target():
 e=next(x for x in R["entries"] if x["path"]=="ontology/scientific_publication_registry.py");assert e["classification"]=="NONCAUSAL_VERIFIED" and e["migration_required"] is False
def test_ambiguous_generic_command_wrappers_remain_blocking():
 e=next(x for x in R["entries"] if x["path"]=="ontology/real_cloud_node_deployment_validator.py");assert e["classification"]=="REVIEW_REQUIRED" and e["migration_required"] is None
def test_no_false_closure():
 assert R["status"]=="OPEN_MIGRATION_REQUIRED"
 d=json.loads((A/"g61_effector_mediation_registry.json").read_text())
 assert d["historical_effector_migration_complete"] is False
