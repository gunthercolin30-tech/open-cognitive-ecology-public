
"""Multi Day Strategy Scheduler"""

class MultiDayStrategyScheduler:
    PRIMITIVE_NAME = "MULTI_DAY_STRATEGY_SCHEDULER"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(self, orchestrator_output=None, planning_horizon_days=7):
        orchestrator_output = orchestrator_output or {}

        progress_score = orchestrator_output.get("progress_score", 0.0)
        recommended_action = orchestrator_output.get(
            "recommended_action",
            "Maintenir la trajectoire actuelle"
        )

        strategic_days = []
        for day in range(1, planning_horizon_days + 1):
            strategic_days.append({
                "day": day,
                "focus": recommended_action,
                "priority_score": round(max(0.1, progress_score), 4),
                "status": "scheduled",
            })

        return {
            "primitive": self.PRIMITIVE_NAME,
            "planning_horizon_days": planning_horizon_days,
            "strategic_schedule": strategic_days,
            "strategy_continuity_score": round(
                (progress_score + 1.0) / 2.0,
                4
            ),
            "long_horizon_ready": True,
        }

if __name__ == "__main__":
    engine = MultiDayStrategyScheduler(user_name="Colin")
    print(engine.step(
        orchestrator_output={
            "progress_score": 0.4,
            "recommended_action": "Maintenir la trajectoire actuelle"
        },
        planning_horizon_days=7
    ))
