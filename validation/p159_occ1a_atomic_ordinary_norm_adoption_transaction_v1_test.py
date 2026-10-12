from pathlib import Path
import json,tempfile
from ontology import occ_atomic_ordinary_norm_adoption_transaction as t
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=t.prepare(ROOT);assert p["status"]=="PREPARED",p;assert p["prepared_count"]==17;assert len(p["transaction"]["events"])==17
 assert tuple(p["transaction"]["target_ids"])==t.ORDINARY;assert tuple(p["transaction"]["excluded_dna_l0_ids"])==t.DNA_L0
 assert all(e["p104_persisted"] is False and e["authority_activated"] is False and e["runtime_execution_enabled"] is False for e in p["transaction"]["events"])
 assert t.prepare(ROOT)["transaction"]["transaction_hash"]==p["transaction"]["transaction_hash"]
 with tempfile.TemporaryDirectory() as td:
  lp=Path(td)/"ledger.json";f=t.commit(ROOT,lp,fail_after=8);assert f["status"]=="BLOCKED";assert not lp.exists()
  c=t.commit(ROOT,lp);assert c["status"]=="COMMITTED" and c["committed_event_count"]==17;assert t.verify_ledger(lp)["status"]=="COMMITTED_VALID"
  assert t.commit(ROOT,lp)["status"]=="COMMITTED_IDEMPOTENT"
  x=json.loads(lp.read_text());x["transaction"]["events"][0]["state"]="ALTERED";lp.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
  assert t.verify_ledger(lp)["status"]=="TAMPERED";assert t.commit(ROOT,lp)["status"]=="REJECTED"
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_FUNCTIONAL_OK")
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_FAILURE_ROLLBACK_17_TO_0_OK")
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_IDEMPOTENCE_OK")
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_TAMPER_REPLAY_OK")
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_DNA_L0_EXCLUDED_OK")
 print("P159_OCC1A_ATOMIC_ORDINARY_NORM_ADOPTION_TRANSACTION_V1_STAGE_BOUNDARY_OK")
 print("transaction_target_count=17");print("dna_l0_committed_count=0");print("real_ledger_not_written_by_test=true")
if __name__=="__main__":main()
