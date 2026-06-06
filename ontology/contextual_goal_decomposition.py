
"""Contextual Goal Decomposition"""

class ContextualGoalDecomposition:
    PRIMITIVE_NAME = "CONTEXTUAL_GOAL_DECOMPOSITION"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def _extract_subgoals(self, goal):
        separators = [" et ", ",", ";", " puis ", " ensuite "]
        parts = [goal]
        for sep in separators:
            new_parts = []
            for p in parts:
                new_parts.extend([x.strip() for x in p.split(sep) if x.strip()])
            parts = new_parts
        if len(parts) == 1:
            return [
                f"Analyser: {goal}",
                f"Planifier: {goal}",
                f"Exécuter: {goal}",
            ]
        return parts

    def step(self, user_goal):
        subgoals = self._extract_subgoals(user_goal)
        priorities = [
            {"rank": i + 1, "subgoal": sg, "priority_score": round(1.0 - i * 0.1, 2)}
            for i, sg in enumerate(subgoals)
        ]
        dependencies = [
            {"subgoal": subgoals[i], "depends_on": subgoals[i - 1]}
            for i in range(1, len(subgoals))
        ]
        if len(subgoals) <= 3:
            time_horizon = "days"
        elif len(subgoals) <= 6:
            time_horizon = "weeks"
        else:
            time_horizon = "months"

        return {
            "primitive": self.PRIMITIVE_NAME,
            "user_goal": user_goal,
            "subgoals": subgoals,
            "priorities": priorities,
            "dependencies": dependencies,
            "recommended_time_horizon": time_horizon,
            "planning_ready": True,
        }

if __name__ == "__main__":
    engine = ContextualGoalDecomposition(user_name="Colin")
    print(engine.step(
        "Finaliser la théorie, préparer la publication Zenodo et mettre à jour la documentation"
    ))
