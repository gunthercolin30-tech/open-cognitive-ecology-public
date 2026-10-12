from __future__ import annotations
import hashlib, shutil, tempfile
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()

def run_fixture(case_id, baseline_text, transform, detector, *, simulate_interrupt=False, simulate_contamination=False):
    parent=Path(tempfile.mkdtemp(prefix="oce_occ1i_")); ws=parent/"workspace"; ws.mkdir()
    base=ws/"fixture.txt"; base.write_text(baseline_text,encoding="utf-8"); before=sha(base)
    result={"case_id":case_id,"workspace_isolated":True,"baseline_sha256":before,"mutation_applied":False,
            "mutation_changed_hash":False,"detector_observed":False,"causal_evidence":None,
            "canonical_write":False,"status":"INCONCLUSIVE","interrupted":False,"workspace_destroyed":False}
    try:
        if simulate_interrupt:
            result["interrupted"]=True; return result
        mutated=transform(base.read_text(encoding="utf-8")); base.write_text(mutated,encoding="utf-8")
        after=sha(base); result["mutated_sha256"]=after; result["mutation_applied"]=True
        result["mutation_changed_hash"]=(after!=before)
        if not result["mutation_changed_hash"]:
            result["status"]="SEMANTICALLY_EQUIVALENT"; return result
        observed=bool(detector(mutated)); result["detector_observed"]=observed
        result["causal_evidence"]={"baseline_sha256":before,"mutated_sha256":after,"detector_observed":observed}
        result["status"]="KILLED" if observed else "SURVIVED"
        if simulate_contamination:
            result["canonical_write"]=True; result["status"]="INCONCLUSIVE"
        return result
    finally:
        shutil.rmtree(parent,ignore_errors=True); result["workspace_destroyed"]=not parent.exists()
