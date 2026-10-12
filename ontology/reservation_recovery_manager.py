"""P162-F5 durable reservation journal and recovery assessment. Non-effecting."""
from pathlib import Path
from hashlib import sha256
from threading import RLock
import json, os, tempfile

ASSESSMENTS=("CONFIRMED_UNUSED","CONFIRMED_USED","LIKELY_USED_REVIEW_REQUIRED","INDETERMINATE")
RISK_RANK={"AVAILABLE":0,"PREPARED":1,"RESERVED":2,"EXECUTION_STARTED":3,"CONSUMED":4,"INDETERMINATE":5}

def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x): return sha256(_canon(x).encode()).hexdigest()

class ReservationRecoveryJournal:
    """Append/replay reference journal. Recovery never creates execution rights."""
    def __init__(self,path,filesystem_effect_context=None):
        self.path=Path(path); self._lock=RLock()
        if not self.path.parent.exists():
            if filesystem_effect_context is None:
                raise RuntimeError("governed_filesystem_effect_context_required")
            filesystem_effect_context.begin()
            filesystem_effect_context.execute_path(
                "reservation_recovery_journal_parent_create", "FS_CREATE_DIRS", self.path.parent
            )

    def append(self,event):
        with self._lock:
            prev=self._last_hash()
            body={"seq":self._count()+1,"prev_hash":prev,**event}
            body["event_hash"]=_hash(body)
            line=_canon(body)+"\n"
            fd,tmp=tempfile.mkstemp(prefix=self.path.name+".",dir=str(self.path.parent))
            try:
                with os.fdopen(fd,"w",encoding="utf-8") as f:
                    if self.path.exists(): f.write(self.path.read_text(encoding="utf-8"))
                    f.write(line); f.flush(); os.fsync(f.fileno())
                os.replace(tmp,self.path)
            finally:
                if os.path.exists(tmp): os.unlink(tmp)
            return dict(body)

    def append_governed(self, event, filesystem_effect_context):
        """Append through a preissued, single-use FS_WRITE_REPLACE_BYTES handle.

        No authority is created here. The caller must begin the context and
        supply slot reservation_recovery_journal_append_write for this path.
        """
        if filesystem_effect_context is None:
            raise RuntimeError("governed_filesystem_effect_context_required")
        with self._lock:
            if not self.path.parent.is_dir():
                raise RuntimeError("reservation_recovery_journal_parent_missing")
            rep = self.replay()
            if rep.get("status") != "OK":
                raise RuntimeError("reservation_recovery_journal_invalid")
            events = rep["events"]
            prev = events[-1]["event_hash"] if events else "GENESIS"
            body = {"seq": len(events) + 1, "prev_hash": prev, **event}
            body["event_hash"] = _hash(body)
            line = _canon(body) + "\n"
            prior = self.path.read_bytes() if self.path.exists() else b""
            if prior and not prior.endswith(b"\n"):
                raise RuntimeError("reservation_recovery_journal_missing_final_newline")
            payload = prior + line.encode("utf-8")
            filesystem_effect_context.execute_path(
                "reservation_recovery_journal_append_write",
                "FS_WRITE_REPLACE_BYTES", self.path, payload,
            )
            return dict(body)

    def replay(self):
        # No journal file means no durable reservation event ever committed.
        # This is distinct from an existing but unreadable/corrupt journal.
        if not self.path.exists(): return {"status":"OK","events":[]}
        out=[]; prev="GENESIS"; seq=0
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            try: e=json.loads(raw)
            except Exception: return {"status":"INDETERMINATE","reason":"JOURNAL_PARSE_FAILURE","events":out}
            h=e.get("event_hash"); body=dict(e); body.pop("event_hash",None)
            if e.get("seq")!=seq+1 or e.get("prev_hash")!=prev or _hash(body)!=h:
                return {"status":"INDETERMINATE","reason":"JOURNAL_CHAIN_FAILURE","events":out}
            out.append(e); seq=e["seq"]; prev=h
        return {"status":"OK","events":out}

    def reconstruct(self,reservation_id,backup_state=None):
        rep=self.replay()
        if isinstance(rep,list) or rep["status"]!="OK":
            return {"reservation_id":reservation_id,"state":"INDETERMINATE","assessment":"INDETERMINATE",
                    "authorization_created":False,"capability_accessed":False,"execution_performed":False}
        ev=[e for e in rep["events"] if e.get("reservation_id")==reservation_id]
        journal_state="AVAILABLE"
        possible_effect=False; confirmed_effect=False; confirmed_unused=False
        for e in ev:
            typ=e.get("type")
            if typ=="RESERVATION_COMMITTED": journal_state="RESERVED"
            elif typ=="EXECUTION_STARTED": journal_state="EXECUTION_STARTED"; possible_effect=True
            elif typ=="EXECUTION_CONFIRMED": journal_state="CONSUMED"; possible_effect=True; confirmed_effect=True
            elif typ=="CONFIRMED_UNUSED": confirmed_unused=True
            elif typ in ("EFFECT_INDETERMINATE","CANCEL_AFTER_POSSIBLE_EFFECT"):
                journal_state="INDETERMINATE"; possible_effect=True
        state=journal_state
        if backup_state is not None:
            bs=backup_state.get("state","AVAILABLE")
            # Never let an older/safer backup reduce the risk represented by journal state.
            if RISK_RANK.get(bs,5)>RISK_RANK.get(state,5): state=bs
        if state=="CONSUMED" or confirmed_effect: assessment="CONFIRMED_USED"
        elif state=="INDETERMINATE": assessment="INDETERMINATE"
        elif possible_effect: assessment="LIKELY_USED_REVIEW_REQUIRED"
        elif confirmed_unused and state not in ("RESERVED","EXECUTION_STARTED"): assessment="CONFIRMED_UNUSED"
        elif state=="AVAILABLE": assessment="CONFIRMED_UNUSED"
        else: assessment="INDETERMINATE"
        return {"reservation_id":reservation_id,"state":state,"assessment":assessment,
                "authorization_created":False,"capability_accessed":False,"execution_performed":False}

    def idempotent_recover(self,reservation_id,backup_state=None):
        """Returns recovered state only; never manufactures a new reservation."""
        return self.reconstruct(reservation_id,backup_state)

    def _count(self):
        r=self.replay()
        return len(r["events"]) if isinstance(r,dict) and r.get("status")=="OK" else 0
    def _last_hash(self):
        r=self.replay()
        if isinstance(r,dict) and r.get("status")=="OK" and r["events"]: return r["events"][-1]["event_hash"]
        return "GENESIS"
