from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import hashlib, json, os, tempfile

PRIMITIVE="p160_normative_decision_persistence"
VERSION="P160-J-v1"
SCHEMA="oce.p160j.persistence_restart_concurrency.v1"

STARTUP_STATES={"STARTUP_VALID","STARTUP_DEGRADED","STARTUP_RECONCILIATION_REQUIRED","STARTUP_CONTINUITY_UNCERTAIN","STARTUP_SAFE_MODE_REQUIRED"}
TEMPORAL_STATES={"TRUSTED","RECONSTRUCTED","UNCERTAIN","INVALID"}
TERMINAL={"STALE","INVALIDATED","SUPERSEDED","EXPIRED"}
ALLOWED_TRANSITIONS={
 "SEALED":{"COMMITTED","STALE","INVALIDATED","SUPERSEDED","EXPIRED"},
 "COMMITTED":{"STALE","INVALIDATED","SUPERSEDED","EXPIRED"},
 "STALE":{"INVALIDATED","SUPERSEDED","EXPIRED"},
 "INVALIDATED":set(),"SUPERSEDED":set(),"EXPIRED":set(),
}

def canonical_json(x:Any)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha256_obj(x:Any)->str:
    return hashlib.sha256(canonical_json(x).encode("utf-8")).hexdigest()

def _atomic_json(path:Path,obj:Any,filesystem_effect_context=None)->None:
    payload=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
    filesystem_effect_context.begin()
    if not path.parent.exists(): filesystem_effect_context.execute_path("p160_atomic_parent_create","FS_CREATE_DIR",path.parent)
    filesystem_effect_context.execute_path("p160_atomic_write_replace","FS_WRITE_REPLACE_BYTES",path,payload)

def dependency_vector(decision:Dict[str,Any])->Dict[str,Any]:
    f=decision.get("freshness_policy") or {}
    b=decision.get("bindings") or {}
    return {
      "profile_version":b.get("compiled_profile_hash"),
      "authority_version":f.get("authority_state_hash") or b.get("authority_state_hash"),
      "target_version":f.get("target_state_hash"),
      "related_actions_version":f.get("related_actions_version"),
      "emergency_version":f.get("emergency_state_hash"),
      "policy_version":f.get("policy_version"),
    }

class NormativeDecisionStore:
    def __init__(self,root:Path,filesystem_effect_context=None):
        self.root=Path(root);self.dir=self.root/"store"
        if not self.dir.exists():
            if filesystem_effect_context is None: raise RuntimeError("governed_store_filesystem_effect_context_required")
            filesystem_effect_context.begin()
            filesystem_effect_context.execute_path("p160_store_create_dirs","FS_CREATE_DIRS",self.dir)
    def persist(self,decision:Dict[str,Any],filesystem_effect_context=None)->str:
        did=str(decision.get("decision_id") or decision.get("artifact_hash") or "")
        if not did: raise ValueError("DECISION_ID_REQUIRED")
        p=self.dir/(did+".json")
        if p.exists():
            old=json.loads(p.read_text(encoding="utf-8"))
            if sha256_obj(old)!=sha256_obj(decision): raise ValueError("IMMUTABLE_PAYLOAD_CONFLICT")
            return did
        _atomic_json(p,deepcopy(decision),filesystem_effect_context);return did
    def load(self,did:str)->Dict[str,Any]:
        return json.loads((self.dir/(did+".json")).read_text(encoding="utf-8"))
    def verify(self,did:str)->bool:
        try:
            d=self.load(did)
            from ontology.p160_normative_decision_sealing import verify_normative_decision
            return verify_normative_decision(d).get("status")=="PASS"
        except Exception:return False

