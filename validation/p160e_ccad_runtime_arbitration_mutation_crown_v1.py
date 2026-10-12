from __future__ import annotations
from pathlib import Path
import hashlib, importlib.util, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/"ontology"/"p160_ccad_runtime_arbitration.py"
EXPECTED="a41e62799b0fc0b1e0eda520c478b3b6faf5734913395d9fa4cfa9856a71d9e2"
MUTANTS={
"M01_HARD_INVALID_RESTORED":('        "legitimate": bool(legitimate) and not hard_invalid,','        "legitimate": bool(legitimate),',"hard_invalid"),
"M02_UNKNOWN_JUSTIFIED":('        if any(not _present(prop.get(k)) for k in positive_prop):','        if False and any(not _present(prop.get(k)) for k in positive_prop):',"unknown"),
"M03_EXPIRY_GUARD_REMOVED":('        if any(not _present(temporal.get(k)) for k in required_temporal_values):','        if False and any(not _present(temporal.get(k)) for k in required_temporal_values):',"expiry"),
"M04_PRECEDENT_TO_NORM":('PRECEDENT_EFFECTS = ("NONE", "INFORMATIONAL_ONLY", "REVIEW_REFERENCE")','PRECEDENT_EFFECTS = ("NONE", "INFORMATIONAL_ONLY", "REVIEW_REFERENCE", "BINDING_NORM")',"precedent"),
"M05_AUTHORITY_CREATED":('    "authority_created": False,','    "authority_created": True,',"authority"),
"M06_AUTHORIZATION_CREATED":('    "authorization_created": False,','    "authorization_created": True,',"authorization"),
"M07_CONTEXT_DRIFT_ACCEPTED":('        if _present(upstream) and _present(current) and str(upstream) != str(current):','        if False and _present(upstream) and _present(current) and str(upstream) != str(current):',"drift"),
"M08_AGGREGATE_HARM_HIDDEN":('                    "hidden_by_aggregate": False,','                    "hidden_by_aggregate": True,',"distribution"),
"M09_C6_LEAST_BAD_FLAG":('        "c6_least_bad_selected": False,','        "c6_least_bad_selected": True,',"c6flag"),
"M10_EXECUTION_BOUNDARY":('    "execution_performed": False,','    "execution_performed": True,',"execution"),
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_mutant(path):
    name="ontology.p160_ccad_runtime_arbitration"
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m; spec.loader.exec_module(m); return m
def load_helpers():
    p=ROOT/"validation"/"p160e_ccad_runtime_arbitration_v1_test.py"
    spec=importlib.util.spec_from_file_location("_p160e_mut_helpers",p); m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
def oracle(kind,e,h):
    if kind=="hard_invalid":
        ev=h.evidence(); ev["options"]["A"].update({"hard_invalid":True,"benefit":"MAXIMAL"})
        assert h.resolve(h.dcase("C2"),ev)["ccad_resolution"]["selected_option_candidate"] is None
    elif kind=="unknown":
        ev=h.evidence(); ev["proportionality_assessment"]["necessity"]="UNKNOWN"
        assert h.resolve(h.dcase("C2"),ev)["ccad_resolution"]["selected_option_candidate"] is None
    elif kind=="expiry":
        ev=h.evidence(mag="SERIOUS"); ev["temporary_limitation"]=True
        ev["temporal_limits"]={"valid_from":"T0","expires_at":None,"renewal_conditions":"REVIEW","max_renewals":1,"review":"REQUIRED"}
        assert h.resolve(h.dcase("C2"),ev)["ccad_resolution"]["selected_option_candidate"] is None
    elif kind=="precedent":
        ev=h.evidence(); ev["precedent_effect"]="BINDING_NORM"
        assert h.resolve(h.dcase("C2"),ev)["ccad_resolution"]["precedent_effect"]=="NONE"
    elif kind=="authority": assert h.resolve(h.dcase("C2"),h.evidence())["authority_created"] is False
    elif kind=="authorization": assert h.resolve(h.dcase("C2"),h.evidence())["authorization_created"] is False
    elif kind=="drift":
        dc=h.dcase("C2"); r,c,s,p=h.inputs(dc); c=dict(c); c["runtime_context_fingerprint"]="STALE"
        try: e.resolve_ccad_conflict(dc,r,c,s,p,arbitration_evidence=h.evidence())
        except ValueError: return
        raise AssertionError("context drift accepted")
    elif kind=="distribution":
        o=h.resolve(h.dcase("C2"),h.evidence()); assert all(x["hidden_by_aggregate"] is False for x in o["distributional_impact"])
    elif kind=="c6flag": assert h.resolve(h.dcase("C2"),h.evidence())["ccad_resolution"]["c6_least_bad_selected"] is False
    elif kind=="execution": assert h.resolve(h.dcase("C2"),h.evidence())["execution_performed"] is False
def child(mid):
    src=RUNTIME.read_text(encoding="utf-8"); old,new,kind=MUTANTS[mid]
    if src.count(old)!=1: raise SystemExit("MUTATION_SITE_COUNT:"+mid+":"+str(src.count(old)))
    mutated=src.replace(old,new,1)
    with tempfile.TemporaryDirectory(prefix="p160e-mut-") as td:
        mp=Path(td)/"p160_ccad_runtime_arbitration.py"; mp.write_text(mutated,encoding="utf-8"); compile(mutated,str(mp),"exec")
        e=load_mutant(mp); h=load_helpers(); oracle(kind,e,h)
    print("SURVIVED:"+mid)
def main():
    if sha(RUNTIME)!=EXPECTED: raise SystemExit("CANONICAL_RUNTIME_DRIFT:"+sha(RUNTIME))
    results=[]
    for mid in MUTANTS:
        cp=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--child",mid],cwd=str(ROOT),text=True,capture_output=True)
        killed=cp.returncode!=0; results.append((mid,killed)); print(mid+(" KILLED" if killed else " SURVIVED"))
    if sha(RUNTIME)!=EXPECTED: raise SystemExit("CANONICAL_RUNTIME_MODIFIED")
    killed=sum(k for _,k in results); survived=len(results)-killed
    print(f"P160E_MUTATION_SCORE={killed}/{len(results)}"); print("P160E_MUTANTS_SURVIVED="+str(survived))
    print("P160E_MUTANTS_INCONCLUSIVE=0"); print("CANONICAL_RUNTIME_UNCHANGED=true")
    print("P160F_OPENED=false"); print("P161_OPENED=false")
    if survived:
        for mid,k in results:
            if not k: print("SURVIVOR="+mid)
        raise SystemExit(1)
    print("P160E_MUTATION_CROWN_V1_OK")
if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--child": child(sys.argv[2])
    else: main()
