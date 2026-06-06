
"""
heterogeneous_node_coordination.py

Coordination distribuée hétérogène multi-nœuds.
"""

from dataclasses import dataclass, field
from statistics import mean


@dataclass
class HeterogeneousNodeCoordination:

    history: list = field(default_factory=list)

    def evaluate_node_heterogeneity(self, nodes):

        if not nodes:
            return {
                "success": False,
                "reason": "no_nodes",
            }

        cpu_values = [n.get("cpu", 0.0) for n in nodes]
        latency_values = [n.get("latency", 1.0) for n in nodes]

        cpu_mean = mean(cpu_values)
        latency_mean = mean(latency_values)

        cpu_variation = max(cpu_values) - min(cpu_values)
        latency_variation = (
            max(latency_values)
            - min(latency_values)
        )

        heterogeneity_index = round(
            (
                cpu_variation
                + latency_variation
            ) / 2.0,
            4,
        )

        coordination_index = round(
            max(
                0.0,
                min(
                    1.0,
                    (
                        cpu_mean
                        + (1.0 - latency_mean)
                    ) / 2.0,
                ),
            ),
            4,
        )

        result = {
            "success": True,
            "heterogeneity_detected":
                heterogeneity_index > 0.1,
            "heterogeneity_index":
                heterogeneity_index,
            "heterogeneous_coordination_index":
                coordination_index,
            "active_nodes": len(nodes),
        }

        self.history.append(result)

        return result

    def step(self):

        default_nodes = [
            {"cpu": 0.95, "latency": 0.10},
            {"cpu": 0.60, "latency": 0.40},
            {"cpu": 0.80, "latency": 0.20},
        ]

        return self.evaluate_node_heterogeneity(
            default_nodes
        )


ENGINE = HeterogeneousNodeCoordination()
