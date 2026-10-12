from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json,pytest
from ontology.p161_authorization_token_persistence import *
from validation.p161j_semantic_mutation_crown_v1 import campaign
def token(policy="SINGLE_USE"):
 b={"token_id":"ATJ","use_policy":policy,"validity":{"not_before":"2026-10-01T10:00:00Z","not_after":"2026-10-01T12:00:00Z"},"permits_execution":False}
 t={"body":b,"signature":{"algorithm":"TEST","value":"x"}};t["token_hash"]=h(t);return t
def test_store_immutable(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");bad=deepcopy(t);bad["body"]["purpose"]="x"
 with pytest.raises(ValueError):r.store.persist(bad)
def test_restart_reconstructs_registry(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"];r.registry.path.write_text(json.dumps({"version":999,"tokens":{}}))
 x=P161JRuntime(tmp_path);assert tid in x.registry.state["tokens"]
def test_precommit_crashes_unusable(tmp_path):
 for stage in ("PREPARE","VALIDATE","SIGN"):
  root=tmp_path/stage;r=P161JRuntime(root)
  with pytest.raises(RuntimeError):r.commit_token(token(),"e",crash_after=stage)
  assert token()["body"]["token_id"] not in P161JRuntime(root).registry.state["tokens"]
def test_post_store_precommit_unusable(tmp_path):
 r=P161JRuntime(tmp_path)
 with pytest.raises(RuntimeError):r.commit_token(token(),"e",crash_after="STORE")
 assert token()["body"]["token_id"] not in P161JRuntime(tmp_path).registry.state["tokens"]
def test_post_commit_journal_recoverable(tmp_path):
 r=P161JRuntime(tmp_path)
 with pytest.raises(RuntimeError):r.commit_token(token(),"e",crash_after="JOURNAL")
 assert token()["body"]["token_id"] in P161JRuntime(tmp_path).registry.state["tokens"]
def test_commit_retry_idempotent(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");r.commit_token(t,"e");assert r.journal.verify()
def test_single_use_concurrent_reservation_one_winner(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"]
 def f(i):return r.reserve(tid,now="2026-10-01T11:00:00Z",reservation_id="R"+str(i),event_id="r"+str(i))["status"]
 with ThreadPoolExecutor(max_workers=8) as ex:out=list(ex.map(f,range(8)))
 assert out.count("RESERVED")==1
def test_revocation_blocks_use(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"];r.revoke(tid,now="2026-10-01T11:00:00Z",reason="X",event_id="rv")
 assert r.reserve(tid,now="2026-10-01T11:01:00Z",reservation_id="R",event_id="u")["status"]=="REFUSED"
def test_terminal_does_not_resurrect_after_restart(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"];r.revoke(tid,now="2026-10-01T11:00:00Z",reason="X",event_id="rv")
 assert P161JRuntime(tmp_path).lifecycle(tid)["state"]=="REVOKED"
def test_registry_not_truth(tmp_path):
 r=P161JRuntime(tmp_path);t=token();r.commit_token(t,"e");tid=t["body"]["token_id"];r.registry.state["tokens"][tid]["lifecycle"]["state"]="REVOKED";r.registry.write(r.registry.state)
 assert P161JRuntime(tmp_path).lifecycle(tid)["state"]!="REVOKED"
def test_mutation_semantic_classification():
 x=campaign();assert x["allow_terminal_resurrection"]["status"]=="KILLED";assert x["double_single_use"]["status"]=="KILLED";assert x["syntax_break"]["status"]=="INCONCLUSIVE";assert x["whitespace_only"]["status"]=="NON_SEMANTIC_MUTATION"
def test_boundaries(tmp_path):
 r=P161JRuntime(tmp_path);x=r.commit_token(token(),"e");assert x["execution_performed"] is False and x["p162_opened"] is False
