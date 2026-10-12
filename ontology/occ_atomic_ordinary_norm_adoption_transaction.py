from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,os,tempfile
from ontology import occ_norm_adoption_event as adoption
from ontology import occ_governed_ordinary_norm_adoption_preflight as preflight
from ontology import occ_independent_institutional_authority_verifier as authority_verifier
from ontology import human_reserved_authority_registry as p095
SCHEMA="oce.p159.occ1a.atomic_ordinary_norm_adoption_transaction.v1"
LEDGER_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_ordinary_norm_adoption_transaction_v1.json")
DEC_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json")
DOS_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_institutional_authority_amendment_dossier.json")
DECL_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
BIND_REL=Path("oif_review/campaigns/P159-OCC1A/occ1a_norm_adoption_authority_context_binding.json")
ORDINARY=tuple([f"DNA.H{i}" for i in range(1,10)]+[f"DNA.L1.{i}" for i in range(1,9)])
DNA_L0=tuple(f"DNA.L0.{i}" for i in range(1,7)); REQUIRED_CONTEXT="P159_OCC1A_NORM_ADOPTION"
def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _binding_ok(r,b):
 return b.get("status")=="HUMAN_CONFIRMED" and b.get("human_confirmed") is True and b.get("binding_kind")=="EXPLICIT_CONTEXT_BINDING_ONLY" and b.get("additional_context")==REQUIRED_CONTEXT and b.get("source_authority_declaration_sha256")==_sha(r/DECL_REL) and b.get("human_confirmation_text")==b.get("required_exact_confirmation") and all(b.get(k) is False for k in ("new_human_holder","new_reserved_function","new_action_class","authority_expansion","root_override_all","dna_l0_ordinary_override","delegation","succession","authority_activated","adoption_performed","package_materialized","execution_performed","occ1a_closed","occ1b_opened","p160_opened"))
def _registry(r,d,b):
 av=authority_verifier.verify(r)
 if av.get("status")!="INDEPENDENT_AUTHORITY_VERIFICATION_OK" or av.get("institutional_authority_established") is not True: raise ValueError("INSTITUTIONAL_AUTHORITY_NOT_VERIFIED")
 if not _binding_ok(r,b): raise ValueError("GOVERNED_CONTEXT_BINDING_INVALID")
 x=p095.P095Canonical()
 a=p095.HumanAuthority(d["authority_id"],d["holder"],d["authenticated"],p095.INITIAL_DEVELOPMENT_ROLE,d["mandate"],tuple(d["scope"]),("DEVELOPMENT",REQUIRED_CONTEXT),int(d["valid_from"]),int(d["valid_until"]),d["constitution_version"],d["governance_version"],0,None,False)
 if x.register_authority(a).get("status")!=p095.PASS: raise ValueError("P095_AUTHORITY_REGISTRATION_FAILED")
 e=p095.ReservedEntry("P159-OCC1A-R1","CONSTITUTIONAL_CHANGE",("OCC1A",),(p095.INITIAL_DEVELOPMENT_ROLE,),1,1,False,int(d["valid_until"]))
 if x.register_reserved(e).get("status")!=p095.PASS: raise ValueError("P095_RESERVED_ENTRY_FAILED")
 return x
