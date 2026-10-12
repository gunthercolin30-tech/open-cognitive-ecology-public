from pathlib import Path
from ontology import occ1h_h7_a075_common_tcb_resolution_probe as probe
ROOT=Path.home()/"open-cognitive-ecology"
def test_probe_is_diagnostic_only_and_non_promotional():
    r=probe.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE" and r["diagnostic_only"] is True
    assert r["a075_verdict_changed"] is False and r["historical_evidence_rewritten"] is False
    assert r["occ1f_modified"] is False and r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False and r["p159_final_lock"] is False and r["p160_opened"] is False
def test_probe_records_loaded_common_tcb_identities():
    r=probe.run(ROOT); c=r.get("observations",{}).get("child",{})
    if not c.get("child_failed") and "verifier" in c:
        assert c["verifier"]["sha256"]==probe.HISTORICAL_VERIFIER_SHA256
        assert c["builder_via_verifier"]["sha256"]==probe.HISTORICAL_BUILDER_SHA256
        assert c["nir"]["sha256"]==probe.HISTORICAL_NIR_SHA256
def test_probe_measures_actual_loaded_modules():
    r=probe.run(ROOT); c=r.get("observations",{}).get("child",{})
    if not c.get("child_failed") and "verifier" in c:
        assert c["verifier"]["inside_sandbox"] is True and c["builder_via_verifier"]["inside_sandbox"] is True and c["nir"]["inside_sandbox"] is True
        assert c["verifier_builder_module_name"]=="ontology.occ_normative_ir_real_builder"
def test_probe_never_claims_a075_resolution():
    r=probe.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE"
    assert r["reason"] not in ("ASSURANCE_GAP","RESISTED","DETECTED")
