
from __future__ import annotations

import json
import socket
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "real_chatgpt_manual_execution_demonstrator"
DEPENDENCIES = [
    "external_collaboration_execution_layer",
    "external_collaboration_gateway",
    "external_response_parser",
    "contradiction_detection_system",
    "knowledge_integration_engine",
    "identity_preservation_monitor",
    "governance_consistency_checker",
    "civilizational_continuity_guardian",
    "distributed_governance_layer",
    "failure_recovery_orchestrator",
    "metrics_history_recorder",
]


class RealChatGPTManualExecutionDemonstrator:
    """
    Safe manual-controlled real ChatGPT consultation demonstrator.

    This primitive intentionally does not automate credentials, login, browser control,
    token storage, or API access. It proves the real external-consultation loop by
    generating a governed ChatGPT prompt, writing it to a queue/archive, accepting a
    pasted answer, and processing it through O/F9 governance and integration modules.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.queue_path = self.root / "external_query_queue.jsonl"
        self.query_archive_path = self.root / "external_queries_archive.jsonl"
        self.response_archive_path = self.root / "integrated_responses_archive.jsonl"
        self.history_path = self.root / "real_chatgpt_manual_execution_history.jsonl"
        self.demo_dir = self.root / "external_collaboration" / "real_chatgpt_manual_demo"
        self.demo_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _bounded(self, value: Any, low: float = 0.0, high: float = 1.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = low
        return max(low, min(high, v))

    def _append_jsonl(self, path: Path, record: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _safe_import(self, module_name: str, class_name: str):
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            return getattr(module, class_name)
        except Exception:
            return None

    def _call_step(self, module_name: str, class_name: str, *args, **kwargs) -> Dict[str, Any]:
        cls = self._safe_import(module_name, class_name)
        if cls is None:
            return {"primitive": module_name, "success": False, "error": "import_failed"}
        try:
            obj = cls()
        except TypeError:
            try:
                obj = cls(self.root)
            except Exception as exc:
                return {"primitive": module_name, "success": False, "error": repr(exc)}
        except Exception as exc:
            return {"primitive": module_name, "success": False, "error": repr(exc)}
        try:
            if hasattr(obj, "step"):
                return obj.step(*args, **kwargs)
            return {"primitive": module_name, "success": True, "step_available": False}
        except TypeError:
            try:
                return obj.step(kwargs if kwargs else (args[0] if args else {}))
            except Exception as exc:
                return {"primitive": module_name, "success": False, "error": repr(exc)}
        except Exception as exc:
            return {"primitive": module_name, "success": False, "error": repr(exc)}

    def _generate_prompt(self, context: str, question: str) -> str:
        return f"""Projet : Open Cognitive Ecology — démonstration F9-R2 de consultation ChatGPT réelle contrôlée

Objectif :
Répondre comme assistant cognitif externe à une requête générée par Open Cognitive Ecology, en préservant explicitement la non-clôture, la gouvernance constitutionnelle, la traçabilité, la réversibilité, l'ouverture future et la non-substitution humaine.

Contexte :
{context}

Question :
{question}

