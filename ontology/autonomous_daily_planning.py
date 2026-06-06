
"""Autonomous Daily Planning"""

class AutonomousDailyPlanning:
    PRIMITIVE_NAME = "AUTONOMOUS_DAILY_PLANNING"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(self, decomposition):
        subgoals = decomposition.get("subgoals", [])
        tasks = []
        start_hour = 8
        for i, subgoal in enumerate(subgoals):
            duration = 90 if i == 0 else 60
            task = {
                "task_id": i + 1,
                "task": subgoal,
                "priority_rank": i + 1,
                "estimated_duration_minutes": duration,
                "recommended_start": f"{start_hour + i:02d}:00",
                "recommended_end": f"{start_hour + i + duration // 60:02d}:00",
                "status": "planned",
            }
            tasks.append(task)

        return {
            "primitive": self.PRIMITIVE_NAME,
            "tasks": tasks,
            "total_tasks": len(tasks),
            "daily_plan_ready": True,
            "execution_score": 0.95,
        }

if __name__ == "__main__":
    from contextual_goal_decomposition import ContextualGoalDecomposition
    d = ContextualGoalDecomposition().step(
        "Finaliser la théorie, préparer la publication Zenodo et mettre à jour la documentation"
    )
    print(AutonomousDailyPlanning(user_name="Colin").step(d))
