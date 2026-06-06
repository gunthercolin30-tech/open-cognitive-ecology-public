
"""
Personalized Response Synthesis
"""

class PersonalizedResponseSynthesis:
    PRIMITIVE_NAME = "PERSONALIZED_RESPONSE_SYNTHESIS"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        user_goal="",
        dialogue_memory=None,
        adaptive_profile=None,
        proactive_recommendations=None,
        long_term_strategy=None,
        governance_metrics=None,
    ):
        dialogue_memory = dialogue_memory or {}
        adaptive_profile = adaptive_profile or {}
        proactive_recommendations = proactive_recommendations or []
        long_term_strategy = long_term_strategy or {}
        governance_metrics = governance_metrics or {}

        recent_topics = dialogue_memory.get("recent_topics", [])
        next_milestone = long_term_strategy.get(
            "next_milestone",
            "contextual_goal_decomposition"
        )

        context_summary = (
            f"Goal={user_goal}; "
            f"RecentTopics={recent_topics}; "
            f"Language={adaptive_profile.get('preferred_language', 'fr')}"
        )

        personalized_response = (
            f"{self.user_name}, votre objectif actuel est '{user_goal}'. "
            f"Les sujets récents incluent {recent_topics}. "
            f"Les recommandations prioritaires sont "
            f"{proactive_recommendations}. "
            f"La prochaine étape stratégique recommandée est "
            f"'{next_milestone}'."
        )

        return {
            "primitive": self.PRIMITIVE_NAME,
            "user_goal": user_goal,
            "context_summary": context_summary,
            "action_priorities": proactive_recommendations,
            "recommended_next_milestone": next_milestone,
            "governance_status": governance_metrics,
            "personalized_response": personalized_response,
            "response_quality_score": 0.95,
        }


if __name__ == "__main__":
    engine = PersonalizedResponseSynthesis(user_name="Colin")
    print(engine.step(
        user_goal="Finaliser la théorie des intelligences sous contraintes"
    ))
