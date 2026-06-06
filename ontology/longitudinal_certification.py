
PRIMITIVE = "longitudinal_certification"

DEPENDENCIES = [
    "civilizational_longitudinal_stability_synthesizer",
    "longitudinal_drift_detection",
    "thirty_day_distributed_monitoring",
    "longitudinal_recovery_observer",
    "persistent_experimental_validation_network",
]

class LongitudinalCertification:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        civilizational_longitudinal_stability_index=0.95,
        civilizational_drift_index=0.05,
        thirty_day_monitoring_index=0.95,
        longitudinal_recovery_index=0.95,
        persistent_validation_index=0.95,
        founder_independence_index=0.9432,
    ):

        certification_score = (
            self._bounded(civilizational_longitudinal_stability_index) * 0.25 +
            self._bounded(1.0 - civilizational_drift_index) * 0.20 +
            self._bounded(thirty_day_monitoring_index) * 0.20 +
            self._bounded(longitudinal_recovery_index) * 0.15 +
            self._bounded(persistent_validation_index) * 0.10 +
            self._bounded(founder_independence_index) * 0.10
        )

        certified = (
            civilizational_longitudinal_stability_index >= 0.90 and
            civilizational_drift_index <= 0.10 and
            thirty_day_monitoring_index >= 0.90 and
            founder_independence_index >= 0.90
        )

        if certified and certification_score >= 0.90:
            certification_class = "certified_longitudinal_civilization"
        elif certification_score >= 0.75:
            certification_class = "provisionally_stable_civilization"
        else:
            certification_class = "longitudinal_certification_failed"

        return {
            "success": True,
            "certification_score": round(certification_score, 4),
            "certified": certified,
            "certification_class": certification_class,
            "founder_independence_index": round(founder_independence_index, 4),
            "longitudinal_stability_confirmed": certified,
        }
