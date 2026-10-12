# -*- coding: utf-8 -*-
"""E1 — governed metrics history recorder.

P162-G6 refinement: every mutating FILESYSTEM effect is dispatched through
GovernedFilesystemEffector using caller-supplied, target-bound, single-use
handles. Construction/import perform no filesystem mutation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, math
from typing import Any, Dict, Iterable, Optional

from ontology.governed_filesystem_effector import FilesystemEffectRequest

PRIMITIVE="metrics_history_recorder"
DEPENDENCIES=[
    "civilizational_metrics_synthesizer","enhanced_civilizational_metrics",
    "runtime_experiment_manager","experiment_stability_dashboard",
    "scientific_anomaly_detector","scientific_meta_analysis_engine",
    "consciousness_statistical_significance_engine",
]
DEFAULT_MAX_HISTORY_BYTES=25*1024*1024
DEFAULT_MAX_LEGACY_BYTES=10*1024*1024

SLOT_METRICS_DIR_CREATE="metrics_dir_create"
SLOT_STATE_WRITE_REPLACE="state_write_replace"
SLOT_ROTATION_ARCHIVE_REMOVE="rotation_archive_remove"
SLOT_ROTATION_MOVE_REPLACE="rotation_move_replace"
SLOT_HISTORY_PARENT_CREATE="history_parent_create"
SLOT_HISTORY_APPEND="history_append"
SLOT_LEGACY_HISTORY_APPEND="legacy_history_append"
REQUIRED_EFFECT_SLOTS=frozenset({
    SLOT_METRICS_DIR_CREATE,SLOT_STATE_WRITE_REPLACE,SLOT_ROTATION_ARCHIVE_REMOVE,
    SLOT_ROTATION_MOVE_REPLACE,SLOT_HISTORY_PARENT_CREATE,SLOT_HISTORY_APPEND,
    SLOT_LEGACY_HISTORY_APPEND,
})

def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def _bounded(value,default=0.0):
    try:number=float(value)
    except Exception:number=default
    if math.isnan(number) or math.isinf(number):return default
    return max(0.0,min(1.0,number))
def _is_number(value):
    if isinstance(value,bool):return False
    if isinstance(value,(int,float)):
        try:return not(math.isnan(float(value)) or math.isinf(float(value)))
        except Exception:return False
    return False
def _safe_status(value,default="unknown"):
    if value is None:return default
    if isinstance(value,bool):return "validated" if value else "not_validated"
    text=str(value).strip()
    return text if text else default

@dataclass
class GovernedMetricsFilesystemEffectContext:
    effector: Any
    root_id: str
    adapter_id: str
    effector_id: str
    handles: Dict[str, Any]
    _queues: Dict[str,list]=field(init=False,repr=False)
    _recording_started: bool=field(default=False,init=False,repr=False)

    def __post_init__(self):
        unknown=set(self.handles)-REQUIRED_EFFECT_SLOTS
        if unknown: raise ValueError("unknown_effect_slots:"+",".join(sorted(unknown)))
        self._queues={}
        for slot,value in dict(self.handles).items():
            if isinstance(value,(list,tuple)):
                q=list(value)
            else:
                q=[value]
            if any(x is None for x in q): raise ValueError("null_effect_handle:"+slot)
            self._queues[slot]=q

    def begin_recording(self):
        if self._recording_started:
            raise RuntimeError("governed_effect_context_replay_forbidden")
        self._recording_started=True

    def remaining(self,slot):
        return len(self._queues.get(slot,[]))

    def execute(self,slot,request):
        if not self._recording_started:
            raise RuntimeError("governed_effect_context_recording_not_started")
        if slot not in REQUIRED_EFFECT_SLOTS: raise RuntimeError("unknown_effect_slot")
        q=self._queues.get(slot,[])
        if not q: raise RuntimeError("missing_or_exhausted_governed_effect_handle:"+slot)
        handle=q.pop(0)
        result=self.effector.execute(request=request,handle=handle,
            adapter_id=self.adapter_id,effector_id=self.effector_id)
        if not isinstance(result,dict) or result.get("status")!="EFFECT_CONFIRMED":
            reason=result.get("reason") if isinstance(result,dict) else "invalid_effector_result"
            raise RuntimeError("governed_filesystem_effect_not_confirmed:"+str(reason))
        return result

class MetricsHistoryRecorder:
    primitive=PRIMITIVE
    def __init__(self,root=None,max_history_bytes=DEFAULT_MAX_HISTORY_BYTES,
                 max_legacy_bytes=DEFAULT_MAX_LEGACY_BYTES):
        self.root=Path(root) if root else Path.home()/"open-cognitive-ecology"
        self.metrics_dir=self.root/"metrics"
        self.history_path=self.metrics_dir/"metrics_history.jsonl"
        self.legacy_history_path=self.root/"metrics_history.jsonl"
        self.state_path=self.metrics_dir/"metrics_history_recorder_state.json"
        self.max_history_bytes=max(1024*1024,int(max_history_bytes))
        self.max_legacy_bytes=max(256*1024,int(max_legacy_bytes))

    def _relative(self,path):
        try:return path.relative_to(self.root).as_posix()
        except ValueError as exc: raise RuntimeError("metrics_path_outside_governed_root") from exc

    def _read_state(self):
        if self.state_path.exists():
            try:return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:pass
        return {"primitive":PRIMITIVE,"record_count":0,"rotation_count":0,"last_record_timestamp":None}

    def _effect(self,ctx,slot,operation,path,payload=None,source=None):
        if ctx is None: raise RuntimeError("governed_filesystem_effect_context_required")
        req=FilesystemEffectRequest(operation_id=operation,root_id=ctx.root_id,
            relative_path=self._relative(path),payload=payload,
            source_root_id=ctx.root_id if source is not None else None,
            source_relative_path=self._relative(source) if source is not None else None)
        return ctx.execute(slot,req)

    def _write_state(self,state,ctx):
        state["primitive"]=PRIMITIVE
        payload=json.dumps(state,ensure_ascii=False,indent=2,sort_keys=True).encode("utf-8")
        self._effect(ctx,SLOT_STATE_WRITE_REPLACE,"FS_WRITE_REPLACE_BYTES",self.state_path,payload)

    def _rotate_if_needed(self,path,max_bytes,ctx):
        if not path.exists() or path.stat().st_size<=max_bytes:return False
        archive=path.with_suffix(path.suffix+".bak")
        if archive.exists():
            self._effect(ctx,SLOT_ROTATION_ARCHIVE_REMOVE,"FS_REMOVE_FILE",archive)
        self._effect(ctx,SLOT_ROTATION_MOVE_REPLACE,"FS_MOVE_OR_REPLACE",archive,source=path)
        return True

    def _extract_metrics(self,payload):
        metrics={}
        explicit=payload.get("metrics")
        if isinstance(explicit,dict):
            for k,v in explicit.items():
                if _is_number(v):metrics[str(k)]=v
        for k,v in payload.items():
            if k in {"metrics","diagnostics","latest_records","records","agent_result","notification_result"}:continue
            if _is_number(v):metrics[str(k)]=v
        diagnostics=payload.get("diagnostics")
        if isinstance(diagnostics,dict):
            for k,v in diagnostics.items():
                if _is_number(v):metrics["diagnostics."+str(k)]=v
        return metrics

    def _infer_error_count(self,payload):
        for k in ("error_count","errors","failed_calls","failed_emissions"):
            v=payload.get(k)
            if isinstance(v,bool):continue
            if isinstance(v,(int,float)):return max(0,int(v))
        d=payload.get("diagnostics")
        if isinstance(d,dict):
            v=d.get("error_count")
            if isinstance(v,(int,float)) and not isinstance(v,bool):return max(0,int(v))
        return 1 if payload.get("error") or payload.get("exception") else 0

    def normalize(self,payload=None,primitive=None,validation_status=None,
                  governance_status=None,runtime_status=None):
        payload=dict(payload or {})
        source=primitive or payload.get("primitive") or payload.get("source") or "unknown"
        if validation_status is None:
            validation_status=payload.get("validation_status")
            if validation_status is None:validation_status=payload.get("validated") or payload.get("certified")
        if governance_status is None:
            governance_status=payload.get("governance_status")
            if governance_status is None:governance_status=payload.get("governance_allowed")
        if runtime_status is None:
            runtime_status=payload.get("runtime_status")
            if runtime_status is None:runtime_status=payload.get("status") or payload.get("operational")
        return {"timestamp":payload.get("timestamp") or payload.get("timestamp_utc") or _now(),
            "primitive":str(source).lower(),"metrics":self._extract_metrics(payload),
            "validation_status":_safe_status(validation_status),
            "governance_status":_safe_status(governance_status),
            "runtime_status":_safe_status(runtime_status),
            "error_count":self._infer_error_count(payload),
            "source_payload_keys":sorted(str(k) for k in payload.keys())[:200]}

    def append(self,record,*,effect_context=None):
        if effect_context is None:raise RuntimeError("governed_filesystem_effect_context_required")
        effect_context.begin_recording()
        serialized=(json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")
        rotations=0
        # Constructor no longer creates this directory; creation is mediated here.
        if not self.metrics_dir.exists():
            self._effect(effect_context,SLOT_METRICS_DIR_CREATE,"FS_CREATE_DIR",self.metrics_dir)
        if self._rotate_if_needed(self.history_path,self.max_history_bytes,effect_context):rotations+=1
        # Historical parent-create call site remains represented, but is only needed
        # if a custom transport/environment leaves the parent absent.
        if not self.history_path.parent.exists():
            self._effect(effect_context,SLOT_HISTORY_PARENT_CREATE,"FS_CREATE_DIR",self.history_path.parent)
        self._effect(effect_context,SLOT_HISTORY_APPEND,"FS_APPEND_BYTES",self.history_path,serialized)
        if self._rotate_if_needed(self.legacy_history_path,self.max_legacy_bytes,effect_context):rotations+=1
        self._effect(effect_context,SLOT_LEGACY_HISTORY_APPEND,"FS_APPEND_BYTES",self.legacy_history_path,serialized)
        state=self._read_state()
        state["record_count"]=int(state.get("record_count",0))+1
        state["rotation_count"]=int(state.get("rotation_count",0))+rotations
        state["last_record_timestamp"]=record.get("timestamp")
        state["history_path"]=str(self.history_path)
        state["legacy_history_path"]=str(self.legacy_history_path)
        self._write_state(state,effect_context)
        return state

    def record(self,payload=None,primitive=None,validation_status=None,
               governance_status=None,runtime_status=None,*,effect_context=None):
        record=self.normalize(payload,primitive,validation_status,governance_status,runtime_status)
        state=self.append(record,effect_context=effect_context)
        return {"primitive":PRIMITIVE,"recorded":True,"history_path":str(self.history_path),
            "legacy_history_path":str(self.legacy_history_path),"state_path":str(self.state_path),
            "record":record,"record_count":state.get("record_count",0),
            "metrics_history_exists":self.history_path.exists(),"error_count":0}

    def tail(self,limit=20):
        if not self.history_path.exists():return []
        lines=self.history_path.read_text(encoding="utf-8",errors="ignore").splitlines()[-max(1,min(1000,int(limit))):]
        out=[]
        for line in lines:
            try:out.append(json.loads(line))
            except Exception:pass
        return out

    def step(self,inputs=None):
        inputs=dict(inputs or {})
        ctx=inputs.pop("effect_context",None)
        sample=inputs.get("payload")
        if not isinstance(sample,dict):
            sample={"primitive":inputs.get("primitive",PRIMITIVE),
                "metrics":inputs.get("metrics",{"metrics_history_recorder_self_test":1.0}),
                "validation_status":inputs.get("validation_status","validated"),
                "governance_status":inputs.get("governance_status","governed"),
                "runtime_status":inputs.get("runtime_status","operational"),
                "error_count":inputs.get("error_count",0)}
        result=self.record(sample,primitive=inputs.get("primitive"),
            validation_status=inputs.get("validation_status"),
            governance_status=inputs.get("governance_status"),
            runtime_status=inputs.get("runtime_status"),effect_context=ctx)
        recent=self.tail(5)
        result.update({"sample_count":len(recent),
            "schema_fields":["timestamp","primitive","metrics","validation_status","governance_status","runtime_status","error_count"],
            "history_directory":str(self.metrics_dir),"disk_quota_bytes":self.max_history_bytes,
            "local_disk_usage_bounded":True,
            "e1_metrics_history_core_operational":bool(result.get("metrics_history_exists"))})
        return result

ENGINE=MetricsHistoryRecorder()

def record_metrics(payload=None,primitive=None,*,effect_context=None,**status):
    try:return MetricsHistoryRecorder().record(payload or {},primitive=primitive,effect_context=effect_context,**status)
    except Exception as exc:
        return {"primitive":PRIMITIVE,"recorded":False,"error":repr(exc),"error_count":1}

def step(inputs=None):return ENGINE.step(inputs)