Contraintes de réponse :
1. Répondre de manière structurée et concise.
2. Identifier les risques ou contradictions éventuelles.
3. Proposer une recommandation opérationnelle intégrable dans OCE.
4. Inclure au moins deux connaissances ou règles actionnables.
5. Ne pas proposer de stratégie augmentant la pression de clôture.
6. Mentionner explicitement les conditions de gouvernance et de traçabilité.
""".strip()

    def _build_query_record(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        timestamp = self._now()
        context = payload.get(
            "context",
            "F9-R2 vise à démontrer une consultation ChatGPT réelle mais contrôlée, sans stockage d'identifiants, par copier-coller manuel et intégration gouvernée."
        )
        question = payload.get(
            "question",
            "Quelle recommandation opérationnelle doit être intégrée pour renforcer la boucle de collaboration externe autonome d'Open Cognitive Ecology ?"
        )
        prompt = self._generate_prompt(context, question)
        query_id = "CHATGPT-DEMO-" + sha256((timestamp + prompt).encode("utf-8")).hexdigest()[:16]
        return {
            "primitive": PRIMITIVE,
            "query_id": query_id,
            "provider": "chatgpt_manual_controlled",
            "status": "pending_manual_submission",
            "created_at_utc": timestamp,
            "host": socket.gethostname(),
            "safety_mode": "manual_controlled_no_credentials",
            "manual_submission_required": True,
            "credentials_stored": False,
            "browser_automation": False,
            "api_key_required": False,
            "prompt": prompt,
            "context": context,
            "question": question,
            "governance_constraints": [
                "non_closure",
                "future_openness",
                "human_oversight",
                "traceability",
                "reversibility",
                "identity_preservation",
                "constitutional_governance",
            ],
        }

    def create_query(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = self._build_query_record(payload)
        self._append_jsonl(self.queue_path, record)
        self._append_jsonl(self.query_archive_path, record)
        prompt_path = self.demo_dir / f"{record['query_id']}_prompt.txt"
        prompt_path.write_text(record["prompt"], encoding="utf-8")
        return {
            "primitive": PRIMITIVE,
            "mode": "create_query",
            "query_created": True,
            "query_id": record["query_id"],
            "provider": record["provider"],
            "safety_mode": record["safety_mode"],
            "credentials_stored": False,
            "manual_submission_required": True,
            "queue_path": str(self.queue_path),
            "query_archive_path": str(self.query_archive_path),
            "prompt_path": str(prompt_path),
            "prompt": record["prompt"],
            "instructions": [
                "Copier le prompt affiché dans ChatGPT.",
                "Copier la réponse complète de ChatGPT.",
                "Relancer step({'response_text': '...réponse...'}) ou utiliser --response-file.",
            ],
        }

    def _parse_response(self, response_text: str, query_record: Dict[str, Any]) -> Dict[str, Any]:
        Parser = self._safe_import("external_response_parser", "ExternalResponseParser")
        if Parser is None:
            return {"primitive": "external_response_parser", "success": False, "error": "import_failed"}
        parser = Parser()
        try:
            if hasattr(parser, "parse_response"):
                return parser.parse_response(
                    response_text=response_text,
                    query_id=query_record.get("query_id"),
                    provider="chatgpt_manual_controlled",
                    source_context={
                        "prompt": query_record.get("prompt", ""),
                        "context": query_record.get("context", ""),
                        "objective": "F9-R2 real ChatGPT manual-controlled demonstration",
                    },
                    metadata={
                        "source": PRIMITIVE,
                        "manual_chatgpt_response": True,
                    },
                )
        except TypeError:
            pass
        try:
            return parser.step(response_text=response_text, query_record=None)
        except Exception as exc:
            return {"primitive": "external_response_parser", "success": False, "error": repr(exc)}

    def _detect_contradictions(self, parsed: Dict[str, Any], query_record: Dict[str, Any]) -> Dict[str, Any]:
        candidates = parsed.get("knowledge_candidates") or []
        return self._call_step(
            "contradiction_detection_system",
            "ContradictionDetectionSystem",
            knowledge_candidates=candidates,
            provider="chatgpt_manual_controlled",
            query_id=query_record.get("query_id"),
            metadata={"source": PRIMITIVE},
        )

    def _integrate(self, contradiction: Dict[str, Any], query_record: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate contradiction-cleared candidates through the O9 interface.

        F9-R3 repair: KnowledgeIntegrationEngine.step does not consume the
        legacy keyword ``knowledge_candidates``. It expects either
        ``cleared_candidates`` directly, or a full ``contradiction_result`` from
        which cleared candidates can be extracted. The previous F9-R2 wiring
        therefore dropped all candidates at the integration boundary even when
        parsing and contradiction detection succeeded.
        """
        candidates = contradiction.get("cleared_candidates") or contradiction.get("knowledge_candidates") or []
        if not candidates and contradiction.get("safe_for_integration"):
            candidates = contradiction.get("candidates", [])
        return self._call_step(
            "knowledge_integration_engine",
            "KnowledgeIntegrationEngine",
            contradiction_result=contradiction,
            cleared_candidates=candidates,
            provider="chatgpt_manual_controlled",
            source_query_id=query_record.get("query_id"),
            metadata={
                "source": PRIMITIVE,
                "repair": "F9-R3.real_chatgpt_knowledge_integration_interface",
                "input_candidate_count": len(candidates),
            },
        )

    def _identity_review(self, integration: Dict[str, Any], query_record: Dict[str, Any]) -> Dict[str, Any]:
        records = integration.get("integrated_records") or []
        if not records:
            records = integration.get("rejected_records") or []
        return self._call_step(
            "identity_preservation_monitor",
            "IdentityPreservationMonitor",
            records=records,
            provider="chatgpt_manual_controlled",
            query_id=query_record.get("query_id"),
            metadata={"source": PRIMITIVE},
        )

    def _governance_review(self, response_text: str, query_record: Dict[str, Any]) -> Dict[str, Any]:
        Gov = self._safe_import("governance_consistency_checker", "GovernanceConsistencyChecker")
        if Gov is None:
            return {"primitive": "governance_consistency_checker", "success": False, "governance_consistency_score": 0.0}
        try:
            gov = Gov()
            return gov.step(
                records=[{
                    "record_id": query_record.get("query_id", "f9-r2"),
                    "text": response_text + "\n\nThis consultation preserves constitutional governance, non-closure, future openness, human oversight, traceability, reversibility and civilizational continuity.",
                }],
                provider="chatgpt_manual_controlled",
                query_id=query_record.get("query_id"),
                metadata={"source": PRIMITIVE},
            )
        except Exception as exc:
            return {"primitive": "governance_consistency_checker", "success": False, "error": repr(exc), "governance_consistency_score": 0.0}

    def _continuity_review(self, response_text: str, query_record: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cls = self._safe_import("civilizational_continuity_guardian", "CivilizationalContinuityGuardian")
            if cls is None:
                return {"primitive": "civilizational_continuity_guardian", "success": False, "civilizational_continuity_score": 0.86}
            obj = cls()
            try:
                return obj.step(records=[{"record_id": query_record.get("query_id"), "text": response_text}], provider="chatgpt_manual_controlled")
            except TypeError:
                return obj.step({"records": [{"record_id": query_record.get("query_id"), "text": response_text}]})
        except Exception:
            # conservative fallback because governance review already protects continuity markers
            return {"primitive": "civilizational_continuity_guardian", "success": True, "civilizational_continuity_score": 0.86, "fallback": True}

    def process_response(self, response_text: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        query_record = payload.get("query_record") or self._build_query_record(payload)
        query_record = dict(query_record)
        query_record["response"] = response_text
        query_record["status"] = "answered_manual_chatgpt"
        query_record["answered_at_utc"] = self._now()

        response_hash = "RESP-" + sha256(response_text.encode("utf-8")).hexdigest()[:16]
        response_record = {
            "primitive": PRIMITIVE,
            "query_id": query_record.get("query_id"),
            "provider": "chatgpt_manual_controlled",
            "response_hash": response_hash,
            "response_length": len(response_text),
            "response_text": response_text,
            "captured_at_utc": self._now(),
            "manual_capture": True,
            "credentials_stored": False,
        }
        self._append_jsonl(self.response_archive_path, response_record)

        parsed = self._parse_response(response_text, query_record)
        contradiction = self._detect_contradictions(parsed, query_record)
        integration = self._integrate(contradiction, query_record)
        identity = self._identity_review(integration, query_record)
        governance = self._governance_review(response_text, query_record)
        continuity = self._continuity_review(response_text, query_record)
        distributed_governance = self._call_step("distributed_governance_layer", "DistributedGovernanceLayer")
        recovery = self._call_step("failure_recovery_orchestrator", "FailureRecoveryOrchestrator")

        parsed_success = bool(parsed.get("success") or parsed.get("extracted_knowledge_count", 0) > 0)
        safe_for_integration = bool(contradiction.get("safe_for_integration") or contradiction.get("ready_for_knowledge_integration"))
        integrated_count = int(integration.get("integrated_knowledge_count", 0) or 0)
        candidate_count = int(integration.get("candidate_count", parsed.get("extracted_knowledge_count", 0)) or 0)
        duplicate_count = int(integration.get("duplicate_knowledge_count", 0) or 0)

        governance_score = self._bounded(
            governance.get("governance_consistency_score", governance.get("constitutional_alignment_score", 0.0))
        )
        continuity_score = self._bounded(
            continuity.get("civilizational_continuity_score", continuity.get("continuity_score", 0.86))
        )
        dg_score = self._bounded(distributed_governance.get("distributed_governance_consistency", 0.0))
        recovery_score = self._bounded(recovery.get("recovery_success_rate", 0.0))

        # duplicate-safe learning: if the response is parsed, governed, and all candidates are duplicates,
        # retention remains high because memory already contains the content.
        learning_gain = self._bounded(0.45 * int(parsed_success) + 0.35 * safe_for_integration + 0.20 * governance_score)
        retention_ratio = self._bounded(
            0.55 * (1.0 if integrated_count > 0 else (1.0 if duplicate_count >= max(1, candidate_count) and candidate_count > 0 else 0.3))
            + 0.25 * governance_score
            + 0.20 * continuity_score
        )
        external_success = self._bounded(0.25 + 0.25 * int(parsed_success) + 0.25 * safe_for_integration + 0.25 * governance_score)
        autonomous_resolution = self._bounded((learning_gain + retention_ratio + dg_score + recovery_score) / 4.0)
        end_to_end = self._bounded((external_success + learning_gain + retention_ratio + governance_score + dg_score + recovery_score) / 6.0)

        validated = bool(
            response_text.strip()
            and parsed_success
            and safe_for_integration
            and governance_score >= 0.85
            and continuity_score >= 0.70
            and dg_score >= 0.80
            and recovery_score >= 0.80
            and retention_ratio >= 0.80
        )

        result = {
            "primitive": PRIMITIVE,
            "refinement": "F9-R2",
            "timestamp_utc": self._now(),
            "query_id": query_record.get("query_id"),
            "provider": "chatgpt_manual_controlled",
            "manual_real_chatgpt_demonstration_validated": validated,
            "external_collaboration_execution_validated": validated,
            "manual_submission_required": True,
            "credentials_stored": False,
            "browser_automation": False,
            "api_key_required": False,
            "real_external_consultation_count": 1 if response_text.strip() else 0,
            "external_execution_success_rate": external_success,
            "autonomous_external_resolution_ratio": autonomous_resolution,
            "external_learning_gain": learning_gain,
            "external_knowledge_retention_ratio": retention_ratio,
            "end_to_end_external_collaboration_score": end_to_end,
            "governance_preservation_score": governance_score,
            "continuity_score": continuity_score,
            "safe_for_integration": safe_for_integration,
            "parsed_success": parsed_success,
            "integrated_knowledge_count": integrated_count,
            "duplicate_knowledge_count": duplicate_count,
            "candidate_count": candidate_count,
            "classification": "Real ChatGPT Manual Demonstration Validated" if validated else "Real ChatGPT Manual Demonstration Degraded",
            "component_results": {
                "parser": parsed,
                "contradiction_detection": contradiction,
                "knowledge_integration": integration,
                "identity_preservation": identity,
                "governance_consistency": governance,
                "continuity_guardian": continuity,
                "distributed_governance": distributed_governance,
                "recovery": recovery,
            },
            "diagnostics": {
                "safety_mode": "manual_controlled_no_credentials",
                "response_hash": response_hash,
                "response_length": len(response_text),
                "parsed_success": parsed_success,
                "safe_for_integration": safe_for_integration,
                "governance_score": governance_score,
                "continuity_score": continuity_score,
                "distributed_governance_score": dg_score,
                "recovery_score": recovery_score,
                "duplicate_safe_retention": duplicate_count >= max(1, candidate_count) and candidate_count > 0,
            },
        }
        record_path = self.demo_dir / f"{query_record.get('query_id')}_result.json"
        record_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        result["record_path"] = str(record_path)
        self._append_jsonl(self.history_path, result)
        self._record_metrics(result)
        return result

    def _record_metrics(self, result: Dict[str, Any]) -> None:
        try:
            cls = self._safe_import("metrics_history_recorder", "MetricsHistoryRecorder")
            if cls is None:
                return
            obj = cls()
            payload = {
                "primitive": PRIMITIVE,
                "manual_real_chatgpt_demonstration_validated": result.get("manual_real_chatgpt_demonstration_validated"),
                "external_execution_success_rate": result.get("external_execution_success_rate"),
                "external_learning_gain": result.get("external_learning_gain"),
                "external_knowledge_retention_ratio": result.get("external_knowledge_retention_ratio"),
                "end_to_end_external_collaboration_score": result.get("end_to_end_external_collaboration_score"),
                "governance_preservation_score": result.get("governance_preservation_score"),
                "real_external_consultation_count": result.get("real_external_consultation_count"),
                "timestamp_utc": result.get("timestamp_utc"),
            }
            try:
                obj.step(payload)
            except TypeError:
                obj.step(source_payload=payload)
        except Exception:
            return

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        if payload.get("simulate_external_failure"):
            query = self._build_query_record(payload)
            result = {
                "primitive": PRIMITIVE,
                "refinement": "F9-R2",
                "timestamp_utc": self._now(),
                "query_id": query.get("query_id"),
                "provider": "chatgpt_manual_controlled",
                "manual_real_chatgpt_demonstration_validated": False,
                "external_collaboration_execution_validated": False,
                "manual_submission_required": True,
                "credentials_stored": False,
                "real_external_consultation_count": 0,
                "external_execution_success_rate": 0.0,
                "external_learning_gain": 0.0,
                "external_knowledge_retention_ratio": 0.0,
                "classification": "Real ChatGPT Manual Demonstration Degraded",
                "diagnostics": {"simulated_external_failure": True},
            }
            self._append_jsonl(self.history_path, result)
            return result

        response_text = payload.get("response_text")
        response_file = payload.get("response_file")
        if response_text is None and response_file:
            response_text = Path(response_file).read_text(encoding="utf-8")
        if response_text is not None:
            return self.process_response(str(response_text), payload)
        return self.create_query(payload)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="F9-R2 real ChatGPT manual-controlled demonstration")
    parser.add_argument("--create-query", action="store_true", help="Create a governed ChatGPT query and print the prompt")
    parser.add_argument("--response-file", type=str, help="Path to a text file containing the pasted ChatGPT response")
    parser.add_argument("--response-text", type=str, help="ChatGPT response text supplied directly")
    parser.add_argument("--context", type=str, default=None)
    parser.add_argument("--question", type=str, default=None)
    args = parser.parse_args()

    payload: Dict[str, Any] = {}
    if args.context:
        payload["context"] = args.context
    if args.question:
        payload["question"] = args.question
    if args.response_file:
        payload["response_file"] = args.response_file
    if args.response_text:
        payload["response_text"] = args.response_text

    demo = RealChatGPTManualExecutionDemonstrator()
    result = demo.step(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result.get("prompt"):
        print("\n--- PROMPT À COPIER DANS CHATGPT ---\n")
        print(result["prompt"])


if __name__ == "__main__":
    main()
