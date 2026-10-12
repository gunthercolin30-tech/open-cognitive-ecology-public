from pathlib import Path
import json

SCHEMA="oce.p159.occ1a.governed_version_binding_resolver.v1.2"
LOCK_SCHEMA="oce.p110.final_lock.v1"
POST_SCHEMA="oce.p110.postlock.verification.v1"
SIGNAL="CONSTITUTIONAL_FINAL_LOCK_OK"

def _root(root=None): return Path(root) if root is not None else Path.home()/"open-cognitive-ecology"
def _load(p):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return None
def _walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from _walk(v)
    elif isinstance(x,list):
        for v in x: yield from _walk(v)
def _has(x,k,v): return any(d.get(k)==v for d in _walk(x) if k in d)
def _first(x,k):
    for d in _walk(x):
        if k in d: return d[k]
    return None
def _candidates(root,schema):
    out=[]
    for base in (root/"validation",root/"ontology"):
        if not base.exists(): continue
        for p in sorted(base.rglob("*.json")):
            d=_load(p)
            if isinstance(d,dict) and d.get("schema")==schema: out.append((p,d))
    return out

def resolve(root=None):
    r=_root(root); locks=_candidates(r,LOCK_SCHEMA); posts=_candidates(r,POST_SCHEMA); b=[]
    if len(locks)!=1: b.append("P110_CANONICAL_FINAL_LOCK_NOT_UNIQUE")
    if len(posts)!=1: b.append("P110_CANONICAL_POSTLOCK_NOT_UNIQUE")
    lp=pp=None; lock=post=None
    if len(locks)==1: lp,lock=locks[0]
    if len(posts)==1: pp,post=posts[0]
    ident=post_ident=None
    if lock is not None:
        if lock.get("milestone")!="P110": b.append("P110_FINAL_LOCK_MILESTONE_INVALID")
        if lock.get("status")!="LOCKED": b.append("P110_FINAL_LOCK_STATUS_INVALID")
        if lock.get("canonical_signal")!=SIGNAL: b.append("P110_FINAL_LOCK_SIGNAL_INVALID")
        if lock.get("constitutional_final_lock_ok") is not True: b.append("P110_FINAL_LOCK_BOOLEAN_INVALID")
        for k in ("CONSTITUTION_LOCKED","DNA_CONSTITUTIVE_LOCKED","GOVERNANCE_ENGINE_VALIDATED"):
            if not _has(lock,k,True): b.append("P110_"+k+"_MISSING")
        ident=_first(lock,"final_lock_identity_sha256")
        if not isinstance(ident,str) or len(ident)!=64: b.append("P110_FINAL_LOCK_IDENTITY_INVALID")
    if post is not None:
        checks=post.get("checks")
        if not isinstance(checks,dict): checks={}
        if post.get("milestone")!="P110": b.append("P110_POSTLOCK_MILESTONE_INVALID")
        if post.get("status")!="POSTLOCK_VERIFIED": b.append("P110_POSTLOCK_STATUS_INVALID")
        if post.get("canonical_signal")!=SIGNAL: b.append("P110_POSTLOCK_SIGNAL_INVALID")
        if checks.get("identity_exact") is not True: b.append("P110_POSTLOCK_IDENTITY_NOT_EXACT")
        if checks.get("identity_recomputed") is not True: b.append("P110_POSTLOCK_IDENTITY_NOT_RECOMPUTED")
        if checks.get("protected_artifact_drift_absent") is not True: b.append("P110_POSTLOCK_PROTECTED_DRIFT_CHECK_FAILED")
        if post.get("protected_artifact_drift") is not False: b.append("P110_POSTLOCK_PROTECTED_DRIFT_PRESENT")
        if checks.get("final_lock_sha_exact") is not True: b.append("P110_POSTLOCK_FINAL_LOCK_SHA_NOT_EXACT")
        probes=post.get("tamper_probes")
        if not isinstance(probes,list) or len(probes)<1 or not all(isinstance(x,dict) and x.get("rejected") is True for x in probes):
            b.append("P110_POSTLOCK_TAMPER_PROBES_INVALID")
        post_ident=post.get("final_lock_identity_sha256")
        if not isinstance(post_ident,str) or len(post_ident)!=64: b.append("P110_POSTLOCK_IDENTITY_INVALID")
    if ident and post_ident and ident!=post_ident: b.append("P110_LOCK_POSTLOCK_IDENTITY_DIVERGENCE")
    b=sorted(set(b)); ok=not b
    return {"schema":SCHEMA,"status":"GOVERNED_VERSION_BINDINGS_RESOLVED" if ok else "GOVERNED_VERSION_BINDINGS_BLOCKED",
      "blockers":b,
      "constitution_version":("P110:"+SIGNAL+":"+ident) if ok else None,
      "governance_version":("P110:GOVERNANCE_ENGINE_VALIDATED:"+ident) if ok else None,
      "p110_final_lock_identity_sha256":ident if ok else None,
      "p110_final_lock_path":str(lp.relative_to(r)) if lp else None,
      "p110_postlock_path":str(pp.relative_to(r)) if pp else None,
      "read_only":True,"normative_effect":False,"authority_activated":False,"adoption_performed":False,
      "execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
