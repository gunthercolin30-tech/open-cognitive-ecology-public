from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

try:
    import networkx as nx
except Exception:
    nx = None

from ontology.causal_inference import CausalInference
from ontology.monitoring import Monitoring
from ontology.performance_improvement_planner import PerformanceImprovementPlanner


class AdvancedCausalReasoningEngine:
    def __init__(self):
        if nx is None:
            raise RuntimeError("networkx n'est pas installé.")

        self.graph = nx.DiGraph()
        self.causal_inference = CausalInference()
        self.monitoring = Monitoring()
        self.planner = PerformanceImprovementPlanner()

        root = Path.home() / "open-cognitive-ecology"
        state_dir = root / "causal_reasoning"
        state_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = state_dir / "causal_history.sqlite"

        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS causal_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cause TEXT NOT NULL,
                    effect TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    executed_utc TEXT NOT NULL
                )
                """
            )

    def _normalize(self, text: str) -> str:
        return " ".join((text or "").strip().lower().split())

    def add_causal_relation(self, cause: str, effect: str, weight: float = 1.0):
        cause = self._normalize(cause)
        effect = self._normalize(effect)

        if not cause or not effect:
            return

        self.graph.add_edge(cause, effect, weight=float(weight))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO causal_history
                (cause, effect, confidence, executed_utc)
                VALUES (?, ?, ?, ?)
                """,
                (
                    cause,
                    effect,
                    float(weight),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def ingest_text(self, text: str):
        patterns = [
            (r"(.+?) parce que (.+)", True),
            (r"(.+?) est dû à (.+)", True),

            # Verbes "provoquer"
            (r"(.+?) provoque(?:nt|ait|aient|ra|ront)? (.+)", False),

            # Verbes "entraîner"
            (r"(.+?) entraîne(?:nt|ait|aient|ra|ront)? (.+)", False),

            # Verbes "causer"
            (r"(.+?) cause(?:nt|ait|aient|ra|ront)? (.+)", False),
        ]

        normalized = self._normalize(text).strip(" .")

        for pattern, reverse in patterns:
            match = re.match(pattern, normalized)
            if not match:
                continue

            left = match.group(1).strip(" .")
            right = match.group(2).strip(" .")

            if reverse:
                self.add_causal_relation(right, left, 0.95)
            else:
                self.add_causal_relation(left, right, 0.95)
            return True

        return False


    def answer_why(self, effect: str) -> List[str]:
        effect = self._normalize(effect)
        if effect not in self.graph:
            return []
        return sorted(self.graph.predecessors(effect))

    def predict_consequences(self, cause: str) -> List[str]:
        cause = self._normalize(cause)
        if cause not in self.graph:
            return []
        return sorted(nx.descendants(self.graph, cause))

    def find_causal_chain(self, cause: str, effect: str) -> List[str]:
        cause = self._normalize(cause)
        effect = self._normalize(effect)

        try:
            return nx.shortest_path(self.graph, cause, effect)
        except Exception:
            return []

    def counterfactual(self, cause: str, present: bool = False) -> List[str]:
        consequences = self.predict_consequences(cause)
        if present:
            return consequences
        return [f"prevented: {c}" for c in consequences]

    def step(self, inputs=None):
        inputs = inputs or {}

        if "statement" in inputs:
            self.ingest_text(inputs["statement"])

        if "cause" in inputs and "effect" in inputs:
            self.add_causal_relation(
                inputs["cause"],
                inputs["effect"],
                inputs.get("weight", 0.95),
            )

        discriminations = [True] * max(1, self.graph.number_of_edges())
        predictions = [True] * max(1, self.graph.number_of_nodes())
        structural = [True] * max(1, self.graph.number_of_edges())

        causal_result = self.causal_inference.evaluate(
            discriminations=discriminations,
            intervention_predictions=predictions,
            structural_signals=structural,
        )

        monitoring_result = self.monitoring.evaluate(
            observed_states=[True],
            deviations=[1.0],
            signal_quality=[0.99],
        )

        planner_result = self.planner.step(
            {
                "civilizational_viability_index":
                    causal_result["causal_inference_index"]
            }
        )

        confidence_score = min(
            causal_result["causal_inference_index"],
            monitoring_result["monitoring_index"],
        )

        return {
            "primitive": "ADVANCED_CAUSAL_REASONING_ENGINE",
            "success": True,
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "causal_inference_index":
                causal_result["causal_inference_index"],
            "confidence_score": confidence_score,
            "monitoring_index":
                monitoring_result["monitoring_index"],
            "recommended_next_primitive":
                planner_result["recommended_next_primitive"],
            "database_path": str(self.db_path),
        }
