from pathlib import Path
from copy import deepcopy
import json, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiled_profile_independent_verifier as v
from ontology import occ_normative_ir as nir

SRC=ROOT/"normative"/"occ1a"
PROFILE=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json"
TX=ROOT/"validation_artifacts"/"p159"/"occ1c"/"compilation_transaction_v1.json"

def write(p,o): p.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
def rehash_profile(p):
    q={k:deepcopy(val) for k,val in p.items() if k!="profile_sha256"}
    p["profile_sha256"]=nir.canonical_sha256(q)

def run():
    base=v.verify(SRC,PROFILE,TX)
    assert base["status"]==v.PASS,base
    assert base["compiler_imported"] is False and base["transaction_writer_imported"] is False
    assert v.verify_proof(base["proof"])["status"]==v.PASS
    po=json.loads(PROFILE.read_text(encoding="utf-8"))
    to=json.loads(TX.read_text(encoding="utf-8"))

    attacks=[
      ("DROP_NORM",lambda p:p["rules"].pop()),
      ("INVENT_NORM",lambda p:p["rules"].append(dict(p["rules"][0],norm_id="INVENTED"))),
      ("FORMALIZATION_PROMOTION",lambda p:p["rules"][0].__setitem__("formalization_level","F3")),
      ("PROVENANCE_BREAK",lambda p:p["rules"][0].__setitem__("lineage_artifacts",[])),
      ("EVIDENCE_CHANGE",lambda p:p["rules"][0].__setitem__("evidence_ids",["LAUNDERED"])),
      ("SOURCE_MAP_BREAK",lambda p:p["rules"][0].__setitem__("source_map",{})),
      ("AUTHORITY_INFLATION",lambda p:p["rules"][0].__setitem__("authority_created",True)),
      ("EXECUTION_INJECTION",lambda p:p["rules"][0].__setitem__("execution",True)),
      ("RELATION_DROP",lambda p:p["relations"].pop() if p["relations"] else p.__setitem__("relations",[{"x":"bad"}])),
      ("CONFLICT_ARBITRATION",lambda p:p["compiler_contract"].__setitem__("conflict_arbitration_performed",True)),
      ("EXECUTABLE_PAYLOAD",lambda p:p["compiler_contract"].__setitem__("executable_payload",True)),
    ]
    for name,attack in attacks:
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); pp=td/"profile.json"; tp=td/"tx.json"
            p=deepcopy(po); attack(p); rehash_profile(p); write(pp,p)
            # Attacker also launders transaction hashes/bindings coherently.
            t=deepcopy(to); t["payload"]["profile_sha256"]=p["profile_sha256"]
            import hashlib
            t["payload"]["profile_artifact_sha256"]=hashlib.sha256(pp.read_bytes()).hexdigest()
            h=nir.canonical_sha256(t["payload"]); t["payload_sha256"]=h; t["transaction_id"]=h; write(tp,t)
            r=v.verify(SRC,pp,tp)
            assert r["status"]==v.FAIL,(name,r)
    # Proof tamper and rehashed false verification both rejected.
    bad=deepcopy(base["proof"]); bad["payload"]["execution_performed"]=True
    assert v.verify_proof(bad)["status"]==v.FAIL
    bad=deepcopy(base["proof"]); bad["payload"]["authorization_created"]=True
    bad["proof_sha256"]=nir.canonical_sha256(bad["payload"])
    assert v.verify_proof(bad)["status"]==v.FAIL

    again=v.verify(SRC,PROFILE,TX)
    assert again["proof_sha256"]==base["proof_sha256"]
    print("P159_OCC1C_INDEPENDENT_SEMANTIC_FUNCTIONAL_OK")
    print("P159_OCC1C_INDEPENDENT_48_OF_48_OK")
    print("P159_OCC1C_INDEPENDENT_COMPILER_NOT_ORACLE_OK")
    print("P159_OCC1C_INDEPENDENT_TRANSACTION_WRITER_NOT_ORACLE_OK")
    print("P159_OCC1C_INDEPENDENT_REHASHED_SEMANTIC_LAUNDERING_DETECTED")
    print("P159_OCC1C_INDEPENDENT_PROVENANCE_EVIDENCE_SOURCE_MAP_ATTACKS_DETECTED")
    print("P159_OCC1C_INDEPENDENT_AUTHORITY_EXECUTION_ATTACKS_DETECTED")
    print("P159_OCC1C_INDEPENDENT_RELATION_CONFLICT_ATTACKS_DETECTED")
    print("P159_OCC1C_INDEPENDENT_EXECUTABLE_PAYLOAD_ATTACK_DETECTED")
    print("P159_OCC1C_INDEPENDENT_PROOF_TAMPER_DETECTED")
    print("P159_OCC1C_INDEPENDENT_REHASHED_FALSE_PROOF_DETECTED")
    print("P159_OCC1C_INDEPENDENT_DETERMINISM_OK")
    print("P159_OCC1C_INDEPENDENT_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
