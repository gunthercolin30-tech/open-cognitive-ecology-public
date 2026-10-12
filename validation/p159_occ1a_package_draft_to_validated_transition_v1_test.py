from pathlib import Path
import hashlib
from ontology import occ_package_draft_to_validated_transition as q
from ontology import occ_postcommit_population_verifier as pv
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=ROOT/q.MANIFEST_REL
    before=hashlib.sha256(manifest.read_bytes()).hexdigest()
    parts={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in pv.PARTITIONS}
    p=q.prepare(ROOT)
    assert not p["already_validated"]
    assert p["before_sha256"]==before and p["after_sha256"]!=before
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==before
    assert parts=={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in pv.PARTITIONS}
    # Fingerprint drift rejection without touching disk.
    bad=dict(p["fingerprint"]); bad[q.MANIFEST_REL]="0"*64
    try: q.commit(ROOT,expected_fingerprint=bad)
    except RuntimeError as e: assert "PRECOMMIT_FINGERPRINT_DRIFT" in str(e)
    else: raise AssertionError("DRIFT_NOT_REJECTED")
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==before
    print("P159_OCC1A_PACKAGE_TRANSITION_READINESS_PRECONDITION_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_SINGLE_STATE_DELTA_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_FINGERPRINT_DRIFT_REJECTED_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_PREPARE_NON_MUTATION_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_READY")
if __name__=="__main__": main()
