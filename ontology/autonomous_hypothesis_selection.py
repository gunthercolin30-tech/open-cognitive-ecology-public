
from datetime import datetime


class AutonomousHypothesisSelection:
    """
    Selects the most promising scientific hypothesis based on quantitative scores.
    """

    def score(self, hypothesis):
        novelty = float(hypothesis.get("novelty", 0.0))
        feasibility = float(hypothesis.get("feasibility", 0.0))
        expected_impact = float(hypothesis.get("expected_impact", 0.0))
        return 0.4 * novelty + 0.3 * feasibility + 0.3 * expected_impact

    def step(self, hypotheses=None):
        if hypotheses is None:
            hypotheses = [
                {
                    "id": "H1",
                    "title": "Constraint-field resonance",
                    "novelty": 0.95,
                    "feasibility": 0.90,
                    "expected_impact": 0.96,
                },
                {
                    "id": "H2",
                    "title": "Distributed reflective scaling",
                    "novelty": 0.91,
                    "feasibility": 0.94,
                    "expected_impact": 0.92,
                },
            ]

        scored = []
        for hypothesis in hypotheses:
            entry = dict(hypothesis)
            entry["selection_score"] = round(self.score(hypothesis), 6)
            scored.append(entry)

        ranked = sorted(scored, key=lambda x: x["selection_score"], reverse=True)
        selected = ranked[0] if ranked else None

        return {
            "primitive": "AUTONOMOUS_HYPOTHESIS_SELECTION",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "hypothesis_count": len(ranked),
            "ranked_hypotheses": ranked,
            "selected_hypothesis": selected,
            "selection_status": "completed" if selected else "no_candidates",
        }
