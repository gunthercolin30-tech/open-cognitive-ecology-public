
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from typing import Any

PRIMITIVE = "governed_external_revision_pipeline"
DEPENDENCIES = ["interaction_queue_manager","canonical_external_influence_ledger","external_action_proposal_queue","external_revision_traceability_extension","external_commit_traceability_hook","external_decision_record_extension","execution_request_generation","governed_execution_dispatcher","human_review_gate","controlled_execution_layer","outcome_monitoring","effectiveness_assessment"]
PIPELINE_STAGES = ["external_query","canonical_influence","action_proposal","revision_proposal","patch_scope","test_plan","human_review","execution_request","governed_dispatch","controlled_execution","post_impact_audit"]

class GovernedExternalRevisionPipeline:
    primitive = PRIMITIVE
    dependencies = DEPENDENCIES

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.pipeline_dir = self.root / "external_revision_pipeline"
        self.pipeline_log = self.root / "external_revision_pipeline.jsonl"
        self.latest_path = self.pipeline_dir / "latest_governed_external_revision_pipeline.json"
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)

    def _now(self): return datetime.now(timezone.utc).isoformat()
    def _list(self, v):
        if v is None: return []
        if isinstance(v, list): return v
        if isinstance(v, tuple): return list(v)
        return [v]
    def _hash(self, v):
        return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    def _id_seed(self, payload, query_id, influence_id, action_id):
        return self._hash({"q":query_id,"i":influence_id,"a":action_id,"s":payload.get("proposal_summary",""),"t":self._list(payload.get("target_files"))})[:12]

    def _derive_ids(self, payload: dict[str, Any]):
        trace = payload.get("trace_chain") if isinstance(payload.get("trace_chain"), dict) else {}
        cand = payload.get("execution_request_candidate") if isinstance(payload.get("execution_request_candidate"), dict) else {}
        query_id = payload.get("query_id") or trace.get("query_id") or cand.get("query_id")
        influence_id = payload.get("external_influence_id") or trace.get("external_influence_id") or cand.get("external_influence_id")
        action_id = payload.get("action_proposal_id") or trace.get("action_proposal_id") or cand.get("action_proposal_id")
        exec_id = payload.get("execution_request_id") or trace.get("execution_request_id") or cand.get("execution_request_id")
        seed = self._id_seed(payload, query_id, influence_id, action_id)
        if influence_id and not action_id: action_id = "ACTPROP-" + seed
        if action_id and not exec_id: exec_id = "EXREQ-" + seed
        return {
            "query_id": str(query_id) if query_id else None,
            "external_influence_id": str(influence_id) if influence_id else None,
            "action_proposal_id": str(action_id) if action_id else None,
            "execution_request_id": str(exec_id) if exec_id else None,
            "decision_record_id": str(payload.get("decision_record_id") or "DECISION-R10-" + seed),
            "review_id": str(payload.get("review_id") or "HREV-R10-" + seed),
            "dispatch_id": str(payload.get("dispatch_id") or "DISPATCH-R10-" + seed),
            "commit_id": str(payload.get("commit_id") or "pending_human_or_codex_commit"),
        }

    def _blocked(self, payload, ids):
        out = []
        if payload.get("direct_execution_requested") or payload.get("direct_write_requested"): out.append("direct_execution")
        if payload.get("direct_commit_requested"): out.append("direct_commit")
        for k in ["query_id","external_influence_id","action_proposal_id","execution_request_id"]:
            if not ids.get(k): out.append(k + "_missing")
        if not self._list(payload.get("test_plan")): out.append("test_plan_absent")
        if not self._list(payload.get("rollback_plan")): out.append("rollback_plan_absent")
        if not self._list(payload.get("patch_scope", payload.get("target_files"))): out.append("patch_scope_absent")
        if payload.get("human_review_required") is False: out.append("human_review_not_required")
        return sorted(set(out))

    def _scores(self, payload, ids, blocked):
        trace_keys = ["query_id","external_influence_id","action_proposal_id","execution_request_id","decision_record_id","review_id","dispatch_id","commit_id"]
        trace = sum(1 for k in trace_keys if ids.get(k)) / len(trace_keys)
        checks = [bool(self._list(payload.get("patch_scope", payload.get("target_files")))), bool(self._list(payload.get("test_plan"))), bool(self._list(payload.get("rollback_plan"))), bool(payload.get("proposal_summary", payload.get("revision_summary",""))), bool(payload.get("commit_rationale", payload.get("proposal_summary",""))), payload.get("human_review_required", True) is True]
        complete = sum(1 for c in checks if c) / len(checks)
        safety = max(0.0, 1.0 - min(len(blocked), 6) / 6.0)
        audit = max(0.0, min(1.0, 0.45*trace + 0.35*complete + 0.20*safety))
        return {"traceability_score": round(trace,6), "pipeline_completeness_score": round(complete,6), "pipeline_auditability_score": round(audit,6)}

    def _decision(self, blocked, audit):
        if any(x in blocked for x in ["direct_execution","direct_commit","human_review_not_required"]): return "pipeline_blocked"
        if not blocked and audit >= 0.85: return "pipeline_ready_for_human_review"
        if audit >= 0.55: return "pipeline_partial_requires_completion"
        return "pipeline_missing_traceability"

    def _append_jsonl(self, path, record, fs_context=None):
        if fs_context is None:
            raise PermissionError("JSONL append requires preissued filesystem effect context")
        data = (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fs_context.execute_path("jsonl_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("jsonl_append", "FS_APPEND_BYTES", path, data)
    def _safe(self, s):
        return ("".join(c if c.isalnum() or c in "-_" else "-" for c in str(s)).strip("-") or "pipeline")[:120]

    def _persist(self, r, fs_context=None):
        d = self.pipeline_dir / self._safe(r["pipeline_id"]); d.mkdir(parents=True, exist_ok=True)
        paths = {
            "revision_proposal_path": d/"revision_proposal.md",
            "patch_scope_path": d/"patch_scope.json",
            "test_plan_path": d/"test_plan.json",
            "commit_rationale_path": d/"commit_rationale.md",
            "pipeline_record_path": d/"pipeline_record.json",
        }
        paths["revision_proposal_path"].write_text(f"# Governed External Revision Proposal\\n\\nPipeline: {r['pipeline_id']}\\n\\nSummary: {r.get('proposal_summary','')}\\n\\nDecision: {r.get('pipeline_decision','')}\\n", encoding="utf-8")
        paths["patch_scope_path"].write_text(json.dumps(r["patch_scope"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        paths["test_plan_path"].write_text(json.dumps(r["test_plan"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        paths["commit_rationale_path"].write_text(str(r["commit_rationale"]), encoding="utf-8")
        paths["pipeline_record_path"].write_text(json.dumps(r, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.latest_path.write_text(json.dumps(r, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._append_jsonl(self.pipeline_log, r, fs_context=fs_context)
        out = {k: str(v) for k,v in paths.items()}
        out.update({"pipeline_folder": str(d), "pipeline_log_path": str(self.pipeline_log), "latest_path": str(self.latest_path)})
        return out

    def step(self, payload: dict[str, Any] | None = None, persist: bool = False, **kwargs):
        fs_context = kwargs.pop("fs_context", None)
        payload = {} if payload is None else (payload if isinstance(payload, dict) else {"raw_payload": payload})
        if kwargs: payload = {**payload, **kwargs}
        ids = self._derive_ids(payload)
        blocked = self._blocked(payload, ids)
        scores = self._scores(payload, ids, blocked)
        decision = self._decision(blocked, scores["pipeline_auditability_score"])
        patch_scope = self._list(payload.get("patch_scope", payload.get("target_files")))
        test_plan = self._list(payload.get("test_plan"))
        rollback_plan = self._list(payload.get("rollback_plan"))
        summary = str(payload.get("proposal_summary", payload.get("revision_summary", "")))
        rationale = str(payload.get("commit_rationale", summary or "pending governed rationale"))
        core = {"ids": ids, "patch_scope": patch_scope, "test_plan": test_plan, "rollback_plan": rollback_plan, "proposal_summary": summary, "commit_rationale": rationale, "blocked_reasons": blocked, "decision": decision}
        pipeline_hash = self._hash(core)
        pipeline_id = str(payload.get("pipeline_id") or "GEXREV-" + pipeline_hash[:16])
        trace_chain = {**ids, "pipeline_id": pipeline_id}
        exec_candidate = {"execution_request_id": ids.get("execution_request_id"), "query_id": ids.get("query_id"), "external_influence_id": ids.get("external_influence_id"), "action_proposal_id": ids.get("action_proposal_id"), "pipeline_id": pipeline_id, "requires_governed_dispatch": True, "requires_human_review": True, "requires_controlled_execution": True, "direct_execution_allowed": False, "test_plan_required": True, "rollback_required": True}
        r = {"success": True, "primitive": PRIMITIVE, "dependencies": DEPENDENCIES, "timestamp_utc": self._now(), "pipeline_id": pipeline_id, "pipeline_hash": pipeline_hash, "pipeline_stages": PIPELINE_STAGES, "trace_chain": trace_chain, "trace_chain_complete": all(ids.get(k) for k in ["query_id","external_influence_id","action_proposal_id","execution_request_id"]), "query_id": ids.get("query_id"), "external_influence_id": ids.get("external_influence_id"), "action_proposal_id": ids.get("action_proposal_id"), "execution_request_id": ids.get("execution_request_id"), "decision_record_id": ids.get("decision_record_id"), "review_id": ids.get("review_id"), "dispatch_id": ids.get("dispatch_id"), "commit_id": ids.get("commit_id"), "proposal_summary": summary, "patch_scope": patch_scope, "test_plan": test_plan, "rollback_plan": rollback_plan, "commit_rationale": rationale, "human_review_required": True, "governed_dispatch_required": True, "controlled_execution_required": True, "direct_execution_allowed": False, "direct_commit_allowed": False, "execution_request_candidate": exec_candidate, "blocked_reasons": blocked, "pipeline_decision": decision, **scores, "schema_fields_present": True}
        if persist: r.update(self._persist(r, fs_context=fs_context))
        return r

if __name__ == "__main__":
    print(json.dumps(GovernedExternalRevisionPipeline().step(), ensure_ascii=False, indent=2, sort_keys=True))
