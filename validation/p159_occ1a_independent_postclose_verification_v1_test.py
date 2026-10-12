from pathlib import Path
from copy import deepcopy
import hashlib, json
from ontology import occ_occ1a_independent_postclose_verification as q
from ontology import occ_occ1a_atomic_closing_transaction as closing
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/closing.ARTIFACT_REL

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def must_block(raw, mutate, expected):
    env=json.loads(raw.decode("utf-8")); mutate(env)
    bad=json.dumps(env,sort_keys=True,indent=2).encode("utf-8")
    a=q.audit(ROOT,bad)
    assert a["decision"]==q.FAIL,a
    assert expected in a["blockers"],a

def main():
    assert ART.is_file(),ART
    before=sha(ART)
    a=q.audit(ROOT); b=q.audit(ROOT)
    assert a==b
    assert a["decision"]==q.PASS,a
    assert a["passed_count"]==a["check_count"]==18,a
    assert a["blockers"]==[]
    assert a["occ1a_closed"] is True
    assert a["occ1b_opened"] is False and a["p160_opened"] is False
    assert a["authority_activated"] is False and a["execution_performed"] is False
    assert a["final_lock_performed"] is False
    assert a["read_only"] is True
    assert sha(ART)==before
    print("P159_OCC1A_POSTCLOSE_V1_FUNCTIONAL_OK")
    print("P159_OCC1A_POSTCLOSE_V1_DETERMINISM_OK")
    print("P159_OCC1A_POSTCLOSE_V1_NON_MUTATION_OK")

    raw=ART.read_bytes()
    must_block(raw,lambda x:x["transaction"].__setitem__("occ1b_opened",True),"FAILED_TRANSACTION_HASH_RECONSTRUCTED")
    print("P159_OCC1A_POSTCLOSE_V1_TAMPER_OK")
    must_block(raw,lambda x:x["transaction"].__setitem__("manifest_sha256","0"*64),"FAILED_TRANSACTION_HASH_RECONSTRUCTED")
    print("P159_OCC1A_POSTCLOSE_V1_MANIFEST_TAMPER_OK")
    must_block(raw,lambda x:x["transaction"].__setitem__("final_lock_performed",True),"FAILED_TRANSACTION_HASH_RECONSTRUCTED")
    print("P159_OCC1A_POSTCLOSE_V1_FINAL_LOCK_BOUNDARY_OK")
    must_block(raw,lambda x:x.__setitem__("status","BROKEN"),"FAILED_ENVELOPE_CONTRACT")
    print("P159_OCC1A_POSTCLOSE_V1_ENVELOPE_TAMPER_OK")

    missing=q.audit(ROOT,b"")
    assert missing["decision"]==q.FAIL and "FAILED_ARTIFACT_PARSEABLE" in missing["blockers"],missing
    print("P159_OCC1A_POSTCLOSE_V1_MISSING_OR_INVALID_ARTIFACT_OK")
    assert sha(ART)==before
    print("P159_OCC1A_POSTCLOSE_V1_TEST_OK")
if __name__=="__main__": main()
