"""Evolution Sandbox"""

PRIMITIVE = "evolution_sandbox"

DEPENDENCIES = [
    "self_parameter_optimization",
    "persistent_multi_scale_memory",
    "internet_controlled_gateway",
    "evaluation",
    "monitoring",
]


class EvolutionSandbox:
    def __init__(self):
        self.generations = []

    def register_generation(self, candidates):
        self.generations.append(list(candidates))

    def generation_count(self):
        return len(self.generations)

    def latest_generation(self):
        if not self.generations:
            return []
        return list(self.generations[-1])

    def diagnostics(self):
        latest = self.latest_generation()
        return {
            "primitive": PRIMITIVE,
            "generation_count": self.generation_count(),
            "latest_population_size": len(latest),
        }
