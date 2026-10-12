import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=json.loads((R/"validation_artifacts/p159/occ1i/f7a_consolidated_mroot_evidence_ledger_v1.json").read_text())
def ho(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def test_count(): assert D["mroot_expected_count"]==43 and D["case_count"]==43 and len(D["cases"])==43
def test_identity(): assert set(D["mroot_ids"])==set(D["cases"])
def test_unique_ids(): assert len(D["mroot_ids"])==len(set(D["mroot_ids"]))==43
def test_all_killed(): assert D["summary"]=={"killed":43,"inconclusive":0,"unresolved":0} and all(x["causal_verdict"]=="KILLED" for x in D["cases"].values())
def test_threshold(): assert all(x["minimum_distinct_detectors"]==2 for x in D["cases"].values())
def test_extended_exact(): assert sum(x["evidence_mode"]=="EXACT_CAUSAL" for x in D["cases"].values())==11
def test_core(): assert sum(x["campaign"]=="F4_CORE" for x in D["cases"].values())==32
def test_extended(): assert sum(x["campaign"]=="F6_EXTENDED" for x in D["cases"].values())==11
def test_hash(): x=dict(D); h=x.pop("ledger_identity_sha256"); assert h==ho(x)
def test_non_authorizing(): assert D["non_authorizing_derived_evidence"] is True and D["historical_artifacts_modified"] is False
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
def test_boundaries(): assert D["p159_final_lock"] is False and D["p160_opened"] is False
def test_next(): assert D["next_required_stage"]=="F7_B_META_MUTATION_CROWN"