class NormativeDecisionJournal:
    def __init__(self,root:Path,filesystem_effect_context=None):
        self.path=Path(root)/"journal.jsonl"
        if not self.path.parent.exists():
            if filesystem_effect_context is None:
                raise RuntimeError("governed_filesystem_effect_context_required")
            filesystem_effect_context.begin()
            filesystem_effect_context.execute_path("archive_create_dirs","FS_CREATE_DIRS",self.path.parent)
    def entries(self)->List[Dict[str,Any]]:
        if not self.path.exists():return []
        out=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():out.append(json.loads(line))
        return out
    def verify(self)->bool:
        prev="GENESIS"
        seen={}
        for e in self.entries():
            payload=e.get("payload")
            if e.get("previous_journal_hash")!=prev:return False
            if e.get("journal_hash")!=sha256_obj({"previous_journal_hash":prev,"event_id":e.get("event_id"),"payload":payload}):return False
            eid=e.get("event_id")
            if eid in seen and seen[eid]!=sha256_obj(payload):return False
            seen[eid]=sha256_obj(payload);prev=e["journal_hash"]
        return True
    def append(self,event_id:str,payload:Dict[str,Any])->Dict[str,Any]:
        entries=self.entries()
        for e in entries:
            if e["event_id"]==event_id:
                if sha256_obj(e["payload"])!=sha256_obj(payload):raise ValueError("JOURNAL_EVENT_ID_CONFLICT")
                return deepcopy(e)
        prev=entries[-1]["journal_hash"] if entries else "GENESIS"
        e={"event_id":event_id,"previous_journal_hash":prev,"payload":deepcopy(payload)}
        e["journal_hash"]=sha256_obj(e)
        with self.path.open("a",encoding="utf-8") as f:
            f.write(canonical_json(e)+"\n");f.flush();os.fsync(f.fileno())
        return e

class NormativeDecisionRegistry:
    def __init__(self,root:Path):
        self.path=Path(root)/"registry.json";self.state={"version":0,"decisions":{}}
        if self.path.exists():self.state=json.loads(self.path.read_text(encoding="utf-8"))
    def get(self,did:str)->Optional[Dict[str,Any]]:return deepcopy(self.state["decisions"].get(did))
    def set(self,did:str,status:str,artifact_hash:str,dependency:Dict[str,Any],journal_hash:str,filesystem_effect_context=None)->int:
        self.state["version"]+=1
        self.state["decisions"][did]={"status":status,"artifact_hash":artifact_hash,"dependency_vector":deepcopy(dependency),"journal_hash":journal_hash,"registry_version":self.state["version"]}
        _atomic_json(self.path,self.state,filesystem_effect_context);return self.state["version"]

