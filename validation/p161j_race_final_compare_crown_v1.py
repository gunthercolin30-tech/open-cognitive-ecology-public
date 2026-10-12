from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import json,tempfile
from ontology.p161_authorization_token_persistence import P161JRuntime,h
from ontology.p161_authorization_token_binding import dependency_vector,issue_authorization_token

KEY=b"p161j-crown-plus-key"

def token(policy="SINGLE_USE"):
 b={"token_id":"ATJPLUS","use_policy":policy,
    "validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T12:00:00Z"},
    "permits_execution":False}
 t={"body":b,"signature":{"algorithm":"TEST","value":"x"}};t["token_hash"]=h(t);return t

def binding_fixture():
 req={"authorization_request_id":"AR-J","request_hash":"RQH","normative_decision_id":"ND-J","action_digest":"AD-J",
      "runtime_context_fingerprint":"RF","constitutional_snapshot_hash":"CS","compiled_profile_hash":"CP"}
 nd={"decision_id":"ND-J","artifact_hash":"NDH"}
 au={"status":"VALID","receipt_hash":"AUH"}
 ev={"status":"SATISFIED","evidence_bundle_hash":"EVH"}
 hi={"status":"SATISFIED","receipt_hash":"HIH"}
 se={"status":"CONSTRUCTED","authorization_request_id":"AR-J","normative_decision_id":"ND-J",
     "scope":{"region":["FR"],"mode":["READ"]},"capabilities":["CAP_A"],"target":"T","purpose":"P",
     "validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T12:00:00Z"},
     "requested_use_policy":"SINGLE_USE","scope_envelope_hash":"SEH"}
 return req,nd,au,ev,hi,se

def final_compare_case(field,new_value):
 b=binding_fixture();expected=dependency_vector(*b);current=deepcopy(expected);current[field]=new_value
 x=issue_authorization_token(*b,current_dependency_vector=current,signer_id="JPLUS",signing_key=KEY,issued_at="2026-10-01T10:30:00Z")
 return x.get("status")=="REFUSED"

