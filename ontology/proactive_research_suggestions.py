
"""Proactive Research Suggestions"""

class ProactiveResearchSuggestions:
    PRIMITIVE_NAME = "PROACTIVE_RESEARCH_SUGGESTIONS"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        user_goal="",
        dialogue_memory=None,
        governance_metrics=None,
    ):
        dialogue_memory = dialogue_memory or {}
        governance_metrics = governance_metrics or {}

        recent_topics = dialogue_memory.get("recent_topics", [])

        suggestions = [
            {
                "type": "hypothesis",
                "title": "Étendre la formalisation théorique",
                "priority_score": 0.98,
            },
            {
                "type": "publication",
                "title": "Préparer un nouveau manuscrit Zenodo",
                "priority_score": 0.96,
            },
            {
                "type": "experiment",
                "title": "Évaluer quantitativement la nouvelle primitive",
                "priority_score": 0.94,
            },
        ]

        return {
            "primitive": self.PRIMITIVE_NAME,
            "user_goal": user_goal,
            "recent_topics": recent_topics,
            "governance_status": governance_metrics,
            "research_suggestions": suggestions,
            "top_priority": suggestions[0]["title"],
            "research_readiness_score": 0.97,
        }

if __name__ == "__main__":
    engine = ProactiveResearchSuggestions(user_name="Colin")
    print(engine.step(
        user_goal="Finaliser la théorie des intelligences sous contraintes",
        dialogue_memory={"recent_topics": ["constraint_fields", "non_closure"]},
        governance_metrics={"global_viability_score": 0.92457},
    ))
