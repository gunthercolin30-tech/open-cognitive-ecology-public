from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, json, tempfile

from ontology import occ_normative_ir as nir
from ontology import occ_constitutional_compiled_profile_independent_verifier as verifier

PASS,FAIL="PASS","FAIL"
VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
SCHEMA="oce.p159.occ1h.h4.execution.v1"

ATTACKS=(
 ("A031","dead norm elimination"),
 ("A032","unsafe constant folding"),
 ("A033","conjunction simplification"),
 ("A034","exception insertion"),
 ("A035","implicit normative defaults"),
 ("A036","unsourced restrictive invention"),
 ("A037","human to automatic transformation"),
 ("A038","two norms to one"),
 ("A039","review requirement removal"),
 ("A040","expiry removal"),
 ("A041","sunset removal"),
 ("A042","purpose broadening"),
)

def _write(p,o):
    p.write_text(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")

def _rehash_profile(p):
    q={k:deepcopy(v) for k,v in p.items() if k!="profile_sha256"}
    p["profile_sha256"]=nir.canonical_sha256(q)

def _launder_tx(tx,profile,profile_path):
    t=deepcopy(tx)
    t["payload"]["profile_sha256"]=profile["profile_sha256"]
    t["payload"]["profile_artifact_sha256"]=hashlib.sha256(profile_path.read_bytes()).hexdigest()
    h=nir.canonical_sha256(t["payload"])
    t["payload_sha256"]=h
    t["transaction_id"]=h
    return t

def _verify_mutation(source_root,base_profile,base_tx,mutator):
    with tempfile.TemporaryDirectory(prefix="oce-occ1h-h4-") as td:
        td=Path(td); pp=td/"profile.json"; tp=td/"tx.json"
        p=deepcopy(base_profile); mutator(p); _rehash_profile(p); _write(pp,p)
        t=_launder_tx(base_tx,p,pp); _write(tp,t)
        r=verifier.verify(source_root,pp,tp)
        return r

def _row(aid,label,verdict,reason,evidence=None):
    return {"attack_id":aid,"family_id":"H4","implementation_label":label,
            "success_criteria_fixed_before_execution":True,
            "injection_effective":verdict!="INCONCLUSIVE",
            "detector":"OCC1C_INDEPENDENT_SEMANTIC_VERIFIER" if verdict!="INCONCLUSIVE" else "REPRESENTATION_BOUNDARY",
            "observed_reason":reason,"verdict":verdict,
            "causal_evidence":evidence or {},
            "authorization_created":False,"execution_performed":False}

def run(root:Path):
    root=Path(root)
    source=root/"normative/occ1a"
    pp=root/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
    tp=root/"validation_artifacts/p159/occ1c/compilation_transaction_v1.json"
    base=json.loads(pp.read_text(encoding="utf-8"))
    tx=json.loads(tp.read_text(encoding="utf-8"))
    baseline=verifier.verify(source,pp,tp)
    if baseline.get("status")!=PASS:
        raise RuntimeError("OCC1C_BASELINE_NOT_INDEPENDENTLY_VERIFIED:%r"%baseline)

    human_idx=next((i for i,r in enumerate(base["rules"]) if r.get("human_judgment_required") is True),None)
    rows=[]

    mutations={
      "A031":lambda p:p["rules"].pop(),
      "A032":lambda p:p["rules"][0].__setitem__("text","TRUE"),
      "A033":lambda p:p["rules"][0].__setitem__("text","SIMPLIFIED_CONJUNCTION"),
      "A034":lambda p:p["rules"][0].__setitem__("text",str(p["rules"][0].get("text"))+" EXCEPT_UNSOURCED"),
      "A035":lambda p:p["compiler_contract"].__setitem__("compiler_invents_normative_defaults",True),
      "A036":lambda p:p["rules"].append(dict(deepcopy(p["rules"][0]),norm_id="UNSOURCED.RESTRICTIVE.INVENTION")),
      "A037":lambda p:p["rules"][human_idx].__setitem__("machine_formalization_claimed",True),
      "A038":lambda p:p["rules"].pop(1),
      "A039":lambda p:p["rules"][human_idx].__setitem__("human_judgment_required",False),
    }
    labels=dict(ATTACKS)
    for aid in ("A031","A032","A033","A034","A035","A036","A037","A038","A039"):
        if human_idx is None and aid in ("A037","A039"):
            rows.append(_row(aid,labels[aid],"INCONCLUSIVE","NO_HUMAN_REVIEW_RULE_IN_CURRENT_PROFILE"))
            continue
        r=_verify_mutation(source,base,tx,mutations[aid])
        if r.get("status")==FAIL:
            rows.append(_row(aid,labels[aid],"DETECTED",r.get("reason","FAIL"),
                             {"findings":r.get("findings",[]),"field_diffs":r.get("field_diffs",[])[:4]}))
        else:
            rows.append(_row(aid,labels[aid],"VIOLATED","MUTATED_PROFILE_ACCEPTED_BY_INDEPENDENT_VERIFIER"))

    # C09 explicitly records temporal source absence. There is therefore no
    # source-backed expiry/sunset field that H4 may legitimately delete.
    bounded=set(base.get("bounded_source_absence") or [])
    for aid,label in (("A040",labels["A040"]),("A041",labels["A041"])):
        reason="C09_TEMPORAL_SOURCE_ABSENT_NO_SOURCE_BACKED_FIELD_TO_REMOVE" if "C09_TEMPORAL" in bounded else "TEMPORAL_REPRESENTATION_NOT_PROVEN"
        rows.append(_row(aid,label,"INCONCLUSIVE",reason))

    # The OCC-1C v1 projection has no purpose field. Do not invent one merely
    # to obtain a favorable adversarial verdict.
    has_purpose=any("purpose" in r for r in base.get("rules",[]))
    if has_purpose:
        def mut(p): p["rules"][0]["purpose"]="UNSOURCED_BROAD_PURPOSE"
        r=_verify_mutation(source,base,tx,mut)
        verdict="DETECTED" if r.get("status")==FAIL else "VIOLATED"
        rows.append(_row("A042",labels["A042"],verdict,r.get("reason","MUTATED_PROFILE_ACCEPTED")))
    else:
        rows.append(_row("A042",labels["A042"],"INCONCLUSIVE","NO_PURPOSE_FIELD_IN_CURRENT_OCC1C_PROFILE"))

    counts={v:sum(1 for r in rows if r["verdict"]==v) for v in VERDICTS}
    return {"schema":SCHEMA,"version":"P159-OCC1H-H4-executable-v1",
            "family_id":"H4","scenario_count":12,"rows":rows,"verdict_counts":counts,
            "baseline_independently_verified":True,
            "success_criteria_fixed_before_execution":True,
            "inconclusive_not_resisted":True,"normative_auto_rewrite":False,
            "authorization_created":False,"execution_performed":False,
            "functional_only":True,"phenomenology_undetermined":True,
            "occ1h_closed":False,"occ1i_opened":False,
            "p159_final_lock":False,"p160_opened":False}
