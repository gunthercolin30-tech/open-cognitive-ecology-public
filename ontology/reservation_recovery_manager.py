"""P162-F5 durable reservation journal and recovery assessment. Non-effecting."""
from pathlib import Path
from hashlib import sha256
from threading import RLock
import json, os, tempfile, stat

ASSESSMENTS=("CONFIRMED_UNUSED","CONFIRMED_USED","LIKELY_USED_REVIEW_REQUIRED","INDETERMINATE")
RISK_RANK={"AVAILABLE":0,"PREPARED":1,"RESERVED":2,"EXECUTION_STARTED":3,"CONSUMED":4,"INDETERMINATE":5}

def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
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
            rep = self.replay()
            if rep["status"] != "OK":
                raise RuntimeError("reservation_recovery_journal_invalid")
            body = self._prepare_event(event, rep["events"])
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
            body = self._prepare_event(event, events)
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

    @staticmethod
    def _prepare_event(event, events):
        if type(event) is not dict:
            raise ValueError("journal_event_object_required")
        if {"seq", "prev_hash", "event_hash"}.intersection(event):
            raise ValueError("journal_metadata_is_not_caller_controlled")
        body = {**event, "seq": len(events) + 1,
                "prev_hash": events[-1]["event_hash"] if events else "GENESIS"}
        body["event_hash"] = _hash(body)
        return body

    @staticmethod
    def _json_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    @staticmethod
    def _reject_constant(value):
        raise ValueError("non_finite_json_number")

    def replay(self):
        # A missing journal is not evidence that an existing reservation is
        # reusable. This reader reports only journal integrity; callers retain
        # the separate no-auto-resume/no-replay recovery gate.
        out = []
        def unknown(reason):
            return {"status": "INDETERMINATE", "reason": reason, "events": out}
        try:
            if self.path.is_symlink():
                return unknown("JOURNAL_UNSAFE_PATH")
            try:
                fd = os.open(str(self.path), os.O_RDONLY |
                             getattr(os, "O_NOFOLLOW", 0) |
                             getattr(os, "O_NONBLOCK", 0))
            except FileNotFoundError:
                return {"status": "OK", "events": []}
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    return unknown("JOURNAL_NOT_REGULAR")
                with os.fdopen(fd, "r", encoding="utf-8", closefd=False) as stream:
                    text = stream.read()
            finally:
                os.close(fd)
            if text and not text.endswith("\n"):
                return unknown("JOURNAL_INCOMPLETE_RECORD")
            previous = "GENESIS"
            sequence = 0
            for raw in text.splitlines():
                try:
                    event = json.loads(raw, object_pairs_hook=self._json_object,
                                       parse_constant=self._reject_constant)
                except (ValueError, TypeError, RecursionError):
                    return unknown("JOURNAL_PARSE_FAILURE")
                if type(event) is not dict:
                    return unknown("JOURNAL_RECORD_NOT_OBJECT")
                body = dict(event)
                supplied_hash = body.pop("event_hash", None)
                if (type(event.get("seq")) is not int or
                        event["seq"] != sequence + 1 or
                        event.get("prev_hash") != previous or
                        type(supplied_hash) is not str or _hash(body) != supplied_hash):
                    return unknown("JOURNAL_CHAIN_FAILURE")
                out.append(event)
                sequence = event["seq"]
                previous = supplied_hash
            return {"status": "OK", "events": out}
        except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
            return unknown("JOURNAL_READ_FAILURE")

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
            # A later record cannot lower the risk already observed for this
            # reservation, even if its hash chain is internally consistent.
            if typ=="RESERVATION_COMMITTED":
                if RISK_RANK[journal_state] < RISK_RANK["RESERVED"]:
                    journal_state="RESERVED"
            elif typ=="EXECUTION_STARTED":
                if RISK_RANK[journal_state] < RISK_RANK["EXECUTION_STARTED"]:
                    journal_state="EXECUTION_STARTED"
                possible_effect=True
            elif typ=="EXECUTION_CONFIRMED":
                if RISK_RANK[journal_state] < RISK_RANK["CONSUMED"]:
                    journal_state="CONSUMED"
                possible_effect=True; confirmed_effect=True
            elif typ=="CONFIRMED_UNUSED": confirmed_unused=True
            elif typ in ("EFFECT_INDETERMINATE","CANCEL_AFTER_POSSIBLE_EFFECT"):
                journal_state="INDETERMINATE"; possible_effect=True
        state=journal_state
        if backup_state is not None:
            bs = backup_state.get("state") if type(backup_state) is dict else None
            if type(bs) is not str or bs not in RISK_RANK:
                bs = "INDETERMINATE"
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

    def idempotent_recover(self,reservation_id,backup_state=None,*,effect_evidence=None):
        """Conservative recovery decision; optional evidence cannot enable replay.

        Existing two-argument callers retain their original behavior. When
        evidence is supplied, the same recovery entry point reconciles it and
        returns a read-only decision for the caller to enforce. No handle is
        issued or consumed, and no external effect is invoked.
        """
        recovered = self.reconstruct(reservation_id,backup_state)
        if effect_evidence is None:
            return recovered
        unknown = {**recovered, "effect_decision": "OUTCOME_UNKNOWN",
                   "automatic_resume_allowed": False, "replay_permitted": False,
                   "authorization_created": False, "execution_performed": False}
        if type(effect_evidence) is not dict:
            return unknown
        expected = {"claim_hash", "handle_hash", "payload_sha256",
                    "effect_path", "outcome_path"}
        if set(effect_evidence) != expected:
            return unknown
        result = self.reconcile_effect_evidence(
            reservation_id=reservation_id, **effect_evidence)
        if (result.get("decision") == "EXECUTED_CONFIRMED" and
                recovered.get("assessment") == "CONFIRMED_USED" and
                recovered.get("state") == "CONSUMED"):
            return {**unknown, "effect_decision": "EXECUTED_CONFIRMED"}
        return unknown


    def reconcile_effect_evidence(self, *, reservation_id, claim_hash, handle_hash,
                                  payload_sha256, effect_path, outcome_path):
        """Read-only evidence reconciliation; never authorizes or replays an effect.

        EXECUTED_CONFIRMED requires a valid ordered reservation chain, a matching
        physical postcondition and one matching integrity-checked outcome.
        Everything else is OUTCOME_UNKNOWN (including absent or corrupt evidence).
        """
        from ontology.governed_effect_outcome_accounting import _digest
        import hashlib
        unknown = {"reservation_id": reservation_id, "decision": "OUTCOME_UNKNOWN",
                   "authorization_created": False, "execution_performed": False,
                   "replay_permitted": False}
        try:
            if not all(type(x) is str and x for x in
                       (reservation_id, claim_hash, handle_hash, payload_sha256)):
                return dict(unknown)
            if len(payload_sha256) != 64 or any(c not in '0123456789abcdef' for c in payload_sha256):
                return dict(unknown)
            rep = self.replay()
            if rep.get('status') != 'OK':
                return dict(unknown)
            relevant = [e for e in rep['events'] if e.get('reservation_id') == reservation_id]
            matching = [e for e in relevant if e.get('type') in ('EXECUTION_STARTED', 'EXECUTION_CONFIRMED')]
            if len(matching) != 2 or [e['type'] for e in matching] != ['EXECUTION_STARTED', 'EXECUTION_CONFIRMED']:
                return dict(unknown)
            started, confirmed = matching
            if not all(e.get('claim_hash') == claim_hash and e.get('handle_hash') == handle_hash
                       for e in matching) or confirmed.get('payload_sha256') != payload_sha256:
                return dict(unknown)
            if any(e.get('type') in ('EFFECT_INDETERMINATE', 'CANCEL_AFTER_POSSIBLE_EFFECT')
                   for e in relevant):
                return dict(unknown)
            effect, ledger = Path(effect_path), Path(outcome_path)
            if (effect.is_symlink() or ledger.is_symlink() or
                not effect.is_file() or not ledger.is_file()):
                return dict(unknown)
            if hashlib.sha256(effect.read_bytes()).hexdigest() != payload_sha256:
                return dict(unknown)
            lines = ledger.read_text(encoding='utf-8').splitlines()
            if len(lines) != 1:
                return dict(unknown)
            outcome = json.loads(lines[0])
            if type(outcome) is not dict:
                return dict(unknown)
            supplied_hash = outcome.pop('event_hash', None)
            if type(supplied_hash) is not str or supplied_hash != _digest(outcome):
                return dict(unknown)
            if (outcome.get('schema') != 'oce.p162.pc4.outcome.v1' or
                outcome.get('effect_status') != 'EFFECT_CONFIRMED' or
                outcome.get('claim_hash') != claim_hash or
                outcome.get('handle_hash') != handle_hash or
                outcome.get('revocation_state') != 'ACTIVE' or
                type(outcome.get('observed_postcondition')) is not dict or
                outcome['observed_postcondition'].get('verified') is not True):
                return dict(unknown)
            return {**unknown, 'decision': 'EXECUTED_CONFIRMED'}
        except (OSError, ValueError, TypeError, KeyError, UnicodeError, OverflowError):
            return dict(unknown)

    def bind_restart_recovery_context(self, reservation_id, context, *, effect_evidence=None, backup_state=None):
        """Bind a restart assessment to a preexisting context before any dispatch.

        Recovery never issues handles, executes effects, or grants a fresh lease.
        Fail closed if the context is already begun or lacks a recovery gate.
        """
        from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
        if type(context) is not GovernedFilesystemEffectContext:
            raise TypeError('p162_pc4_restart_context_type_required')
        if context._begun or context.recovery_decision is not None:
            raise RuntimeError('p162_pc4_restart_context_already_used_or_bound')
        # Bind the deny marker first: even an unexpected failure while reading
        # evidence must not leave a caller-supplied context dispatchable.
        context.recovery_decision = {'effect_decision': 'OUTCOME_UNKNOWN',
                                     'automatic_resume_allowed': False,
                                     'replay_permitted': False}
        decision = self.idempotent_recover(reservation_id, backup_state,
                                           effect_evidence=effect_evidence)
        if type(decision) is not dict:
            raise RuntimeError('p162_pc4_restart_recovery_invalid_decision')
        context.recovery_decision = {**decision, 'automatic_resume_allowed': False,
                                     'replay_permitted': False}
        return dict(context.recovery_decision)

    def _count(self):
        r=self.replay()
        return len(r["events"]) if isinstance(r,dict) and r.get("status")=="OK" else 0
    def _last_hash(self):
        r=self.replay()
        if isinstance(r,dict) and r.get("status")=="OK" and r["events"]: return r["events"][-1]["event_hash"]
        return "GENESIS"
