
PRIMITIVE = "thirty_day_distributed_monitoring"

class ThirtyDayDistributedMonitoring:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        monitoring_days_completed=0,
        average_longitudinal_stability=0.95,
        average_drift_index=0.05,
        cumulative_regression_events=0,
    ):

        completion_ratio = self._bounded(
            monitoring_days_completed / 30.0
        )

        continuity = self._bounded(
            (
                average_longitudinal_stability
                + (1.0 - average_drift_index)
            ) / 2.0
        )

        regression_penalty = min(
            1.0,
            cumulative_regression_events * 0.08
        )

        drift_penalty = self._bounded(
            average_drift_index * 1.5
        )

        monitoring_index = self._bounded(
            (
                completion_ratio * 0.30
                + continuity * 0.40
                + (1.0 - regression_penalty) * 0.15
                + (1.0 - drift_penalty) * 0.15
            )
        )

        certification_ready = (
            monitoring_days_completed >= 30
            and average_longitudinal_stability >= 0.90
            and average_drift_index <= 0.10
            and cumulative_regression_events == 0
        )

        return {
            "success": True,
            "monitoring_days_completed": monitoring_days_completed,
            "monitoring_completion_ratio": round(completion_ratio,4),
            "average_longitudinal_stability": round(average_longitudinal_stability,4),
            "average_drift_index": round(average_drift_index,4),
            "cumulative_regression_events": cumulative_regression_events,
            "distributed_monitoring_continuity": round(continuity,4),
            "regression_penalty": round(regression_penalty,4),
            "drift_penalty": round(drift_penalty,4),
            "thirty_day_monitoring_index": round(monitoring_index,4),
            "certification_ready": certification_ready,
        }
