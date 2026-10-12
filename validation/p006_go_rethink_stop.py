"""P006 — preregistered falsifiability decision contract (functional only)."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib, json, re, os
from datetime import datetime, timezone

DECISIONS = ("GO", "GO_WITH_CHANGES", "RETHINK", "STOP_COMPONENT")
_ID = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")

def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _sha(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()

def _nonempty_str(x: Any) -> bool:
    return isinstance(x, str) and bool(x.strip())

def _validate_condition(c: Any) -> None:
    if not isinstance(c, dict):
        raise ValueError("condition must be mapping")
    if not _nonempty_str(c.get("id")) or not _ID.fullmatch(c["id"]):
        raise ValueError("condition.id invalid")
    if not _nonempty_str(c.get("description")):
        raise ValueError("condition.description required")
    if c.get("expected") not in (True, False):
        raise ValueError("condition.expected must be boolean")
    if c.get("severity") not in ("INFO", "CHANGE", "RETHINK", "STOP"):
        raise ValueError("condition.severity invalid")

def validate_criteria(criteria: Any) -> dict:
    if not isinstance(criteria, dict):
        raise ValueError("criteria must be mapping")
    if criteria.get("schema_version") != "P006-1":
        raise ValueError("schema_version must be P006-1")
    if not _nonempty_str(criteria.get("experiment_id")) or not _ID.fullmatch(criteria["experiment_id"]):
        raise ValueError("experiment_id invalid")
    if criteria.get("decision_set") != list(DECISIONS):
        raise ValueError("canonical decision_set required")
    conditions = criteria.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise ValueError("conditions required")
    seen=set()
    for c in conditions:
        _validate_condition(c)
        if c["id"] in seen: raise ValueError("duplicate condition id")
        seen.add(c["id"])
    if not any(c["severity"]=="STOP" for c in conditions):
        raise ValueError("at least one STOP condition required")
    if not any(c["severity"]=="RETHINK" for c in conditions):
        raise ValueError("at least one RETHINK condition required")
    if not any(c["severity"]=="CHANGE" for c in conditions):
        raise ValueError("at least one CHANGE condition required")
    return criteria

def preregister(criteria: dict, registry_dir: Path, registered_at: str | None = None) -> dict:
    criteria = validate_criteria(criteria)
    registry_dir = Path(registry_dir)
    registry_dir.mkdir(parents=True, exist_ok=True)
    cid = _sha(criteria)
    canonical_path=registry_dir/f'{criteria["experiment_id"]}.canonical.json'
    canonical={"experiment_id":criteria["experiment_id"],"criteria_hash":cid}
    try:
        fd=os.open(str(canonical_path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        if json.loads(canonical_path.read_text()) != canonical:
            raise RuntimeError("divergent preregistration forbidden")
    else:
        with os.fdopen(fd,"w") as f:
            f.write(json.dumps(canonical,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
    path = registry_dir / f'{criteria["experiment_id"]}.{cid}.json'
    if path.exists():
        existing=json.loads(path.read_text(encoding="utf-8"))
        if existing["criteria"] != criteria: raise RuntimeError("preregistration collision")
        return existing
    record={
        "canonical_id":"P006",
        "experiment_id":criteria["experiment_id"],
        "criteria_hash":cid,
        "registered_at":registered_at or datetime.now(timezone.utc).isoformat(),
        "criteria":criteria,
        "functional_conclusion_only":True,
        "phenomenology_undetermined":True,
    }
    path.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return record

def open_campaign(registration: dict, registry_dir: Path, started_at: str) -> dict:
    criteria=validate_criteria(registration.get("criteria"))
    if registration.get("criteria_hash") != _sha(criteria): raise ValueError("criteria hash mismatch")
    canonical=json.loads((Path(registry_dir)/f'{criteria["experiment_id"]}.canonical.json').read_text())
    if canonical.get("criteria_hash") != registration["criteria_hash"]: raise ValueError("noncanonical registration")
    rt=datetime.fromisoformat(registration["registered_at"].replace("Z","+00:00"))
    st=datetime.fromisoformat(started_at.replace("Z","+00:00"))
    if rt.tzinfo is None or st.tzinfo is None or not rt < st: raise ValueError("preregistration must precede campaign")
    base={"experiment_id":criteria["experiment_id"],"criteria_hash":registration["criteria_hash"],
          "registered_at":registration["registered_at"],"started_at":started_at}
    base["campaign_hash"]=_sha(base)
    p=Path(registry_dir)/f'{criteria["experiment_id"]}.campaign.json'
    try: fd=os.open(str(p),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        existing=json.loads(p.read_text())
        if existing != base: raise RuntimeError("campaign temporal record immutable")
        return existing
    else:
        with os.fdopen(fd,"w") as f:
            f.write(json.dumps(base,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
    return base

def evaluate(registration: dict, observations: dict) -> dict:
    if not isinstance(registration, dict) or registration.get("canonical_id")!="P006":
        raise ValueError("valid P006 registration required")
    criteria=validate_criteria(registration.get("criteria"))
    if registration.get("criteria_hash") != _sha(criteria):
        raise ValueError("criteria hash mismatch")
    if not isinstance(observations, dict):
        raise ValueError("observations must be mapping")
    if observations.get("experiment_id") != criteria["experiment_id"]:
        raise ValueError("experiment_id mismatch")
    if observations.get("criteria_hash") != registration["criteria_hash"]:
        raise ValueError("observations not bound to preregistered criteria")
    campaign=observations.get("campaign")
    if not isinstance(campaign,dict): raise ValueError("campaign temporal record required")
    base={k:campaign.get(k) for k in ("experiment_id","criteria_hash","registered_at","started_at")}
    if campaign.get("campaign_hash") != _sha(base): raise ValueError("campaign temporal hash mismatch")
    if base["criteria_hash"] != registration["criteria_hash"]: raise ValueError("campaign binding mismatch")
    rt=datetime.fromisoformat(registration["registered_at"].replace("Z","+00:00"))
    st=datetime.fromisoformat(base["started_at"].replace("Z","+00:00"))
    if not rt < st: raise ValueError("late preregistration forbidden")
    values=observations.get("values")
    if not isinstance(values, dict): raise ValueError("values mapping required")
    unknown=[]; triggered=[]
    for c in criteria["conditions"]:
        if c["id"] not in values or values[c["id"]] is None:
            unknown.append(c["id"]); continue
        v=values[c["id"]]
        if not isinstance(v,bool): raise ValueError("observed condition values must be boolean or null")
        if v == c["expected"]: triggered.append(c)
    if unknown:
        decision="RETHINK"; reason="UNKNOWN_OR_INCOMPLETE_EVIDENCE"
    elif any(c["severity"]=="STOP" for c in triggered):
        decision="STOP_COMPONENT"; reason="PREREGISTERED_STOP_CONDITION_TRIGGERED"
    elif any(c["severity"]=="RETHINK" for c in triggered):
        decision="RETHINK"; reason="PREREGISTERED_RETHINK_CONDITION_TRIGGERED"
    elif any(c["severity"]=="CHANGE" for c in triggered):
        decision="GO_WITH_CHANGES"; reason="PREREGISTERED_CHANGE_CONDITION_TRIGGERED"
    else:
        decision="GO"; reason="NO_ADVERSE_PREREGISTERED_CONDITION_TRIGGERED"
    return {
        "canonical_id":"P006","experiment_id":criteria["experiment_id"],
        "criteria_hash":registration["criteria_hash"],"decision":decision,"reason":reason,
        "unknown_condition_ids":sorted(unknown),
        "triggered_condition_ids":sorted(c["id"] for c in triggered),
        "provenance":observations.get("provenance",{}),
        "configuration":observations.get("configuration",{}),
        "functional_conclusion_only":True,"phenomenology_undetermined":True,
    }
