from copy import deepcopy
import pytest
from validation import p159_occ1k_independent_s10_replay_v1 as a
def test_real_replay_s10_pass():
 r=a.replay();assert r["s10_finding"]["result"]=="PASS" and r["coverage"]["rules"]==48
def test_existing_checker_reused(): assert a.replay()["checker_identity"]["parallel_checker_created"] is False
def test_runtime_claim_forbidden():
 s=a.replay()["semantic_scope"];assert not s["runtime_reachability_proven"] and not s["runtime_enforcement_proven"] and not s["p160_runtime_graph_claimed"]
def test_missing_rule_degradation():
 x=a.load(a.AC2);x=deepcopy(x);x["consolidated_rule_map"].pop(next(iter(x["consolidated_rule_map"])))
 with pytest.raises(RuntimeError):a.build_profile(x)
def test_orphan_consumer_degradation():
 x=deepcopy(a.load(a.AC2));k=next(iter(x["consolidated_rule_map"]));x["consolidated_rule_map"][k]["consumers"]=[]
 with pytest.raises(RuntimeError):a.build_profile(x)
def test_unknown_consumer_degradation():
 x=deepcopy(a.load(a.AC2));k=next(iter(x["consolidated_rule_map"]));x["consolidated_rule_map"][k]["consumers"]=["UnknownConsumer"]
 with pytest.raises(RuntimeError):a.build_profile(x)
def test_checker_rejects_unreachable():
 p=a.build_profile();k=next(iter(p["enforcement_coverage_map"]));p["enforcement_coverage_map"][k]["reachable"]=False
 c=a.checker_module();rep=c.check_profile(p,a.ROOT,a.sha(a.CNP));assert a.phase(rep,"S10")["result"]=="FAIL"
def test_boundaries():
 r=a.replay();assert not r["historical_occ1d_rewritten"] and not r["cnp_modified"] and not r["rule_bindings_modified"] and not r["p160b_opened"]
def test_deterministic(): assert a.replay()==a.replay()
