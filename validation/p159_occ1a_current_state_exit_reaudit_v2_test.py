from pathlib import Path
from copy import deepcopy
import hashlib
from ontology import occ_current_state_exit_reaudit as q
ROOT=Path(__file__).resolve().parents[1]

def protected_hashes():
    paths=[ROOT/q.PKG_REL/"manifest.yaml",ROOT/q.DEC_REL,ROOT/q.POST_REL,ROOT/q.LEDGER_REL]
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def must_block(base, mutate, expected):
    x=deepcopy(base); mutate(x); r=q.evaluate(x)
    assert r["decision"]=="OCC1A_REMAINS_OPEN",r
    assert expected in r["current_blockers"],r

def main():
    before=protected_hashes()
    evidence=q.collect_evidence(ROOT)
    a=q.evaluate(evidence)
    b=q.audit(ROOT)
    after=protected_hashes()
    assert before==after
    assert a==b
    assert a["decision"]=="OCC1A_READY_TO_CLOSE",a
    assert a["passed_count"]==a["check_count"]==15,a
    assert a["current_blockers"]==[]
    assert a["ordinary_committed_adoption_count"]==17
    assert a["dna_l0_reserved_count"]==6
    assert a["package_state"]=="VALIDATED"
    assert a["kernel_population_status"]=="POPULATED_48_VERIFIED"
    assert a["authority_activated"] is False and a["execution_performed"] is False
    assert a["occ1a_closed"] is False and a["occ1b_opened"] is False and a["p160_opened"] is False
    assert a["closure_performed"] is False
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_FUNCTIONAL_OK")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_NON_MUTATION_OK")

    must_block(evidence,lambda x:x["post_validation"].__setitem__("package_state","DRAFT"),
               "FAILED_PACKAGE_STATE_VALIDATED")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_PACKAGE_STATE_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"].__setitem__("kernel_population_status","UNRESOLVED"),
               "FAILED_KERNEL_POPULATION_VERIFIED")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_KERNEL_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"]["checks"].__setitem__("semantic_binding_complete",False),
               "FAILED_SEMANTIC_BINDING_COMPLETE")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_SEMANTIC_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"]["checks"].__setitem__("source_lineage_complete",False),
               "FAILED_SOURCE_LINEAGE_COMPLETE")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_LINEAGE_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"]["checks"].__setitem__("l0_protection_preserved",False),
               "FAILED_L0_PROTECTION_PRESERVED")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_L0_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"].__setitem__("decision","POST_VALIDATION_INDEPENDENT_AUDIT_BLOCKED"),
               "FAILED_POST_VALIDATION_INDEPENDENT_AUDIT_20_OF_20")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_POSTVALIDATION_DEGRADATION_OK")

    must_block(evidence,lambda x:x["ledger"].__setitem__("valid",False),
               "FAILED_ORDINARY_ADOPTION_LEDGER_COMMITTED_VALID_17")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_LEDGER_DEGRADATION_OK")

    must_block(evidence,lambda x:x["authority"].__setitem__("authority_activated",True),
               "FAILED_AUTHORITY_NOT_ACTIVATED")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_AUTHORITY_DEGRADATION_OK")

    must_block(evidence,lambda x:x["post_validation"].__setitem__("occ1b_opened",True),
               "FAILED_STAGE_BOUNDARIES_PRESERVED")
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_STAGE_BOUNDARY_OK")

    c=q.audit(ROOT)
    assert b==c
    assert protected_hashes()==before
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_DETERMINISM_OK")
    print("decision="+a["decision"])
    print("checks=%d/%d"%(a["passed_count"],a["check_count"]))
    print("blockers="+repr(a["current_blockers"]))
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__":
    main()
