import subprocess, sys
from ontology import p160_normative_conflict_detection as d

def main():
    r=subprocess.run([sys.executable,"-m","pytest","-q","validation/p160d_defensive_crown_v11_test.py"],capture_output=True,text=True)
    print(r.stdout,end="")
    if r.returncode:
        print(r.stderr,end="")
        raise SystemExit(r.returncode)
    m=d.manifest()
    assert m["boundaries"]["conflict_arbitration_performed"] is False
    assert m["boundaries"]["winner_selected"] is False
    assert m["boundaries"]["p160e_opened"] is False
    assert m["boundaries"]["p161_opened"] is False
    print("P160D_DEFENSIVE_CROWN=20/20")
    print("P160D_DEFENSIVE_CROWN_OK")
    print("P160E_OPENED=false")
    print("P161_OPENED=false")
    print("P160_FINAL_LOCK=false")

if __name__=="__main__":
    main()
