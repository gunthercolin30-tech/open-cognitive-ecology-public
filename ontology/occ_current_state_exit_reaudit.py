from pathlib import Path
import hashlib, json
from ontology import occ_independent_institutional_authority_verifier as authority
from ontology import occ_atomic_ordinary_norm_adoption_transaction as atomic
from ontology import occ_post_validation_independent_audit as post_validation

SCHEMA="oce.p159.occ1a.current_state_exit_reaudit.v2"
DEC_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
POST_REL=Path("validation/evidence/p159_occ1a/occ1a_human_decisions_postcampaign_audit_v1.json")
LEDGER_REL=atomic.LEDGER_REL
PKG_REL=Path("normative/occ1a")

def _root(root=None):
    return Path(root) if root else Path.home()/"open-cognitive-ecology"

def _load(p):
    text=Path(p).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        import yaml
        return yaml.safe_load(text)

def _single(obj,key):
    found=[]
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if str(k)==key:
                    found.append(v)
                walk(v)
        elif isinstance(x,list):
            for v in x:
                walk(v)
    walk(obj)
    return found[0] if len(found)==1 else None

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def _hash(v):
    return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()

def _strict_ledger(r):
    p=r/LEDGER_REL
    if not p.is_file():
        return {"valid":False,"reason":"LEDGER_MISSING"}
    base=atomic.verify_ledger(p)
    if base.get("status")!="COMMITTED_VALID" or base.get("valid") is not True:
        return {"valid":False,"reason":base.get("reason") or base.get("status","LEDGER_INVALID")}
    x=_load(p); tx=x.get("transaction") or {}; events=tx.get("events") or []
    envelope_false=("authority_activated","package_materialized","execution_performed",
                    "occ1a_closed","occ1b_opened","p160_opened")
    if any(x.get(k) is not False for k in envelope_false):
        return {"valid":False,"reason":"ENVELOPE_STAGE_BOUNDARY_VIOLATION"}
    if any(tx.get(k) is not False for k in envelope_false):
        return {"valid":False,"reason":"TRANSACTION_STAGE_BOUNDARY_VIOLATION"}
    if tx.get("functional_conclusion_only") is not True or tx.get("phenomenology_undetermined") is not True:
        return {"valid":False,"reason":"EPISTEMIC_INVARIANT_VIOLATION"}
    ids=[e.get("canonical_id") for e in events]
    if tuple(ids)!=atomic.ORDINARY or len(set(ids))!=17:
        return {"valid":False,"reason":"EVENT_TARGET_ORDER_OR_UNIQUENESS_INVALID"}
    if any(e.get("state")!="ADOPTED" or e.get("authority_activated") is not False or
           e.get("runtime_execution_enabled") is not False or e.get("p104_persisted") is not False
           for e in events):
        return {"valid":False,"reason":"EVENT_STAGE_BOUNDARY_VIOLATION"}
    if any(cid in atomic.DNA_L0 for cid in ids):
        return {"valid":False,"reason":"DNA_L0_PRESENT_IN_ORDINARY_LEDGER"}
    return {"valid":True,"status":"COMMITTED_VALID","event_count":17,
            "transaction_hash":tx.get("transaction_hash"),"ledger_sha256":_sha(p)}

def collect_evidence(root=None, authority_result=None):
    r=_root(root)
    manifest=_load(r/PKG_REL/"manifest.yaml")
    decisions=_load(r/DEC_REL)
    historical_post=_load(r/POST_REL)
    auth=authority_result if authority_result is not None else authority.verify(r)
    ledger=_strict_ledger(r)
    pv=post_validation.audit(r)

    rows=decisions.get("rows",[])
    ordinary=[x for x in rows if x.get("layer") in ("DNA_H","DNA_L1")]
    l0=[x for x in rows if x.get("layer")=="DNA_L0"]
    ordinary_decisions=[x for x in ordinary if x.get("decision")=="ADOPT" and x.get("out_of_band_confirmation") is True]
    l0_decisions=[x for x in l0 if x.get("decision")]

    return {
      "manifest":manifest,
      "manifest_sha256":_sha(r/PKG_REL/"manifest.yaml"),
      "post_validation":pv,
      "ledger":ledger,
      "ordinary_count":len(ordinary),
      "ordinary_confirmed_count":len(ordinary_decisions),
      "l0_count":len(l0),
      "l0_decision_count":len(l0_decisions),
      "historical_postcampaign_preserved":
          historical_post.get("human_decision_is_normative_adoption") is False and
          historical_post.get("adoption_performed") is False,
      "authority":auth,
      "source_hashes":{
        "decisions":_sha(r/DEC_REL),
        "postcampaign":_sha(r/POST_REL),
        "ordinary_adoption_ledger":_sha(r/LEDGER_REL) if (r/LEDGER_REL).is_file() else None}
    }

