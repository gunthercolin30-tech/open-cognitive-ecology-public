"""
complex_query_resolution_engine.py

Decomposes complex questions into structured subqueries and synthesizes
a coordinated resolution plan.
Extended with orchestration recommendations and resolution history.
"""

from math import sqrt


class ComplexQueryResolutionEngine:
    """Hierarchical decomposition and synthesis of complex queries."""

    def __init__(self):
        self.query_counter = 0
        self.resolution_history = []

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _extract_subqueries(query):
        separators = [" and ", " et ", " then ", " puis ", "?", ".", ";"]
        parts = [query]
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = new_parts
        return [p.strip() for p in parts if p.strip()]

    def _assign_module(self, subquery):
        text = subquery.lower()
        if "né" in text or "née" in text or "habite" in text:
            return "GENERAL_SEMANTIC_MEMORY_UNIFIED"
        if "param" in text:
            return "SELF_PARAMETER_OPTIMIZATION_ENGINE"
        if "performance" in text:
            return "PERFORMANCE_IMPROVEMENT_PLANNER"
        return "generic_reasoning"

    def step(self, inputs):
        self.query_counter += 1

        query = inputs.get("query", "")
        if not query:
            query = "analyze the current situation and propose next actions"

        subqueries = self._extract_subqueries(query)
        if not subqueries:
            subqueries = [query]

        complexity_score = self._clamp(len(subqueries) / 10.0)
        coordination_load = self._clamp(sqrt(len(subqueries)) / 5.0)
        synthesis_confidence = self._clamp(1.0 - complexity_score * 0.2)

        resolution_plan = [
            {
                "step": index + 1,
                "subquery": subquery,
                "assigned_module": self._assign_module(subquery),
            }
            for index, subquery in enumerate(subqueries)
        ]

        integrated_response_outline = " | ".join(subqueries)

        orchestration_recommendation = (
            "EXECUTE_MULTI_MODULE_COORDINATION"
            if len(subqueries) > 1
            else "EXECUTE_SINGLE_MODULE"
        )

        current_cvi = self._clamp(
            inputs.get("civilizational_viability_index", 0.9573)
        )
        civilizational_viability_projection = self._clamp(
            current_cvi + synthesis_confidence * 0.01
        )

        result = {
            "primitive": "COMPLEX_QUERY_RESOLUTION_ENGINE",
            "query_id": f"CQRE-{self.query_counter:04d}",
            "original_query": query,
            "subqueries": subqueries,
            "subquery_count": len(subqueries),
            "complexity_score": complexity_score,
            "coordination_load": coordination_load,
            "resolution_plan": resolution_plan,
            "integrated_response_outline": integrated_response_outline,
            "synthesis_confidence": synthesis_confidence,
            "orchestration_recommendation":
                orchestration_recommendation,
            "civilizational_viability_projection":
                civilizational_viability_projection,
        }

        self.resolution_history.append(
            {
                "query_id": result["query_id"],
                "subquery_count": len(subqueries),
                "complexity_score": complexity_score,
            }
        )

        result["resolution_history_length"] = len(
            self.resolution_history
        )

        return result
