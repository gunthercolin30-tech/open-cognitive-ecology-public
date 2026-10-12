\
"""AY1-D1c — append-only validated relation registry.

The JSONL decision journal is authoritative. validated_relations.json is a
rebuildable projection. Only approved gate records create validated relations.
"""
from __future__ import annotations
import fcntl, hashlib, json, os, tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

def _canon(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v:Any)->str:return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _atomic(path:Path,value:Any,filesystem_effect_context:Any,slot_prefix:str)->None:
    text=json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\\n"
    if filesystem_effect_context is None:raise RuntimeError("governed filesystem effect context required")
    if not path.parent.exists():filesystem_effect_context.execute_path(slot_prefix+":create_parent","FS_CREATE_DIR",path.parent)
    filesystem_effect_context.execute_path(slot_prefix+":write_replace","FS_WRITE_REPLACE_BYTES",path,payload=text.encode("utf-8"))

def _read_jsonl(path:Path)->list[dict[str,Any]]:
    if not path.exists():return []
    out=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():continue
        try:item=json.loads(line)
        except json.JSONDecodeError as e:raise RuntimeError(f"corrupt review journal line {n}") from e
        if not isinstance(item,dict):raise RuntimeError("review journal item must be mapping")
        out.append(item)
    return out

def _verify_chain(records:list[Mapping[str,Any]])->None:
    prev="GENESIS"
    seen_decisions=set(); seen_candidates=set()
    for r in records:
        if r.get("previous_entry_hash")!=prev:raise RuntimeError("review journal hash chain broken")
        core={k:r.get(k) for k in r if k not in {"entry_hash"}}
        if r.get("entry_hash")!=_sha(core):raise RuntimeError("review journal entry hash mismatch")
        did=r.get("decision_id"); cid=r.get("candidate_id")
        if did in seen_decisions:raise RuntimeError("duplicate decision_id")
        if cid in seen_candidates:raise RuntimeError("candidate already decided")
        seen_decisions.add(did);seen_candidates.add(cid);prev=r["entry_hash"]

@dataclass
class ValidatedRelationRegistry:
    root:Path|None=None
    def __post_init__(self):self.root=Path(self.root) if self.root else Path.home()/"open-cognitive-ecology"
    @property
    def state_dir(self):return self.root/"theory_evolution"/"ay1_d1c"/"latest"
    def step(self,inputs:Mapping[str,Any]|None=None,persist:bool=False, filesystem_effect_context: Any = None)->dict[str,Any]:
        supplied=dict(inputs or {}); gate=supplied.get("gate_result")
        if not isinstance(gate,Mapping):raise TypeError("gate_result must be mapping")
        record=gate.get("review_record")
        if gate.get("status")!="GOVERNED_RELATION_REVIEW_READY" or not isinstance(record,Mapping) or record.get("machine_actionable") is not True:raise ValueError("untrusted gate result")
        if persist is not True:return {"status":"VALIDATED_RELATION_REGISTRY_DRY_RUN","would_persist":True,"approved":record.get("approved") is True,"registry_write_performed":False}
        self.state_dir.mkdir(parents=True,exist_ok=True); lock_path=self.state_dir/"registry.lock"
        with lock_path.open("a+",encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
            journal=self.state_dir/"review_decisions.jsonl"; records=_read_jsonl(journal); _verify_chain(records)
            did=record.get("decision_id"); cid=record.get("candidate_id")
            if any(x.get("decision_id")==did for x in records):raise RuntimeError("duplicate decision_id")
            if any(x.get("candidate_id")==cid for x in records):raise RuntimeError("candidate already decided")
            prev=records[-1]["entry_hash"] if records else "GENESIS"
            entry={**dict(record),"previous_entry_hash":prev};entry["entry_hash"]=_sha(entry)
            line=_canon(entry)+"\n"
            with journal.open("a",encoding="utf-8",newline="\n") as h:h.write(line);h.flush();os.fsync(h.fileno())
            all_records=records+[entry];_verify_chain(all_records)
            approved=[]
            for x in all_records:
                if x.get("approved") is True:
                    rel_core={"source":x["confirmed_source"],"target":x["confirmed_target"],"relation":x["confirmed_relation"],"status":"validated","evidence":x["confirmed_evidence_ids"]}
                    approved.append({"id":"validated:"+_sha(rel_core)[:24],**rel_core,"confidence":1.0,"provenance":"ay1_d1c_governed_review","decision_id":x["decision_id"],"decision_hash":x["decision_hash"]})
            approved=sorted(approved,key=lambda x:x["id"])
            projection={"schema_version":"1.0.0","validated_relations":approved,"count":len(approved),"journal_head_hash":all_records[-1]["entry_hash"],"registry_hash":_sha(approved),"functional_conclusion_only":True,"phenomenology_undetermined":True}
            _atomic(self.state_dir/"validated_relations.json",projection,filesystem_effect_context,"validated_relations")
            _atomic(self.state_dir/"registry_manifest.json",{"journal_entries":len(all_records),"validated_count":len(approved),"journal_head_hash":all_records[-1]["entry_hash"],"registry_hash":projection["registry_hash"]},filesystem_effect_context,"registry_manifest")
            return {"status":"VALIDATED_RELATION_REGISTRY_UPDATED","decision_recorded":True,"relation_validated":record.get("approved") is True,"validated_count":len(approved),"journal_head_hash":all_records[-1]["entry_hash"],"registry_hash":projection["registry_hash"],"functional_conclusion_only":True,"phenomenology_undetermined":True}
