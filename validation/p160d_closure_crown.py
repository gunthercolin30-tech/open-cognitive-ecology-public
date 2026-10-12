import subprocess,sys
from ontology import p160_normative_conflict_detection as d

def main():
    r=subprocess.run([sys.executable,"-m","pytest","-q","validation/p160d_closure_crown_test.py"],capture_output=True,text=True)
    print(r.stdout,end="")
    if r.returncode:
        print(r.stderr,end="")
        raise SystemExit(r.returncode)
    m=d.manifest()
    assert m["scope"]=="P160-D_ONLY"
    assert "normative_conflict_resolution.resolve_conflict" in m["does_not_call"]
    assert m["boundaries"]["conflict_arbitration_performed"] is False
    assert m["boundaries"]["winner_selected"] is False
    assert m["boundaries"]["p160e_opened"] is False
    assert m["boundaries"]["p161_opened"] is False
    print("P160D_CLOSURE_CROWN=12/12")
    print("P160D_CLOSURE_CROWN_OK")
    print("P160E_OPENED=false")
    print("P161_OPENED=false")
    print("P160_FINAL_LOCK=false")

if __name__=="__main__":
    main()
