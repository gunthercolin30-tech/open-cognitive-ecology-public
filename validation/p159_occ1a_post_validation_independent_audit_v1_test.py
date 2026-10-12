from pathlib import Path
import copy, hashlib
from ontology import occ_post_validation_independent_audit as a
ROOT=Path(__file__).resolve().parents[1]
def main():
    files=[ROOT/a.MANIFEST_REL]+[ROOT/x for x in a.EXPECTED_PARTITIONS]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    x=a.audit(ROOT); y=a.audit(ROOT)
    assert x==y and x["decision"]==a.PASS and x["passed_count"]==x["check_count"]
    assert not x["blockers"] and x["read_only"]
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert before==after
    mb=(ROOT/a.MANIFEST_REL).read_bytes()
    parts={k:(ROOT/k).read_bytes() for k in a.EXPECTED_PARTITIONS}
    # Manifest tamper.
    z=a.audit(ROOT,manifest_bytes=mb+b"\n#tamper\n",partition_bytes=parts)
    assert z["decision"]==a.FAIL and "FAILED_MANIFEST_HASH_PINNED" in z["blockers"]
    # Partition tamper.
    p2=dict(parts); k=sorted(p2)[0]; p2[k]=p2[k]+b"\n#tamper\n"
    z=a.audit(ROOT,manifest_bytes=mb,partition_bytes=p2)
    assert z["decision"]==a.FAIL and "FAILED_PARTITION_HASHES_PINNED" in z["blockers"]
    # Missing partition.
    p3=dict(parts); p3.pop(sorted(p3)[0])
    try: z=a.audit(ROOT,manifest_bytes=mb,partition_bytes=p3)
    except Exception: pass
    else: assert z["decision"]==a.FAIL
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_FUNCTIONAL_OK")
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_DETERMINISM_OK")
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_NON_MUTATION_OK")
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_MANIFEST_TAMPER_OK")
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_PARTITION_TAMPER_OK")
    print("P159_OCC1A_POST_VALIDATION_INDEPENDENT_AUDIT_MISSING_PARTITION_OK")
    print("decision="+x["decision"])
    print("checks=%d/%d"%(x["passed_count"],x["check_count"]))
    print("blockers="+repr(x["blockers"]))
if __name__=="__main__": main()
