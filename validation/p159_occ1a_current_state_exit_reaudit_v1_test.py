from pathlib import Path
import hashlib, json, tempfile, shutil
from ontology import occ_current_state_exit_reaudit as q
ROOT=Path(__file__).resolve().parents[1]

def hashes():
 paths=[ROOT/q.PKG_REL/"manifest.yaml",ROOT/q.PKG_REL/"provenance/source_lineage.yaml",
        ROOT/q.DEC_REL,ROOT/q.POST_REL,ROOT/q.LEDGER_REL]
 return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def copy_min(t):
 rels=[q.PKG_REL/"manifest.yaml",q.PKG_REL/"provenance/source_lineage.yaml",q.DEC_REL,q.POST_REL,q.LEDGER_REL,
       Path("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json")]
 for rel in rels:
  src=ROOT/rel; dst=t/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
 for rel in q.historical.PARTS:
  src=ROOT/q.PKG_REL/rel; dst=t/q.PKG_REL/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)

def fake_auth():
 return {"status":"INDEPENDENT_AUTHORITY_VERIFICATION_OK","institutional_authority_established":True,"authority_activated":False}

def rewrite_ledger(t, mutate):
 p=t/q.LEDGER_REL; x=json.loads(p.read_text(encoding="utf-8")); mutate(x)
 p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def main():
 before=hashes(); a=q.audit(ROOT); after=hashes()
 assert before==after
 assert a["decision"]=="OCC1A_REMAINS_OPEN",a
 assert a["adoption_performed"] is True
 assert a["ordinary_committed_adoption_count"]==17
 assert a["ordinary_adoption_ledger"]["status"]=="COMMITTED_VALID"
 s=a["historical_blocker_reassessment"]
 assert s["CANONICAL_PACKAGE_PRINCIPAL_KERNEL_NOT_POPULATED"]["classification"]=="STILL_BLOCKING"
 assert s["KERNEL_SEMANTIC_BINDING_STILL_UNRESOLVED"]["classification"]=="STILL_BLOCKING"
 assert s["SOURCE_LINEAGE_BINDING_STILL_UNRESOLVED"]["classification"]=="STILL_BLOCKING"
 assert s["23_DNA_BINDINGS_ARE_PROPOSED_NOT_ADOPTED"]["classification"]=="REFORMULATED_STILL_BLOCKING"
 assert s["23_DNA_BINDINGS_ARE_PROPOSED_NOT_ADOPTED"]["replacement_blockers"]==["6_DNA_L0_REQUIRE_REFOUNDING_OR_FORK_PATH"]
 assert s["CANONICAL_PACKAGE_STATE_DRAFT"]["classification"]=="STILL_BLOCKING"
 assert "17_ORDINARY_GOVERNED_DECISIONS_EXIST_BUT_NORMATIVE_ADOPTION_NOT_PERFORMED" not in a["current_blockers"]
 assert "17_ORDINARY_GOVERNED_NORM_ADOPTIONS_NOT_COMMITTED_VALID" not in a["current_blockers"]
 assert "6_DNA_L0_REQUIRE_REFOUNDING_OR_FORK_PATH" in a["current_blockers"]
 assert a["checks"]["historical_postcampaign_preserved"] is True
 assert a["authority_activated"] is False and a["execution_performed"] is False
 assert a["occ1b_opened"] is False and a["p160_opened"] is False
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_FUNCTIONAL_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t); (t/q.LEDGER_REL).unlink()
  x=q.audit(t,authority_result=fake_auth())
  assert x["adoption_performed"] is False
  assert "17_ORDINARY_GOVERNED_NORM_ADOPTIONS_NOT_COMMITTED_VALID" in x["current_blockers"]
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_LEDGER_LOSS_DEGRADATION_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t)
  rewrite_ledger(t,lambda x:x.__setitem__("authority_activated",True))
  x=q.audit(t,authority_result=fake_auth())
  assert x["adoption_performed"] is False
  assert x["ordinary_adoption_ledger"]["reason"]=="ENVELOPE_STAGE_BOUNDARY_VIOLATION"
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_ENVELOPE_TAMPER_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t)
  def mut(x):
   x["transaction"]["authority_activated"]=True
   z={k:v for k,v in x["transaction"].items() if k!="transaction_hash"}
   x["transaction"]["transaction_hash"]=q._hash(z)
  rewrite_ledger(t,mut)
  x=q.audit(t,authority_result=fake_auth())
  assert x["adoption_performed"] is False
  assert x["ordinary_adoption_ledger"]["reason"]=="TRANSACTION_STAGE_BOUNDARY_VIOLATION"
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_CORE_STAGE_TAMPER_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t)
  def mut16(x):
   tx=x["transaction"]; tx["events"]=tx["events"][:-1]; tx["event_count"]=16; tx["target_ids"]=tx["target_ids"][:-1]
   z={k:v for k,v in tx.items() if k!="transaction_hash"}; tx["transaction_hash"]=q._hash(z)
  rewrite_ledger(t,mut16)
  x=q.audit(t,authority_result=fake_auth())
  assert x["adoption_performed"] is False
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_16_OF_17_REJECT_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t)
  def mutl0(x):
   tx=x["transaction"]; e=tx["events"][0]; e["canonical_id"]="DNA.L0.1"
   z=dict(e); z.pop("event_hash",None); e["event_hash"]=q._hash(z)
   tx["target_ids"][0]="DNA.L0.1"; z={k:v for k,v in tx.items() if k!="transaction_hash"}; tx["transaction_hash"]=q._hash(z)
  rewrite_ledger(t,mutl0)
  x=q.audit(t,authority_result=fake_auth())
  assert x["adoption_performed"] is False
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_DNA_L0_INJECTION_REJECT_OK")

 with tempfile.TemporaryDirectory() as td:
  t=Path(td); copy_min(t)
  pp=t/q.POST_REL; post=json.loads(pp.read_text()); post["adoption_performed"]=True
  pp.write_text(json.dumps(post,sort_keys=True),encoding="utf-8")
  x=q.audit(t,authority_result=fake_auth())
  assert x["checks"]["historical_postcampaign_preserved"] is False
  assert x["adoption_performed"] is True
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_HISTORICAL_EVIDENCE_NONAUTHORITATIVE_OK")

 a2=q.audit(ROOT); assert a==a2
 print("P159_OCC1A_POSTADOPTION_EXIT_REAUDIT_DETERMINISM_OK")
 print("decision="+a["decision"])
 print("ordinary_committed_adoption_count="+str(a["ordinary_committed_adoption_count"]))
 print("dna_l0_reserved_count="+str(a["dna_l0_reserved_count"]))
 for b in a["current_blockers"]: print("BLOCKER="+b)
 print("authority_activated=false"); print("execution_performed=false")
 print("occ1a_closed=false"); print("occ1b_opened=false"); print("p160_opened=false")
if __name__=="__main__": main()