def prepare(root=None,fail_after=None):
 r=_root(root); pf=preflight.audit(r)
 if pf.get("decision")!="READY_FOR_17_ORDINARY_ADOPTIONS": return {"status":"BLOCKED","reason":"PREFLIGHT_NOT_READY","adoption_performed":False}
 ds=_load(r/DEC_REL); dos=_load(r/DOS_REL); d=_load(r/DECL_REL); b=_load(r/BIND_REL)
 rows={x["canonical_id"]:x for x in ds["rows"] if x.get("layer") in ("DNA_H","DNA_L1")}; l0={x["canonical_id"]:x for x in ds["rows"] if x.get("layer")=="DNA_L0"}
 if set(rows)!=set(ORDINARY): return {"status":"BLOCKED","reason":"ORDINARY_TARGET_SET_MISMATCH","adoption_performed":False}
 if set(l0)!=set(DNA_L0) or any(x.get("ordinary_adoption_permitted") is not False for x in l0.values()): return {"status":"BLOCKED","reason":"DNA_L0_EXCLUSION_INVALID","adoption_performed":False}
 db={x["canonical_id"]:x for x in dos["dossiers"]}
 try: reg=_registry(r,d,b)
 except Exception as e: return {"status":"BLOCKED","reason":str(e),"adoption_performed":False}
 events=[]
 for i,cid in enumerate(ORDINARY,1):
  if fail_after is not None and i>int(fail_after): return {"status":"BLOCKED","reason":"INJECTED_PRECOMMIT_FAILURE","prepared_count":len(events),"adoption_performed":False}
  h=rows[cid]; z=db.get(cid,{})
  if h.get("decision")!="ADOPT" or h.get("out_of_band_confirmation") is not True: return {"status":"BLOCKED","reason":"HUMAN_DECISION_INVALID","canonical_id":cid,"adoption_performed":False}
  g=adoption.bind_registered_proposal(cid,proposal_hash=h["proposal_hash"],dossier_hash=h["dossier_hash"],evidence_snapshot_hash=h["evidence_snapshot_hash"],candidate_definition=h["candidate_definition"],evidence_ids=h["evidence_ids"],root=r)
  if not g.get("accepted"): return {"status":"BLOCKED","reason":"PROPOSAL_BINDING_FAILED","canonical_id":cid}
  rec=g["record"]; ev=deepcopy(z.get("p106") or {});ev.update({"proposal_hash":rec["proposal_hash"],"registered_proposal_seal":rec["registered_proposal_seal"]})
  nonce="OCC1A-"+hashlib.sha256((cid+rec["proposal_hash"]).encode()).hexdigest()
  built=adoption.build_adoption_decision_from_authoritative_inputs(rec,reg,authority_ids=[d["authority_id"]],independent_domains=["INITIAL_CONSTITUENT_AUTHORITY"],now=1,nonce=nonce,rationale=h.get("decision_rationale") or "GOVERNED_ADOPTION",explicit_confirmation=True,out_of_band=True,amendment_evidence=ev,decision_id="OCC1A-ADOPTION-"+cid.replace(".","-")+"-"+rec["proposal_hash"][:16],decision_time=1,proposer="HUMAN",conflict_of_interest_disclosed=True)
  if built.get("status")!=p095.PASS or built.get("valid") is not True or built.get("persisted") is not False: return {"status":"BLOCKED","reason":"AUTHORITATIVE_DECISION_CHAIN_FAILED","canonical_id":cid,"detail":built,"adoption_performed":False}
  e={"canonical_id":cid,"event_type":"NORM_ADOPTION","state":"ADOPTED","proposal_hash":rec["proposal_hash"],"registered_proposal_seal":rec["registered_proposal_seal"],"p104_record_hash":built["record"]["record_hash"],"p104_record":built["record"],"p104_persisted":False,"authority_activated":False,"runtime_execution_enabled":False};e["event_hash"]=_hash(e);events.append(e)
 core={"schema":SCHEMA,"transaction_kind":"OCC1A_ORDINARY_NORM_ADOPTION","target_ids":list(ORDINARY),"excluded_dna_l0_ids":list(DNA_L0),"event_count":17,"events":events,"source_hashes":{"decisions":_sha(r/DEC_REL),"p106_dossiers":_sha(r/DOS_REL),"authority_declaration":_sha(r/DECL_REL),"authority_context_binding":_sha(r/BIND_REL)},"institutional_authority_verified":True,"atomicity":"17_OR_0","authority_activated":False,"package_materialized":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
 core["transaction_hash"]=_hash(core)
 return {"status":"PREPARED","prepared_count":17,"transaction":core,"adoption_performed":False,"authority_activated":False,"package_materialized":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
def verify_ledger(path):
 p=Path(path)
 if not p.is_file(): return {"status":"ABSENT","valid":False}
 try:x=_load(p)
 except Exception:return {"status":"TAMPERED","valid":False,"reason":"JSON_INVALID"}
 if x.get("schema")!=SCHEMA or x.get("status")!="COMMITTED" or x.get("adoption_performed") is not True:return {"status":"TAMPERED","valid":False,"reason":"ENVELOPE_INVALID"}
 tx=x.get("transaction") or {}
 if tuple(tx.get("target_ids",()))!=ORDINARY or tuple(tx.get("excluded_dna_l0_ids",()))!=DNA_L0 or len(tx.get("events",[]))!=17:return {"status":"TAMPERED","valid":False,"reason":"TARGET_SET_INVALID"}
 for e in tx["events"]:
  z=deepcopy(e);h=z.pop("event_hash",None)
  if h!=_hash(z):return {"status":"TAMPERED","valid":False,"reason":"EVENT_HASH_INVALID"}
 z={k:v for k,v in tx.items() if k!="transaction_hash"}
 if tx.get("transaction_hash")!=_hash(z):return {"status":"TAMPERED","valid":False,"reason":"TRANSACTION_HASH_INVALID"}
 return {"status":"COMMITTED_VALID","valid":True,"transaction_hash":tx["transaction_hash"],"event_count":17}
def commit(root=None,ledger_path=None,fail_after=None):
 r=_root(root);p=Path(ledger_path) if ledger_path else r/LEDGER_REL;q=prepare(r,fail_after)
 if q.get("status")!="PREPARED":return q
 tx=q["transaction"]
 if p.exists():
  old=verify_ledger(p)
  if old.get("valid") and old.get("transaction_hash")==tx["transaction_hash"]:return {"status":"COMMITTED_IDEMPOTENT","adoption_performed":True,"committed_event_count":17,"transaction_hash":tx["transaction_hash"],"authority_activated":False,"package_materialized":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
  return {"status":"REJECTED","reason":"EXISTING_LEDGER_DIVERGENCE_OR_TAMPER","adoption_performed":False}
 env={"schema":SCHEMA,"status":"COMMITTED","adoption_performed":True,"transaction":tx,"authority_activated":False,"package_materialized":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
 p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=p.name+".",suffix=".tmp",dir=str(p.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8") as f:f.write(json.dumps(env,ensure_ascii=False,sort_keys=True,indent=2)+"\n");f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 if not verify_ledger(p).get("valid"):raise RuntimeError("POSTCOMMIT_VERIFICATION_FAILED")
 return {"status":"COMMITTED","adoption_performed":True,"committed_event_count":17,"dna_l0_committed_count":0,"transaction_hash":tx["transaction_hash"],"ledger_sha256":_sha(p),"authority_activated":False,"package_materialized":False,"execution_performed":False,"occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}
def main():
 a=argparse.ArgumentParser();a.add_argument("--commit",action="store_true");a.add_argument("--verify",action="store_true");x=a.parse_args();r=_root()
 o=verify_ledger(r/LEDGER_REL) if x.verify else (commit(r) if x.commit else prepare(r));print(json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2))
 if o.get("status") in ("BLOCKED","REJECTED","TAMPERED"):raise SystemExit(2)
if __name__=="__main__":main()
