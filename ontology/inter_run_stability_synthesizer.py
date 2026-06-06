
from statistics import mean, pstdev


class InterRunStabilitySynthesizer:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def _metric_stats(self, values):

        if not values:
            return {
                "mean": 0.0,
                "std_dev": 1.0,
            }

        if len(values) == 1:
            return {
                "mean": values[0],
                "std_dev": 0.0,
            }

        return {
            "mean": mean(values),
            "std_dev": pstdev(values),
        }

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        coherence_values = [
            float(r.get("trajectory_coherence", 0.0))
            for r in runs
        ]

        attractor_values = [
            float(r.get("attractor_stability_index", 0.0))
            for r in runs
        ]

        viability_values = [
            float(r.get("distributed_viability_index", 0.0))
            for r in runs
        ]

        resilience_values = [
            float(r.get("recovery_resilience_index", 0.0))
            for r in runs
        ]

        coherence_stats = self._metric_stats(
            coherence_values
        )

        attractor_stats = self._metric_stats(
            attractor_values
        )

        viability_stats = self._metric_stats(
            viability_values
        )

        resilience_stats = self._metric_stats(
            resilience_values
        )

        inter_run_stability_index = self._bounded(
            (
                coherence_stats["mean"]
                + attractor_stats["mean"]
                + viability_stats["mean"]
                + resilience_stats["mean"]
            ) / 4.0
        )

        variability_penalty = self._bounded(
            (
                coherence_stats["std_dev"]
                + attractor_stats["std_dev"]
                + viability_stats["std_dev"]
                + resilience_stats["std_dev"]
            ) / 4.0
        )

        attractor_persistence = self._bounded(
            attractor_stats["mean"]
            * (1.0 - variability_penalty)
        )

        distributed_ecological_coherence = self._bounded(
            coherence_stats["mean"]
            * viability_stats["mean"]
        )

        if inter_run_stability_index >= 0.90:
            stability_class = (
                "persistent_open_ecological_stability"
            )

        elif inter_run_stability_index >= 0.75:
            stability_class = (
                "functional_distributed_stability"
            )

        else:
            stability_class = (
                "unstable_ecological_distribution"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "inter_run_stability_index":
                round(inter_run_stability_index, 4),
            "attractor_persistence":
                round(attractor_persistence, 4),
            "distributed_ecological_coherence":
                round(
                    distributed_ecological_coherence,
                    4,
                ),
            "variability_penalty":
                round(variability_penalty, 4),
            "stability_class":
                stability_class,
        }
