
from datetime import datetime


class AlertingAndNotificationSystem:
    """
    Monitors critical runtime metrics and emits alert records when thresholds are violated.
    """

    def __init__(self):
        self.thresholds = {
            "global_viability_score": 0.90,
            "civilizational_autonomy_score": 0.90,
            "executive_coherence_score": 0.90,
            "consciousness_readiness_index": 0.90,
        }

    def evaluate(self, metrics):
        alerts = []
        for key, threshold in self.thresholds.items():
            value = metrics.get(key)
            if value is not None and value < threshold:
                alerts.append({
                    "metric": key,
                    "value": value,
                    "threshold": threshold,
                    "severity": "warning",
                })
        return alerts

    def step(self, metrics=None):
        if metrics is None:
            metrics = {
                "global_viability_score": 0.92457,
                "civilizational_autonomy_score": 0.9367,
                "executive_coherence_score": 0.933675,
                "consciousness_readiness_index": 0.93,
            }

        alerts = self.evaluate(metrics)

        return {
            "primitive": "ALERTING_AND_NOTIFICATION_SYSTEM",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "thresholds": dict(self.thresholds),
            "metrics": dict(metrics),
            "alerts": alerts,
            "alert_count": len(alerts),
            "system_status": "nominal" if not alerts else "warning",
        }
