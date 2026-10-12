from copy import deepcopy
from pathlib import Path
import hashlib, json, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compilation_transaction as tx
from ontology import occ_normative_ir as nir

SRC=ROOT/"normative"/"occ1a"
PROOF=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_postclose_verification.json"

def ident(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.name.endswith(".bak")}

def run():
    before=ident(SRC)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); profile=td/"profile.json"; art=td/"tx.json"
        a=tx.commit(SRC,PROOF,profile,art)
        assert a["status"]==tx.PASS,a
        assert a["profile_state"]=="UNVERIFIED_COMPILED_PROFILE"
        assert a["compiled_rules"]==48
        assert a["independent_semantic_verification_performed"] is False
        assert a["occ1d_opened"] is False and a["p160_opened"] is False
        assert before==ident(SRC)

        # Idempotent exact replay.
        b=tx.commit(SRC,PROOF,profile,art)
        assert b["status"]==tx.PASS and b["transaction_id"]==a["transaction_id"]

        # Transaction tamper detected.
        obj=json.loads(art.read_text(encoding="utf-8"))
        bad=deepcopy(obj); bad["payload"]["execution_performed"]=True
        assert tx.verify_transaction(bad)["status"]==tx.FAIL

        # Rehashed semantic laundering still rejected by semantic contract.
        bad=deepcopy(obj); bad["payload"]["authorization_created"]=True
        h=nir.canonical_sha256(bad["payload"]); bad["payload_sha256"]=h; bad["transaction_id"]=h
        r=tx.verify_transaction(bad)
        assert r["status"]==tx.FAIL and r["reason"]=="TRANSACTION_SEMANTICS_INVALID",r

        # Divergent profile replay rejected.
        original=profile.read_text(encoding="utf-8")
        po=json.loads(original); po["rules"][0]["text"]="MUTATED"
        profile.write_text(json.dumps(po,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
        r=tx.commit(SRC,PROOF,profile,art)
        assert r["status"]==tx.FAIL and r["reason"]=="DIVERGENT_PROFILE_REPLAY_REJECTED",r
        profile.write_text(original,encoding="utf-8")

        # Divergent transaction replay rejected.
        original_tx=art.read_text(encoding="utf-8")
        to=json.loads(original_tx); to["payload"]["independent_semantic_verification_performed"]=True
        art.write_text(json.dumps(to,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
        r=tx.commit(SRC,PROOF,profile,art)
        assert r["status"]==tx.FAIL and r["reason"]=="DIVERGENT_TRANSACTION_REPLAY_REJECTED",r

    assert before==ident(SRC)
    print("P159_OCC1C_TRANSACTION_FUNCTIONAL_OK")
    print("P159_OCC1C_TRANSACTION_48_OF_48_OK")
    print("P159_OCC1C_TRANSACTION_IDEMPOTENCE_OK")
    print("P159_OCC1C_TRANSACTION_TAMPER_DETECTED")
    print("P159_OCC1C_TRANSACTION_REHASHED_LAUNDERING_DETECTED")
    print("P159_OCC1C_TRANSACTION_DIVERGENT_PROFILE_REPLAY_REJECTED")
    print("P159_OCC1C_TRANSACTION_DIVERGENT_TX_REPLAY_REJECTED")
    print("P159_OCC1C_TRANSACTION_SOURCE_IMMUTABILITY_OK")
    print("P159_OCC1C_TRANSACTION_PROFILE_REMAINS_UNVERIFIED_OK")
    print("P159_OCC1C_TRANSACTION_NO_AUTHORIZATION_NO_EXECUTION_OK")
    print("P159_OCC1C_TRANSACTION_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
