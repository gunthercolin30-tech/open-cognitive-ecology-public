from pathlib import Path
import hashlib, json, shutil, tempfile
from ontology import occ1a_post_lineage_exit_reaudit as q
ROOT=Path(__file__).resolve().parents[1]

def main():
    watched=[ROOT/"normative/occ1a/manifest.yaml",
             ROOT/"oif_review/campaigns/P159-OCC1A/occ1a_ordinary_norm_adoption_transaction_v1.json"]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched if p.is_file()}
    a=q.audit(ROOT)
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched if p.is_file()}
    assert before==after
    assert a["decision"]=="OCC1A_REMAINS_OPEN",a
    assert a["blocker_status"]["KERNEL_SEMANTIC_BINDING_STILL_UNRESOLVED"]=="RESOLVED_BY_CURRENT_EVIDENCE"
    assert a["blocker_status"]["SOURCE_LINEAGE_BINDING_STILL_UNRESOLVED"]=="RESOLVED_BY_CURRENT_EVIDENCE"
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_TWO_EVIDENCE_BLOCKERS_RESOLVED_OK")
    assert a["blocker_status"]["CANONICAL_PACKAGE_PRINCIPAL_KERNEL_NOT_POPULATED"]=="STILL_BLOCKING"
    assert a["blocker_status"]["CANONICAL_PACKAGE_STATE_DRAFT"]=="STILL_BLOCKING"
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_PHYSICAL_PACKAGE_BLOCKERS_PRESERVED_OK")
    assert a["blocker_status"]["6_DNA_L0_REQUIRE_REFOUNDING_OR_FORK_PATH"]=="REFORMULATED_REQUIRES_GOVERNED_KERNEL_REPRESENTATION_PROOF"
    assert a["l0_protected_constitutive_representation_available"] is True
    assert a["l0_refounding_or_fork_requirement_erased"] is False
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_L0_FAIL_CLOSED_REFORMULATION_OK")
    assert not a["package_population_performed"] and not a["package_state_changed"]
    assert not a["authority_activated"] and not a["execution_performed"]
    assert not a["occ1a_closed"] and not a["occ1b_opened"] and not a["p160_opened"]
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_STAGE_BOUNDARY_OK")
    assert q.audit(ROOT)==q.audit(ROOT)
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_DETERMINISM_OK")
    p,b=q.write_report(ROOT)
    c=json.loads(p.read_text(encoding="utf-8"))
    assert c==b
    print("P159_OCC1A_POST_LINEAGE_REAUDIT_REPORT_OK")
    print("decision="+a["decision"])
    print("resolved_blocker_count="+str(a["resolved_blocker_count"]))
    print("remaining_blockers="+json.dumps(a["remaining_blockers"]))
    print("occ1a_closed=false")
if __name__=="__main__": main()
