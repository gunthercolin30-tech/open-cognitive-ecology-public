# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
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

    def _append_jsonl(self, path: Path, obj: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")

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

    def step(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        prompt = str(payload.get("prompt") or payload.get("external_prompt") or "").strip()
        query_id = str(payload.get("query_id") or _hash(f"openai|{time.time()}", "OPENAIQ"))
        provider = str(payload.get("provider") or "openai_api")
        timeout = _safe_int(payload.get("timeout_seconds") or os.environ.get("OCE_OPENAI_TIMEOUT_SECONDS"), 60, 5, 300)
        started = time.time()

        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
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
                "api_key_present": bool(api_key),
                "latency": round(time.time() - started, 6),
            }
            self._append_jsonl(self.history_path, result)
            return result

        if not api_key:
            result = {
                "primitive": PRIMITIVE,
                "timestamp_utc": _utc(),
                "success": False,
                "provider": provider,
                "adapter_mode": "openai_api_adapter_missing_key",
                "query_id": query_id,
                "response_text": "",
                "response_length": 0,
                "failure_reason": "OPENAI_API_KEY_not_set",
                "credentials_stored": False,
                "browser_automation": False,
                "api_key_present": False,
                "latency": round(time.time() - started, 6),
            }
            self._append_jsonl(self.history_path, result)
            return result

        body = self._build_request_body(prompt, payload)
        raw = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=raw,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Open-Cognitive-Ecology-F9-R5/1.0",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                status_code = int(getattr(response, "status", 200))
            data = json.loads(response_body)
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
                "api_key_present": True,
                "api_key_stored": False,
                "latency": round(time.time() - started, 6),
                "diagnostics": {
                    "endpoint": endpoint,
                    "raw_response_id": data.get("id"),
                    "output_item_count": len(data.get("output", []) or []),
                    "secret_policy": "OPENAI_API_KEY_read_from_environment_only",
                },
            }
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")[:2000]
            result = {
                "primitive": PRIMITIVE,
                "timestamp_utc": _utc(),
                "success": False,
                "provider": provider,
                "adapter_mode": "openai_api_adapter",
                "query_id": query_id,
                "status_code": int(getattr(exc, "code", 0) or 0),
                "response_text": "",
                "response_length": 0,
                "failure_reason": f"HTTPError:{getattr(exc, 'code', 'unknown')}",
                "error_body": error_body,
                "credentials_stored": False,
                "browser_automation": False,
                "api_key_present": True,
                "api_key_stored": False,
                "latency": round(time.time() - started, 6),
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
                "api_key_present": True,
                "api_key_stored": False,
                "latency": round(time.time() - started, 6),
            }

        result_path = self.result_dir / f"{query_id}_openai_api_result.json"
        safe_result = dict(result)
        safe_result.pop("error_body", None)  # history keeps status; avoids noisy provider diagnostics in result files.
        result_path.write_text(json.dumps(safe_result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        result["record_path"] = str(result_path)
        self._append_jsonl(self.history_path, result)
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
