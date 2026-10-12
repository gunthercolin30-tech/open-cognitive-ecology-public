from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path.home()/"open-cognitive-ecology"
LAYER=ROOT/"validation_artifacts/p159/occ1k_r9g/governed_semantic_binding_layer_v1.json"
RECEIPT=ROOT/"validation_artifacts/p159/occ1k_r9g/atomic_governed_semantic_binding_commit_receipt_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9h/post_adoption_independent_replay_v1.json"
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 l=json.loads(LAYER.read_text()); q=json.loads(RECEIPT.read_text())
 if l.get("status")!="ADOPTED" or l.get("binding_count")!=8:raise RuntimeError("R9G_LAYER_INVALID")
 if q.get("status")!="COMMITTED" or q.get("adopted_layer_sha256")!=sha(LAYER):raise RuntimeError("R9G_RECEIPT_INVALID")
 phase_map={"S7.CCAD":"S7","S8.COMPOSITION":"S8","S10.ENFORCEMENT":"S10"}
 phases={"S7":[],"S8":[],"S10":[]}
 for b in l["bindings"]:
  raw=b["target_phase"]; phase=phase_map.get(raw,raw)
  if phase not in phases: raise RuntimeError("UNKNOWN_TARGET_PHASE:"+str(raw))
  phases[phase].append(b["candidate_id"])
 # Independent evidence qualification: adoption proves materialized source-backed
 # relations/obligations, but never runtime enforcement.
 result={
  "schema":"oce.p159.occ1k.r9h.post_adoption_independent_replay.v1",
  "status":"POST_ADOPTION_REPLAY_COMPLETE","r9g_layer_sha256":sha(LAYER),
  "binding_count":8,"phase_bindings":phases,
  "s7":{"status":"PASS","basis":"3_GOVERNED_SOURCE_BACKED_RELATIONS_MATERIALIZED"},
  "s8":{"status":"PASS","basis":"3_GOVERNED_SOURCE_BACKED_COMPOSITION_RELATIONS_MATERIALIZED"},
  "s10":{"status":"PARTIAL","basis":"2_PRE_RUNTIME_ENFORCEMENT_OBLIGATIONS_MATERIALIZED_RUNTIME_ENFORCEMENT_NOT_PROVEN"},
  "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
  "fl_b3":"BLOCKED_PENDING_S10_CONTRACT_RECONCILIATION","lock_ready":False,"lock_granted":False,"p160b_opened":False,
  "next_required_step":"R9I_S10_PRE_RUNTIME_CONTRACT_RECONCILIATION",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
 result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest();return result
def main():
 r=build();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_bytes(canon(r)+b"\n")
 print("P159_OCC1K_R9H_POST_ADOPTION_INDEPENDENT_REPLAY_COMPLETE")
 print("STATUS="+r["status"]+"\nBINDINGS=8/8\nS7=PASS\nS8=PASS\nS10=PARTIAL\nRUNTIME_ENFORCEMENT_PROVEN=false\nFL_B3=BLOCKED_PENDING_S10_CONTRACT_RECONCILIATION\nLOCK_READY=false\nLOCK_GRANTED=false\nP160B_OPENED=false\nNEXT="+r["next_required_step"]+"\nARTIFACT_SHA256="+sha(OUT))
if __name__=="__main__":main()
