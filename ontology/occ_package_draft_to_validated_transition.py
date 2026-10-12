from __future__ import annotations
from pathlib import Path
import hashlib, json, os, shutil, tempfile
from ontology import occ_package_validation_readiness_audit as readiness
from ontology import occ_manifest_kernel_population_reconciliation as manifestio
from ontology import occ_postcommit_population_verifier as pv
from ontology import occ_canonical_principal_kernel_population as population

PRIMITIVE="occ_package_draft_to_validated_transition"
VERSION="P159-OCC1A-package-draft-to-validated-transition-v1.1"
MANIFEST_REL="normative/occ1a/manifest.yaml"
FROM_STATE="DRAFT"; TO_STATE="VALIDATED"; KERNEL_STATUS="POPULATED_48_VERIFIED"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha(b): return hashlib.sha256(b).hexdigest()
def _file_sha(p): return _sha(Path(p).read_bytes())
def _state(data,key):
    x=manifestio._find(data,key)
    if len(x)!=1: raise RuntimeError(key.upper()+"_CARDINALITY_INVALID")
    return x[0]
def _fingerprint(root):
    r=_root(root); files=[r/MANIFEST_REL]+[r/x for x in pv.PARTITIONS]
    return {str(p.relative_to(r)):_file_sha(p) for p in files}

def verify_validated(root=None):
    r=_root(root); p=r/MANIFEST_REL; d=manifestio._load(p)
    if _state(d,"package_state")[1]!=TO_STATE: raise RuntimeError("PACKAGE_NOT_VALIDATED")
    if _state(d,"kernel_population_status")[1]!=KERNEL_STATUS: raise RuntimeError("KERNEL_STATUS_DRIFT")
    payloads={x:(r/x).read_bytes() for x in pv.PARTITIONS}
    if not population.verify_plan(payloads): raise RuntimeError("PHYSICAL_KERNEL_INVALID")
    expected=population.plan(r)
    disk={x:_sha(payloads[x]) for x in pv.PARTITIONS}
    exp={x:_sha(expected[x]) for x in pv.PARTITIONS}
    if disk!=exp: raise RuntimeError("PARTITIONS_DIFFER_FROM_VALIDATED_EVIDENCE")
    return {"decision":"VALIDATED_PACKAGE_INDEPENDENTLY_REVERIFIED",
      "package_state":TO_STATE,"kernel_population_status":KERNEL_STATUS,
      "manifest_sha256":_file_sha(p),"partition_sha256":disk,
      "package_validation_performed":True,"authority_activated":False,
      "execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}

def prepare(root=None):
    r=_root(root); p=r/MANIFEST_REL; before=p.read_bytes(); d=manifestio._load(p)
    ps=_state(d,"package_state"); ks=_state(d,"kernel_population_status")
    if ks[1]!=KERNEL_STATUS: raise RuntimeError("KERNEL_STATUS_NOT_RECONCILED")
    # Critical v1.1 fix: recognize and independently verify committed state BEFORE DRAFT readiness.
    if ps[1]==TO_STATE:
        verified=verify_validated(r)
        return {"already_validated":True,"before":before,"after":before,
          "fingerprint":_fingerprint(r),"before_sha256":_sha(before),"after_sha256":_sha(before),
          "validated_verification":verified}
    if ps[1]!=FROM_STATE: raise RuntimeError("INVALID_SOURCE_STATE:"+repr(ps[1]))
    a=readiness.audit(r)
    if a["decision"]!=readiness.READY or a["passed_count"]!=a["check_count"] or a["blockers"]:
        raise RuntimeError("PACKAGE_NOT_READY:"+json.dumps(a["blockers"],sort_keys=True))
    manifestio._set_path(d,ps[0],TO_STATE)
    if _state(d,"package_state")[1]!=TO_STATE or _state(d,"kernel_population_status")[1]!=KERNEL_STATUS:
        raise RuntimeError("STATE_DELTA_INVALID")
    after=manifestio._dump(d)
    return {"already_validated":False,"before":before,"after":after,
      "fingerprint":_fingerprint(r),"before_sha256":_sha(before),"after_sha256":_sha(after)}

def commit(root=None, expected_fingerprint=None, inject_failure=False):
    r=_root(root); p=r/MANIFEST_REL
    plan=prepare(r)
    if plan["already_validated"]:
        v=plan["validated_verification"]
        return {"decision":"PACKAGE_ALREADY_VALIDATED","package_state":TO_STATE,
          "kernel_population_status":KERNEL_STATUS,"manifest_sha256":v["manifest_sha256"],
          "idempotent":True,"package_validation_performed":True,
          "authority_activated":False,"execution_performed":False,
          "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
    current=_fingerprint(r); expected=expected_fingerprint if expected_fingerprint is not None else plan["fingerprint"]
    if current!=expected: raise RuntimeError("PRECOMMIT_FINGERPRINT_DRIFT")
    a=readiness.audit(r)
    if a["decision"]!=readiness.READY or a["blockers"]: raise RuntimeError("READINESS_CHANGED_BEFORE_COMMIT")
    original=plan["before"]; part_before={x:_file_sha(r/x) for x in pv.PARTITIONS}
    bak=Path(str(p)+".bak"); shutil.copy2(p,bak)
    fd,tmp=tempfile.mkstemp(prefix=p.name+".validate.",dir=str(p.parent)); os.close(fd); tp=Path(tmp)
    try:
        tp.write_bytes(plan["after"])
        with tp.open("rb") as f: os.fsync(f.fileno())
        if inject_failure: raise RuntimeError("INJECTED_VALIDATION_FAILURE")
        os.replace(str(tp),str(p))
        verify_validated(r)
        if part_before!={x:_file_sha(r/x) for x in pv.PARTITIONS}: raise RuntimeError("PARTITION_MUTATION_DETECTED")
    except Exception:
        p.write_bytes(original)
        if tp.exists(): tp.unlink()
        raise
    return {"decision":"PACKAGE_DRAFT_TO_VALIDATED_COMMITTED","package_state":TO_STATE,
      "kernel_population_status":KERNEL_STATUS,"manifest_sha256":_file_sha(p),"idempotent":False,
      "package_validation_performed":True,"authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