class P160JRuntime:
    def __init__(self,root:Path,store_filesystem_effect_context=None,root_filesystem_effect_context=None):
        self.root=Path(root)
        if not self.root.exists():
         if root_filesystem_effect_context is None:raise RuntimeError("governed_runtime_root_filesystem_effect_context_required")
         root_filesystem_effect_context.begin()
         root_filesystem_effect_context.execute_path("p160_runtime_root_create_dirs","FS_CREATE_DIRS",self.root)
        self.store=NormativeDecisionStore(self.root,store_filesystem_effect_context);self.journal=NormativeDecisionJournal(self.root);self.registry=NormativeDecisionRegistry(self.root)
    def commit(self,decision:Dict[str,Any],event_id:str,store_filesystem_effect_context=None,registry_filesystem_effect_context=None)->Dict[str,Any]:
        from ontology.p160_normative_decision_sealing import verify_normative_decision
        if store_filesystem_effect_context is None or registry_filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
        did=str(decision.get("decision_id") or decision.get("artifact_hash") or "")
        if not did:raise ValueError("DECISION_ID_REQUIRED")
        dep=dependency_vector(decision);stages=[]
        for stage in ("PREPARE","VALIDATE","SEAL"):
            if stage=="VALIDATE" and verify_normative_decision(decision).get("status")!="PASS":raise ValueError("DECISION_VERIFICATION_FAILED")
            je=self.journal.append(event_id+":"+stage,{"type":"TRANSACTION_STAGE","stage":stage,"decision_id":did,"artifact_hash":decision.get("artifact_hash"),"usable":False})
            stages.append({"stage":stage,"journal_hash":je["journal_hash"],"usable":False})
        self.store.persist(decision,store_filesystem_effect_context)
        je=self.journal.append(event_id+":PERSIST",{"type":"TRANSACTION_STAGE","stage":"PERSIST","decision_id":did,"artifact_hash":decision["artifact_hash"],"dependency_vector":dep,"usable":False})
        stages.append({"stage":"PERSIST","journal_hash":je["journal_hash"],"usable":False})
        je=self.journal.append(event_id+":COMMIT",{"type":"COMMIT","decision_id":did,"artifact_hash":decision["artifact_hash"],"dependency_vector":dep,"status":"COMMITTED","usable":True})
        stages.append({"stage":"COMMIT","journal_hash":je["journal_hash"],"usable":True})
        rv=self.registry.set(did,"COMMITTED",decision["artifact_hash"],dep,je["journal_hash"],registry_filesystem_effect_context)
        x=self._receipt(event_id,did,"SEALED","COMMITTED","PERSISTED_COMMIT",je["journal_hash"],rv)
        x["transaction_stages"]=stages;x["transaction_complete"]=True
        x["receipt_hash"]=sha256_obj({k:v for k,v in x.items() if k!="receipt_hash"});return x
    def transition(self,did:str,new_status:str,reason:str,event_id:str,registry_filesystem_effect_context=None)->Dict[str,Any]:
        if registry_filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
        cur=self.registry.get(did)
        if not cur:raise ValueError("UNKNOWN_DECISION")
        prev=cur["status"]
        if new_status not in ALLOWED_TRANSITIONS.get(prev,set()):raise ValueError("ILLEGAL_LIFECYCLE_TRANSITION")
        payload={"type":"TRANSITION","decision_id":did,"previous_status":prev,"new_status":new_status,"reason":reason}
        je=self.journal.append(event_id,payload)
        rv=self.registry.set(did,new_status,cur["artifact_hash"],cur["dependency_vector"],je["journal_hash"],registry_filesystem_effect_context)
        return self._receipt(event_id,did,prev,new_status,reason,je["journal_hash"],rv)
    def _receipt(self,tid,did,prev,new,reason,jh,rv):
        x={"schema":"oce.p160j.transition_receipt.v1","transition_id":tid,"decision_id":did,"previous_status":prev,"new_status":new,"reason":reason,"source_event":tid,"timestamp":_utc_timestamp(),"journal_hash":jh,"registry_version":rv,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}
        x["receipt_hash"]=sha256_obj(x);return x
    def startup_reconcile(self,current_dependencies:Optional[Dict[str,Dict[str,Any]]]=None,minimum_viable_constitution:bool=False,startup_issues:Optional[list]=None)->Dict[str,Any]:
        issues=list(startup_issues or [])
        if not self.journal.verify():issues.append("JOURNAL_CONTINUITY_INVALID")
        rebuilt={}
        for e in self.journal.entries():
            p=e["payload"];did=p.get("decision_id")
            if p.get("type")=="COMMIT":rebuilt[did]={"status":"COMMITTED","artifact_hash":p["artifact_hash"],"dependency_vector":p["dependency_vector"],"journal_hash":e["journal_hash"]}
            elif p.get("type")=="TRANSITION" and did in rebuilt:
                if p["new_status"] not in ALLOWED_TRANSITIONS.get(rebuilt[did]["status"],set()):issues.append("ILLEGAL_REPLAY_TRANSITION:"+did)
                else:rebuilt[did]["status"]=p["new_status"];rebuilt[did]["journal_hash"]=e["journal_hash"]
        for did,x in rebuilt.items():
            if not self.store.verify(did):issues.append("STORE_VERIFICATION_FAILED:"+did)
            reg=self.registry.get(did)
            if not reg or reg["status"]!=x["status"] or reg["artifact_hash"]!=x["artifact_hash"]:issues.append("REGISTRY_RECONCILIATION_REQUIRED:"+did)
            if current_dependencies and did in current_dependencies and current_dependencies[did]!=x["dependency_vector"]:issues.append("MATERIAL_DEPENDENCY_DRIFT:"+did)
        # Detect valid-but-truncated journals: hash-chain verification alone cannot
        # prove that the tail is complete. Store/registry material absent from
        # replay is therefore explicit reconciliation evidence.
        store_ids={p.stem for p in self.store.dir.glob("*.json") if p.is_file()}
        registry_ids=set(self.registry.state.get("decisions",{}))
        rebuilt_ids=set(rebuilt)
        for did in sorted(store_ids-rebuilt_ids):issues.append("JOURNAL_MISSING_STORE_HISTORY:"+did)
        for did in sorted(registry_ids-rebuilt_ids):issues.append("JOURNAL_MISSING_REGISTRY_HISTORY:"+did)
        state=classify_startup_state(issues,minimum_viable_constitution=minimum_viable_constitution)
        return {"startup_state":state,"issues":issues,"reconstructed":rebuilt,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}

