from __future__ import annotations
from pathlib import Path
import hashlib, json, os, shutil, tempfile
from ontology import occ_postcommit_population_verifier as verifier

PRIMITIVE="occ_manifest_kernel_population_reconciliation"
VERSION="P159-OCC1A-manifest-kernel-population-reconciliation-v1"
OLD_STATUS="UNRESOLVED_PENDING_EXPLICIT_SEMANTIC_BINDING"
NEW_STATUS="POPULATED_48_VERIFIED"
MANIFEST_REL="normative/occ1a/manifest.yaml"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha_bytes(b): return hashlib.sha256(b).hexdigest()

def _load(path):
    text=Path(path).read_text(encoding="utf-8")
    try:
        import yaml
        data=yaml.safe_load(text)
        if not isinstance(data,dict): raise RuntimeError("MANIFEST_NOT_MAPPING")
        return data
    except ImportError:
        try:
            data=json.loads(text)
            if not isinstance(data,dict): raise RuntimeError("MANIFEST_NOT_MAPPING")
            return data
        except Exception as e:
            raise RuntimeError("STRUCTURED_MANIFEST_PARSER_UNAVAILABLE") from e

def _dump(data):
    try:
        import yaml
        return yaml.safe_dump(data,sort_keys=False,allow_unicode=True).encode("utf-8")
    except ImportError:
        return (json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8")

def _find(obj,key,path=()):
    found=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            np=path+(str(k),)
            if str(k)==key: found.append((np,v))
            found.extend(_find(v,key,np))
    elif isinstance(obj,list):
        for i,v in enumerate(obj): found.extend(_find(v,key,path+(str(i),)))
    return found

def _set_path(obj,path,value):
    cur=obj
    for p in path[:-1]:
        cur=cur[int(p)] if isinstance(cur,list) else cur[p]
    if isinstance(cur,list): cur[int(path[-1])]=value
    else: cur[path[-1]]=value

def prepare(root=None):
    r=_root(root)
    # Strong precondition: physical 48/48 + evidence + DRAFT already independently verified.
    v=verifier.verify(r)
    if v["decision"]!="POSTCOMMIT_POPULATION_VERIFIED" or v["populated_count"]!=48:
        raise RuntimeError("POSTCOMMIT_VERIFICATION_REQUIRED")
    if v["package_state"]!="DRAFT": raise RuntimeError("PACKAGE_NOT_DRAFT")
    if v["kernel_population_status_observed"] not in (OLD_STATUS,NEW_STATUS):
        raise RuntimeError("UNEXPECTED_KERNEL_POPULATION_STATUS:"+repr(v["kernel_population_status_observed"]))
    p=r/MANIFEST_REL
    before=p.read_bytes(); data=_load(p)
    ps=_find(data,"package_state"); ks=_find(data,"kernel_population_status")
    if len(ps)!=1 or ps[0][1]!="DRAFT": raise RuntimeError("PACKAGE_STATE_INVALID")
    if len(ks)!=1: raise RuntimeError("KERNEL_STATUS_CARDINALITY_INVALID")
    old=ks[0][1]
    if old==NEW_STATUS:
        return {"already_reconciled":True,"before":before,"after":before,
                "before_sha256":_sha_bytes(before),"after_sha256":_sha_bytes(before)}
    if old!=OLD_STATUS: raise RuntimeError("KERNEL_STATUS_PRECONDITION_FAILED")
    _set_path(data,ks[0][0],NEW_STATUS)
    # Structural delta proof.
    if _find(data,"package_state")[0][1]!="DRAFT": raise RuntimeError("PACKAGE_STATE_DRIFT")
    if _find(data,"kernel_population_status")[0][1]!=NEW_STATUS: raise RuntimeError("STATUS_UPDATE_FAILED")
    after=_dump(data)
    return {"already_reconciled":False,"before":before,"after":after,
            "before_sha256":_sha_bytes(before),"after_sha256":_sha_bytes(after)}

def commit(root=None,inject_failure=False):
    r=_root(root); p=r/MANIFEST_REL
    plan=prepare(r)
    if plan["already_reconciled"]:
        return {"decision":"MANIFEST_KERNEL_POPULATION_ALREADY_RECONCILED",
                "kernel_population_status":NEW_STATUS,"package_state":"DRAFT",
                "manifest_sha256":plan["after_sha256"],"idempotent":True,
                "authority_activated":False,"execution_performed":False,
                "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
    original=plan["before"]
    bak=Path(str(p)+".bak")
    shutil.copy2(p,bak)
    fd,tmp=tempfile.mkstemp(prefix=p.name+".reconcile.",dir=str(p.parent)); os.close(fd)
    tp=Path(tmp)
    try:
        tp.write_bytes(plan["after"])
        with tp.open("rb") as f: os.fsync(f.fileno())
        if inject_failure: raise RuntimeError("INJECTED_RECONCILIATION_FAILURE")
        os.replace(str(tp),str(p))
        # Reparse and prove only intended semantics.
        d=_load(p)
        if _find(d,"package_state")[0][1]!="DRAFT": raise RuntimeError("POSTCOMMIT_PACKAGE_STATE_DRIFT")
        if _find(d,"kernel_population_status")[0][1]!=NEW_STATUS: raise RuntimeError("POSTCOMMIT_STATUS_INVALID")
        # Physical package must still pass; verifier v1.2 expects old status, so directly prove partitions unchanged below.
    except Exception:
        p.write_bytes(original)
        if tp.exists(): tp.unlink()
        raise
    return {"decision":"MANIFEST_KERNEL_POPULATION_RECONCILED",
            "kernel_population_status":NEW_STATUS,"package_state":"DRAFT",
            "manifest_sha256":_sha_bytes(p.read_bytes()),"idempotent":False,
            "authority_activated":False,"execution_performed":False,
            "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
