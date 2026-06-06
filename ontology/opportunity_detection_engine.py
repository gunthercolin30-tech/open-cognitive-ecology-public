
"""Opportunity Detection Engine"""

class OpportunityDetectionEngine:
    PRIMITIVE_NAME = "OPPORTUNITY_DETECTION_ENGINE"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(self, user_goal="", dialogue_memory=None, environmental_signals=None):
        dialogue_memory = dialogue_memory or {}
        environmental_signals = environmental_signals or []

        recent_topics = dialogue_memory.get("recent_topics", [])
        opportunities = []

        if user_goal:
            opportunities.append({
                "type": "strategic",
                "title": f"Accélérer l'objectif: {user_goal}",
                "priority_score": 0.96,
            })

        for topic in recent_topics[:3]:
            opportunities.append({
                "type": "scientific",
                "title": f"Explorer davantage: {topic}",
                "priority_score": 0.92,
            })

        for signal in environmental_signals[:3]:
            opportunities.append({
                "type": "environmental",
                "title": f"Exploiter le signal: {signal}",
                "priority_score": 0.90,
            })

        return {
            "primitive": self.PRIMITIVE_NAME,
            "opportunities": opportunities,
            "opportunity_count": len(opportunities),
            "top_opportunity": opportunities[0]["title"] if opportunities else None,
            "detection_score": 0.95 if opportunities else 0.50,
            "opportunity_detection_ready": True,
        }

if __name__ == "__main__":
    engine = OpportunityDetectionEngine(user_name="Colin")
    print(engine.step(
        user_goal="Finaliser la théorie des intelligences sous contraintes",
        dialogue_memory={"recent_topics": ["constraint_fields", "non_closure"]},
        environmental_signals=["Nouvelle collaboration", "Nouveau DOI"],
    ))