def temporal_continuity(previous_state:str,clock_rollback:bool=False,continuity_proven:bool=True)->str:
    if previous_state not in TEMPORAL_STATES:return "INVALID"
    if previous_state=="INVALID":return "INVALID"
    if not continuity_proven:return "UNCERTAIN"
    if clock_rollback:return "RECONSTRUCTED"
    return previous_state

def restore_eligibility(meta:Dict[str,Any])->Dict[str,Any]:
    required=("lineage_valid","constitutional_version_compatible","revocations_preserved","supersessions_preserved","journal_continuity","profile_compatible","authority_compatible","expiry_preserved")
    missing=[k for k in required if meta.get(k) is not True]
    return {"status":"RESTORE_ELIGIBLE" if not missing else "RESTORE_REJECTED","missing_or_invalid":missing,"authorization_created":False}

def reconcile_branches(a:Dict[str,Any],b:Dict[str,Any])->Dict[str,Any]:
    if a.get("journal_hash")==b.get("journal_hash"):return {"status":"CONTINUITY_RECONCILED","selected":"EQUIVALENT"}
    aa=set(a.get("ancestry",[]));bb=set(b.get("ancestry",[]))
    if a.get("journal_hash") in bb:return {"status":"CONTINUITY_RECONCILED","selected":"B"}
    if b.get("journal_hash") in aa:return {"status":"CONTINUITY_RECONCILED","selected":"A"}
    return {"status":"CONTINUITY_UNCERTAIN","selected":None}

