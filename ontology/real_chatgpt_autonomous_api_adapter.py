# -*- coding: utf-8 -*-
from __future__ import annotations

from ontology.governed_network_effector import GovernedNetworkEffector, GovernedNetworkRequest, UrllibTrustedTransport

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PRIMITIVE = "real_chatgpt_autonomous_api_adapter"

DEPENDENCIES = [
    "external_collaboration_execution_layer",
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


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash(text: Any, prefix: str = "OPENAI") -> str:
    return prefix + "-" + hashlib.sha256(str(text).encode("utf-8", errors="ignore")).hexdigest()[:16]


def _safe_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except Exception:
        number = default
    return max(low, min(high, number))


P162_G63B4C_AUTH_NETWORK_MEDIATED = True

class RealChatGPTAutonomousAPIAdapter:
    """F9-R5 governed autonomous ChatGPT/OpenAI API adapter.

    This adapter uses OpenAI's Responses API over HTTPS. It never stores API keys,
    cookies, passwords, or browser state. The key is read only from OPENAI_API_KEY.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.history_path = self.root / "real_chatgpt_autonomous_api_history.jsonl"
        self.result_dir = self.root / "external_collaboration" / "real_chatgpt_api"
        self.result_dir.mkdir(parents=True, exist_ok=True)

        self.governed_network_context = None

    def set_governed_network_context(self, context: Optional[Dict[str, Any]]) -> None:
        self.governed_network_context = context

    def _p162_governed_network(self):
        context = self.governed_network_context
        if not isinstance(context, dict) or context.get("handle") is None or context.get("brokered_use") is None:
            raise PermissionError("governed_brokered_network_context_required")
        effector = context.get("effector") or GovernedNetworkEffector(
            transport=UrllibTrustedTransport(), credential_resolver=context.get("credential_resolver"))
        return context, effector


    def _append_jsonl(self, path: Path, obj: Dict[str, Any], fs_context=None) -> None:
        if fs_context is None:
            raise PermissionError("JSONL append requires preissued filesystem effect context")
        data = (json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fs_context.execute_path("jsonl_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("jsonl_append", "FS_APPEND_BYTES", path, data)
    def _extract_output_text(self, data: Dict[str, Any]) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"].strip()
        pieces = []
        for item in data.get("output", []) or []:
            for content in item.get("content", []) or []:
                if isinstance(content, dict):
                    if isinstance(content.get("text"), str):
                        pieces.append(content["text"])
                    elif isinstance(content.get("output_text"), str):
                        pieces.append(content["output_text"])
        if pieces:
            return "\n".join(pieces).strip()
        # Defensive fallback for future JSON shapes.
        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in {"text", "output_text"} and isinstance(value, str):
                        pieces.append(value)
                    else:
                        walk(value)
            elif isinstance(obj, list):
                for x in obj:
                    walk(x)
        walk(data)
        return "\n".join(dict.fromkeys(pieces)).strip()

    def _build_request_body(self, prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = str(
            payload.get("model")
            or os.environ.get("OCE_OPENAI_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or "gpt-4.1-mini"
        )
        max_output_tokens = _safe_int(
            payload.get("max_output_tokens") or os.environ.get("OCE_OPENAI_MAX_OUTPUT_TOKENS"),
            default=900,
            low=120,
            high=4096,
        )
        system_message = (
            "You are acting as an external cognitive assistant for Open Cognitive Ecology. "
            "Return a concise, structured answer with: analysis, risks, operational recommendations, "
            "conditions for governed integration, and validation tests. Preserve constitutional governance, "
            "human oversight, non-closure, future openness, civilizational continuity, traceability, and reversibility. "
            "Do not propose closure-increasing strategies. Treat all recommendations as non-authoritative by default."
        )
        return {
            "model": model,
            "input": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            "max_output_tokens": max_output_tokens,
        }

    def step(self, payload: Optional[Dict[str, Any]] = None, fs_context=None) -> Dict[str, Any]:
        payload = dict(payload or {})
        prompt = str(payload.get("prompt") or payload.get("external_prompt") or "").strip()
        query_id = str(payload.get("query_id") or _hash(f"openai|{time.time()}", "OPENAIQ"))
        provider = str(payload.get("provider") or "openai_api")
        timeout = _safe_int(payload.get("timeout_seconds") or os.environ.get("OCE_OPENAI_TIMEOUT_SECONDS"), 60, 5, 300)
        started = time.time()

        brokered_credential_available = bool(isinstance(self.governed_network_context, dict) and self.governed_network_context.get("brokered_use") is not None)
        endpoint = str(os.environ.get("OCE_OPENAI_RESPONSES_ENDPOINT") or "https://api.openai.com/v1/responses")

        if not prompt:
            result = {
                "primitive": PRIMITIVE,
                "timestamp_utc": _utc(),
                "success": False,
                "provider": provider,
                "adapter_mode": "openai_api_adapter",
                "query_id": query_id,
                "response_text": "",
                "response_length": 0,
                "failure_reason": "empty_prompt",
                "credentials_stored": False,
                "browser_automation": False,
                "brokered_credential_available": brokered_credential_available,
                "latency": round(time.time() - started, 6),
            }
            self._append_jsonl(self.history_path, result, fs_context=fs_context)
            return result

        if not brokered_credential_available:
            result = {"primitive":PRIMITIVE,"timestamp_utc":_utc(),"success":False,"provider":provider,
                      "adapter_mode":"openai_api_adapter_governed","query_id":query_id,"response_text":"",
                      "response_length":0,"failure_reason":"governed_brokered_network_context_required",
                      "credentials_stored":False,"browser_automation":False,
                      "brokered_credential_available":False,"raw_secret_observed":False,
                      "latency":round(time.time()-started,6)}
            self._append_jsonl(self.history_path,result, fs_context=fs_context)
            return result

        body = self._build_request_body(prompt, payload)
        raw = json.dumps(body).encode("utf-8")
        context, effector = self._p162_governed_network()

        try:
            effect = effector.execute(
                request=GovernedNetworkRequest("POST", endpoint,
                    {"Content-Type":"application/json","User-Agent":"Open-Cognitive-Ecology-F9-R5/1.0"},
                    raw, timeout_seconds=float(timeout), idempotent=False),
                handle=context.get("handle"), brokered_use=context.get("brokered_use"),
                adapter_id=context.get("adapter_id"), effector_id=context.get("effector_id"),
                now_iso=context.get("now_iso"))
            effect_status=effect.get("status")
            if effect_status != "EFFECT_CONFIRMED":
                result={"primitive":PRIMITIVE,"timestamp_utc":_utc(),"success":False,"provider":provider,
                        "adapter_mode":"openai_api_adapter_governed","query_id":query_id,"response_text":"",
                        "response_length":0,"failure_reason":"governed_network_effect:"+str(effect_status),
                        "effect_status":effect_status,
                        "effect_state_indeterminate":effect_status=="EFFECT_STATE_INDETERMINATE",
                        "retry_allowed":bool(effect.get("retry_allowed",False)),"credentials_stored":False,
                        "browser_automation":False,"brokered_credential_available":True,
                        "raw_secret_observed":False,"latency":round(time.time()-started,6)}
            else:
                transport_result=effect.get("transport_result") or {}
                response_body=transport_result.get("body",b"")
                if isinstance(response_body,bytes): response_body=response_body.decode("utf-8",errors="replace")
                status_code=int(transport_result.get("status_code",200) or 200)
                data=json.loads(response_body)
                response_text = self._extract_output_text(data)
                success = bool(response_text.strip()) and 200 <= status_code < 300
                result = {
                    "primitive": PRIMITIVE,
                    "timestamp_utc": _utc(),
                    "success": success,
                    "provider": provider,
                    "adapter_mode": "openai_api_adapter",
                    "query_id": query_id,
                    "model": body.get("model"),
                    "status_code": status_code,
                    "response_text": response_text,
                    "response_length": len(response_text),
                    "response_hash": _hash(response_text, "RESP"),
                    "raw_response_id": data.get("id"),
                    "credentials_stored": False,
                    "browser_automation": False,
                    "brokered_credential_available": True,
                    "raw_secret_observed": False,
                    "latency": round(time.time() - started, 6),
                    "diagnostics": {
                        "endpoint": endpoint,
                        "raw_response_id": data.get("id"),
                        "output_item_count": len(data.get("output", []) or []),
                        "secret_policy": "brokered_credential_ref_resolved_inside_trusted_effector_TCB_only",
                    },
                }
        except Exception as exc:
            result = {
                "primitive": PRIMITIVE,
                "timestamp_utc": _utc(),
                "success": False,
                "provider": provider,
                "adapter_mode": "openai_api_adapter",
                "query_id": query_id,
                "response_text": "",
                "response_length": 0,
                "failure_reason": f"{type(exc).__name__}: {exc}",
                "credentials_stored": False,
                "browser_automation": False,
                "brokered_credential_available": True,
                "raw_secret_observed": False,
                "latency": round(time.time() - started, 6),
            }

        result_path = self.result_dir / f"{query_id}_openai_api_result.json"
        safe_result = dict(result)
        safe_result.pop("error_body", None)  # history keeps status; avoids noisy provider diagnostics in result files.
        result_path.write_text(json.dumps(safe_result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        result["record_path"] = str(result_path)
        self._append_jsonl(self.history_path, result, fs_context=fs_context)
        return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F9-R5 real ChatGPT autonomous API adapter")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--prompt-file", default="")
    parser.add_argument("--query-id", default="")
    parser.add_argument("--model", default="")
    args = parser.parse_args()
    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    payload: Dict[str, Any] = {"prompt": prompt, "query_id": args.query_id or None}
    if args.model:
        payload["model"] = args.model
    print(json.dumps(RealChatGPTAutonomousAPIAdapter().step(payload), ensure_ascii=False, indent=2, sort_keys=True))