def evaluate(e):
    pv=e.get("post_validation") or {}
    ledger=e.get("ledger") or {}
    auth=e.get("authority") or {}
    manifest=e.get("manifest") or {}
    pv_checks=pv.get("checks") or {}

    checks={
      "ordinary_human_decisions_17":
          e.get("ordinary_count")==17 and e.get("ordinary_confirmed_count")==17,
      "dna_l0_reserved_6_without_ordinary_decision":
          e.get("l0_count")==6 and e.get("l0_decision_count")==0,
      "ordinary_adoption_ledger_committed_valid_17":
          ledger.get("valid") is True and ledger.get("status")=="COMMITTED_VALID" and ledger.get("event_count")==17,
      "institutional_authority_verified":
          auth.get("status")=="INDEPENDENT_AUTHORITY_VERIFICATION_OK" and
          auth.get("institutional_authority_established") is True,
      "authority_not_activated":
          auth.get("authority_activated") is False,
      "package_state_validated":
          pv.get("package_state")=="VALIDATED" and _single(manifest,"package_state")=="VALIDATED",
      "kernel_population_verified":
          pv.get("kernel_population_status")=="POPULATED_48_VERIFIED" and
          _single(manifest,"kernel_population_status")=="POPULATED_48_VERIFIED",
      "post_validation_independent_audit_20_of_20":
          pv.get("decision")==post_validation.PASS and
          pv.get("check_count")==20 and pv.get("passed_count")==20 and not pv.get("blockers"),
      "semantic_binding_complete":
          pv_checks.get("semantic_binding_complete") is True,
      "source_lineage_complete":
          pv_checks.get("source_lineage_complete") is True,
      "l0_protection_preserved":
          pv_checks.get("l0_protection_preserved") is True and
          pv_checks.get("l0_representation_proven") is True,
      "genesis_no_machine_invention":
          pv_checks.get("genesis_no_invention") is True,
      "h9_f12_f17_distinct_f18_excluded":
          pv_checks.get("h9_f12_f17_distinct") is True and
          pv_checks.get("f18_excluded_from_h9") is True,
      "epistemic_invariants":
          pv.get("functional_conclusion_only") is True and
          pv.get("phenomenology_undetermined") is True,
      "stage_boundaries_preserved":
          pv.get("authority_activated") is False and
          pv.get("execution_performed") is False and
          pv.get("occ1a_closed") is False and
          pv.get("occ1b_opened") is False and
          pv.get("p160_opened") is False
    }
    blockers=sorted("FAILED_"+k.upper() for k,v in checks.items() if v is not True)
    ready=not blockers
    return {
      "schema":SCHEMA,
      "decision":"OCC1A_READY_TO_CLOSE" if ready else "OCC1A_REMAINS_OPEN",
      "check_count":len(checks),
      "passed_count":sum(v is True for v in checks.values()),
      "current_blockers":blockers,
      "checks":checks,
      "ordinary_committed_adoption_count":17 if checks["ordinary_adoption_ledger_committed_valid_17"] else 0,
      "dna_l0_reserved_count":e.get("l0_count"),
      "institutional_authority_established":checks["institutional_authority_verified"],
      "package_state":pv.get("package_state"),
      "kernel_population_status":pv.get("kernel_population_status"),
      "manifest_sha256":pv.get("manifest_sha256"),
      "historical_postcampaign_preserved":e.get("historical_postcampaign_preserved") is True,
      "authority_activated":False,
      "execution_performed":False,
      "occ1a_closed":False,
      "occ1b_opened":False,
      "p160_opened":False,
      "closure_performed":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
      "ordinary_adoption_ledger":ledger,
      "source_hashes":e.get("source_hashes") or {}
    }

def audit(root=None, authority_result=None):
    return evaluate(collect_evidence(root,authority_result))

def main():
    a=audit()
    print("P159_OCC1A_CURRENT_STATE_EXIT_REAUDIT_V2_OK")
    print("decision="+a["decision"])
    print("checks=%d/%d"%(a["passed_count"],a["check_count"]))
    for b in a["current_blockers"]:
        print("BLOCKER="+b)
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__":
    main()