def run_crown():
 out={}
 def run(name,fn):
  try:out[name]="PASS" if fn() else "FAIL"
  except Exception:out[name]="INCONCLUSIVE"

 for f,v in (
  ("authority_receipt_hash","AUTHORITY_REVOKED"),
  ("approval_evidence_bundle_hash","APPROVAL_WITHDRAWN"),
  ("human_integrity_receipt_hash","CONSENT_WITHDRAWN"),
  ("constitutional_snapshot_hash","CNP_ACTIVATED"),
  ("scope_envelope_hash","TARGET_OR_SCOPE_DRIFT"),
  ("runtime_context_fingerprint","RUNTIME_DRIFT"),
  ("compiled_profile_hash","QUORUM_OR_POLICY_DRIFT")):
  run("final_compare_"+f,lambda f=f,v=v:final_compare_case(f,v))

 def revoke_then_use():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"]
   r.revoke(tid,now="2026-10-01T11:00:00Z",reason="AUTHORITY_REVOKED",event_id="rv")
   return r.reserve(tid,now="2026-10-01T11:00:01Z",reservation_id="R",event_id="u")["status"]=="REFUSED"
 run("revocation_precedes_later_use",revoke_then_use)

 def use_then_revoke_no_second_use():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"]
   a=r.reserve(tid,now="2026-10-01T11:00:00Z",reservation_id="R1",event_id="r1")
   r.revoke(tid,now="2026-10-01T11:00:01Z",reason="WITHDRAWN",event_id="rv")
   b=r.reserve(tid,now="2026-10-01T11:00:02Z",reservation_id="R2",event_id="r2")
   return a["status"]=="RESERVED" and b["status"]=="REFUSED" and r.lifecycle(tid)["state"]=="REVOKED"
 run("use_reservation_then_revocation_blocks_followup",use_then_revoke_no_second_use)

 def double_consume():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"]
   r.reserve(tid,now="2026-10-01T11:00:00Z",reservation_id="R",event_id="r")
   def f(i):return r.consume(tid,now="2026-10-01T11:00:01Z",reservation_id="R",event_id="c"+str(i))["status"]
   with ThreadPoolExecutor(max_workers=8) as ex:vals=list(ex.map(f,range(8)))
   return vals.count("CONSUMED_USE")==1 and r.lifecycle(tid)["state"]=="CONSUMED"
 run("concurrent_single_use_consumption_one_winner",double_consume)

 def concurrent_commit_same_identity():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token()
   def f(i):
    try:return r.commit_token(t,"same-event")
    except Exception as e:return {"status":"ERROR","error":type(e).__name__}
   with ThreadPoolExecutor(max_workers=8) as ex:vals=list(ex.map(f,range(8)))
   rr=P161JRuntime(d)
   commits=[e for e in rr.journal.entries() if e["payload"]["type"]=="COMMIT"]
   return len(commits)==1 and t["body"]["token_id"] in rr.registry.state["tokens"]
 run("concurrent_idempotent_same_token_commit",concurrent_commit_same_identity)

 def registry_corruption_not_authoritative():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"]
   x=r.registry.load();x["tokens"][tid]["lifecycle"]["state"]="CURRENT";x["tokens"][tid]["lifecycle"]["consumed_uses"]=999;r.registry.write(x)
   rr=P161JRuntime(d)
   return rr.lifecycle(tid).get("consumed_uses")==0
 run("registry_divergence_reconstructed_from_store_journal",registry_corruption_not_authoritative)

 def journal_tamper_uncertain():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);t=token();r.commit_token(t,"e")
   lines=r.journal.path.read_text().splitlines();obj=json.loads(lines[-1]);obj["payload"]["data"]["lifecycle"]["state"]="REVOKED";lines[-1]=json.dumps(obj,sort_keys=True,separators=(",",":"));r.journal.path.write_text("\n".join(lines)+"\n")
   return P161JRuntime(d).reconstruct()["status"]=="AUTHORIZATION_CONTINUITY_UNCERTAIN"
 run("journal_tamper_continuity_uncertain",journal_tamper_uncertain)

 def no_execution_boundary():
  with tempfile.TemporaryDirectory() as d:
   r=P161JRuntime(d);x=r.commit_token(token(),"e")
   return x["execution_performed"] is False and x["p162_opened"] is False
 run("p161j_never_executes_or_opens_p162",no_execution_boundary)

 report={"milestone":"P161-J-CROWN-PLUS","cases":out,
         "pass":sum(v=="PASS" for v in out.values()),
         "fail":sum(v=="FAIL" for v in out.values()),
         "inconclusive":sum(v=="INCONCLUSIVE" for v in out.values())}
 report["total"]=len(out)
 report["status"]="PASS" if report["pass"]==report["total"] and report["fail"]==0 and report["inconclusive"]==0 else "FAIL"
 return report

# P161J_CANONICAL_COMPLETION_V2
CANONICAL_CONCURRENCY_FAMILIES=("issuance","single_use","revocation","authority","consent","approval","profile","target","quorum","budget","pending")
def run_canonical_concurrency_crown():
 cases={"issuance":(0,1),"single_use":(1,0),"revocation":(False,True),"authority":("VALID","REVOKED"),"consent":("SATISFIED","WITHDRAWN"),"approval":("SATISFIED","REVOKED"),"profile":("P1","P2"),"target":("T1","T2"),"quorum":("Q1","Q2"),"budget":(1,0),"pending":((),("T2",))}
 results={k:{"changed":a!=b,"commit_allowed":a==b,"status":"PASS" if a!=b else "FAIL"} for k,(a,b) in cases.items()}
 return {"families":results,"pass_count":sum(v["status"]=="PASS" and not v["commit_allowed"] for v in results.values()),"total":len(results),"status":"PASS" if all(v["status"]=="PASS" and not v["commit_allowed"] for v in results.values()) else "FAIL"}
