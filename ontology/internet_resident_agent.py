
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class InternetResidentAgent:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "internet_resident_agent"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "internet_resident_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "cycles": 0,
            "knowledge_sources_visited": 0,
            "knowledge_items_acquired": 0,
        }

    def _save_state(self, state: dict) -> None:
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def step(self, inputs=None) -> dict:
        if inputs is None:
            inputs = {}

        state = self._load_state()
        state["cycles"] += 1

        connectivity_score = float(inputs.get("connectivity_score", 0.95))
        retrieval_success = float(inputs.get("retrieval_success", 0.94))
        knowledge_relevance = float(inputs.get("knowledge_relevance", 0.93))
        memory_integration = float(inputs.get("memory_integration", 0.95))
        policy_compliance = float(inputs.get("policy_compliance", 1.0))

        sources_visited = int(inputs.get("sources_visited", 5))
        items_acquired = int(inputs.get("items_acquired", 20))

        state["knowledge_sources_visited"] += max(0, sources_visited)
        state["knowledge_items_acquired"] += max(0, items_acquired)
        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        internet_residency_index = max(
            0.0,
            min(
                1.0,
                (
                    connectivity_score
                    + retrieval_success
                    + knowledge_relevance
                    + memory_integration
                    + policy_compliance
                ) / 5.0,
            ),
        )

        operational = internet_residency_index >= 0.90

        self._save_state(state)

        return {
            "primitive": "INTERNET_RESIDENT_AGENT",
            "cycles": state["cycles"],
            "knowledge_sources_visited": state["knowledge_sources_visited"],
            "knowledge_items_acquired": state["knowledge_items_acquired"],
            "connectivity_score": connectivity_score,
            "retrieval_success": retrieval_success,
            "knowledge_relevance": knowledge_relevance,
            "memory_integration": memory_integration,
            "policy_compliance": policy_compliance,
            "internet_residency_index": internet_residency_index,
            "operational": operational,
            "state_path": str(self.state_path),
        }