def migrate_record(record:Dict[str,Any],supported_critical_fields:Iterable[str],normative_delta:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
    critical=set(record.get("critical_fields",[]));unsupported=critical-set(supported_critical_fields)
    if unsupported:return {"status":"MIGRATION_REJECTED","reason":"UNSUPPORTED_CRITICAL_FIELD","fields":sorted(unsupported)}
    out=deepcopy(record)
    if normative_delta:
        out["normative_delta"]=deepcopy(normative_delta);out["migration_status"]="EXPLICIT_NORMATIVE_DELTA"
    else:out["migration_status"]="SEMANTIC_PRESERVATION_REQUIRED"
    return {"status":"MIGRATED","record":out}

def roundtrip(record:Dict[str,Any])->Dict[str,Any]:
    return json.loads(canonical_json(record))

def concurrent_decision_context(decisions:List[Dict[str,Any]])->Dict[str,Any]:
    targets={};resources={};authorities={}
    for d in decisions:
        aid=d.get("action_digest") or {};target=aid.get("target")
        if target:targets[target]=targets.get(target,0)+1
        for r in aid.get("resource_effects") or []:
            key=canonical_json(r);resources[key]=resources.get(key,0)+1
        auth=(d.get("authority_resolution") or {}).get("authority_state")
        if auth:authorities[auth]=authorities.get(auth,0)+1
    collisions={"shared_targets":sorted(k for k,v in targets.items() if v>1),"shared_resources":sorted(k for k,v in resources.items() if v>1)}
    return {"active_decisions":len(decisions),"collisions":collisions,"interaction_uncertainty":bool(collisions["shared_targets"] or collisions["shared_resources"]),"authorization_created":False,"execution_performed":False}

def compare_dependency_vector(expected:Dict[str,Any],current:Dict[str,Any])->Dict[str,Any]:
    changed=sorted(k for k in set(expected)|set(current) if expected.get(k)!=current.get(k))
    return {"status":"MATCH" if not changed else "REVALIDATE_REQUIRED","changed":changed,"authorization_created":False}

def manifest()->Dict[str,Any]:
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"separates":["PERSISTENCE","RESTART_RECOVERY","CONCURRENCY"],"startup_states":sorted(STARTUP_STATES),"temporal_states":sorted(TEMPORAL_STATES),"boundaries":{"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False},"functional_only":True,"phenomenology_undetermined":True}

# --- P160-J exhaustive annex extensions v1 ---

DEPENDENCY_EDGE_TYPES={"DEPENDS_ON","SUPERSEDES","REVIEWS","REPAIRS","ROLLS_BACK","DERIVES_FROM"}

def snapshot_consistency(before:Dict[str,Any],after:Dict[str,Any])->Dict[str,Any]:
    changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
    return {"status":"CONSISTENT" if not changed else "RETRY_REQUIRED","changed":changed,"authorization_created":False}

def active_exception_context(exceptions:List[Dict[str,Any]])->Dict[str,Any]:
    counts={}
    for e in exceptions:
        if e.get("active") and e.get("temporary"):
            key=str(e.get("class") or e.get("exception_id") or "UNKNOWN")
            counts[key]=counts.get(key,0)+1
    repeated=sorted(k for k,v in counts.items() if v>1)
    return {"status":"TEMPORARY_COMPOSITION_OK" if not repeated else "CUMULATIVE_EXCEPTION_REVIEW_REQUIRED",
            "repeated_temporary_classes":repeated,"authorization_created":False}

def p160_p161_boundary_contract(decision:Dict[str,Any])->Dict[str,Any]:
    b=decision.get("bindings") or {}
    f=decision.get("freshness_policy") or {}
    return {"decision_hash":decision.get("artifact_hash"),
            "dependency_vector":dependency_vector(decision),
            "authority_state_hash":f.get("authority_state_hash") or b.get("authority_state_hash"),
            "context_fingerprint":b.get("runtime_context_fingerprint"),
            "expiry":f.get("expiry") or decision.get("expiry"),
            "authorization_created":False,"execution_performed":False}

def privacy_safe_journal_payload(payload:Dict[str,Any])->bool:
    forbidden={"raw_personal_data","raw_personal_name","raw_email","raw_phone","raw_address"}
    return not any(k in payload for k in forbidden)

def dependency_graph_validate(edges:List[Dict[str,Any]])->Dict[str,Any]:
    bad=[e for e in edges if e.get("type") not in DEPENDENCY_EDGE_TYPES or not e.get("source") or not e.get("target")]
    return {"status":"VALID" if not bad else "INVALID","invalid_edges":bad}

def materially_dependent(graph:List[Dict[str,Any]],source:str)->List[str]:
    return sorted({e["target"] for e in graph if e.get("source")==source and e.get("type") in DEPENDENCY_EDGE_TYPES})

def verified_checkpoint(entries:List[Dict[str,Any]])->Dict[str,Any]:
    cp={"schema":"oce.p160j.verified_checkpoint.v1","entry_count":len(entries),
        "tail_hash":entries[-1].get("journal_hash") if entries else "GENESIS",
        "entries_digest":sha256_obj(entries)}
    cp["checkpoint_hash"]=sha256_obj(cp)
    return cp

def verify_checkpoint(cp:Dict[str,Any],entries:List[Dict[str,Any]])->bool:
    x=deepcopy(cp);h=x.pop("checkpoint_hash",None)
    return h==sha256_obj(x) and x.get("entry_count")==len(entries) and x.get("entries_digest")==sha256_obj(entries) and x.get("tail_hash")==(entries[-1].get("journal_hash") if entries else "GENESIS")

def canonical_platform_vector(record:Dict[str,Any])->Dict[str,Any]:
    encoded=canonical_json(record).encode("utf-8")
    return {"canonical_json":encoded.decode("utf-8"),"sha256":hashlib.sha256(encoded).hexdigest()}

def profile_activation_effect(decisions:List[Dict[str,Any]],old_profile:str,new_profile:str,grandfathered:Optional[Iterable[str]]=None)->Dict[str,str]:
    gf=set(grandfathered or [])
    out={}
    for d in decisions:
        did=str(d.get("decision_id") or d.get("artifact_hash"))
        profile=(d.get("bindings") or {}).get("compiled_profile_hash")
        consumed=bool(d.get("consumed",False))
        out[did]="UNCHANGED" if consumed or profile!=old_profile or did in gf else "REVALIDATE_REQUIRED"
    return out

def retroactive_review(executed:bool,review_outcome:str)->Dict[str,Any]:
    return {"executed":bool(executed),"review_outcome":review_outcome,"retroactive_authorization":False,
            "allowed_effects":["OBSERVE","REPAIR","SANCTION","LEARN"],"authorization_created":False}

def temporal_expiry_state(previous_state:str,expired:bool,clock_rollback:bool=False)->str:
    if expired:return "INVALID"
    return temporal_continuity(previous_state,clock_rollback=clock_rollback,continuity_proven=True)

# --- P160-J canonical completion v1 ---
from datetime import datetime, timezone
TRANSACTION_STAGES=("PREPARE","VALIDATE","SEAL","PERSIST","COMMIT")
PENDING_PRESERVED_STATES={"UNKNOWN","PENDING","REVIEW_REQUIRED","ARBITRATION_PENDING","REVOKED","EXPIRED","STALE","SEALED"}
def _utc_timestamp()->str:return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def planned_authority_consumption(authority_ref=None,budgets=None):
    return {"authority_ref":authority_ref,"planned_budgets":deepcopy(budgets or {}),"effective_consumption":False,"authorization_created":False,"execution_performed":False}
def preserve_restart_state(state:str)->str:return state
def classify_startup_state(issues,minimum_viable_constitution=False):
    if not issues:return "STARTUP_VALID"
    if any(x.startswith("SAFE_MODE_REQUIRED") for x in issues):return "STARTUP_SAFE_MODE_REQUIRED"
    if any(("JOURNAL_CONTINUITY" in x or "BRANCH_CONTINUITY" in x) for x in issues):return "STARTUP_CONTINUITY_UNCERTAIN"
    if minimum_viable_constitution and all(x.startswith("NONCRITICAL_") for x in issues):return "STARTUP_DEGRADED"
    return "STARTUP_RECONCILIATION_REQUIRED"
def decision_execution_separation(decision_status,execution_observed=False):
    return {"decision_status":decision_status,"execution_observed":bool(execution_observed),"execution_inferred_from_decision":False,"retroactive_authorization":False,"authorization_created":False}
def transactional_creation_trace(decision):
    return [{"stage":s,"usable":s=="COMMIT","authorization_created":False,"authorization_token_created":False,"execution_performed":False} for s in TRANSACTION_STAGES]
