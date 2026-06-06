
"""Project Execution Orchestrator"""

class ProjectExecutionOrchestrator:
    PRIMITIVE_NAME = "PROJECT_EXECUTION_ORCHESTRATOR"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        goal_decomposition=None,
        daily_plan=None,
        research_suggestions=None,
        self_assessment=None,
    ):
        goal_decomposition = goal_decomposition or {}
        daily_plan = daily_plan or {}
        research_suggestions = research_suggestions or {}
        self_assessment = self_assessment or {}

        subgoals = goal_decomposition.get("subgoals", [])
        tasks = daily_plan.get("tasks", [])
        suggestions = research_suggestions.get("research_suggestions", [])
        recommended_action = self_assessment.get(
            "recommended_action",
            "Maintenir la trajectoire actuelle"
        )

        progress_score = round(
            (
                min(len(subgoals), 10) / 10.0 +
                min(len(tasks), 10) / 10.0 +
                min(len(suggestions), 10) / 10.0 +
                (1.0 if self_assessment.get("self_regulation_ready") else 0.0)
            ) / 4.0,
            4
        )

        return {
            "primitive": self.PRIMITIVE_NAME,
            "project_status": "active",
            "subgoals_count": len(subgoals),
            "daily_tasks_count": len(tasks),
            "research_suggestions_count": len(suggestions),
            "recommended_action": recommended_action,
            "progress_score": progress_score,
            "orchestration_ready": True,
        }

if __name__ == "__main__":
    print(ProjectExecutionOrchestrator(user_name="Colin").step(
        goal_decomposition={"subgoals": ["A", "B", "C"]},
        daily_plan={"tasks": [{"task_id": 1}, {"task_id": 2}]},
        research_suggestions={"research_suggestions": [{"type": "hypothesis"}]},
        self_assessment={
            "recommended_action": "Maintenir la trajectoire actuelle",
            "self_regulation_ready": True
        },
    ))
