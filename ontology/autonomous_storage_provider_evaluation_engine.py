from __future__ import annotations


class AutonomousStorageProviderEvaluationEngine:
    DEFAULT_PROVIDERS = [
        {
            "name": "local_disk",
            "capacity_gb": 512,
            "monthly_cost_eur": 0.0,
            "security_score": 0.70,
            "api_compatibility": 1.0,
            "local_disk_usage": 1.0,
        },
        {
            "name": "nas",
            "capacity_gb": 4000,
            "monthly_cost_eur": 10.0,
            "security_score": 0.85,
            "api_compatibility": 0.80,
            "local_disk_usage": 0.10,
        },
        {
            "name": "cloud_object_storage",
            "capacity_gb": 100000,
            "monthly_cost_eur": 20.0,
            "security_score": 0.95,
            "api_compatibility": 1.0,
            "local_disk_usage": 0.01,
        },
        {
            "name": "distributed_storage",
            "capacity_gb": 1000000,
            "monthly_cost_eur": 30.0,
            "security_score": 0.90,
            "api_compatibility": 0.90,
            "local_disk_usage": 0.01,
        },
    ]

    def __init__(self):
        self.providers = list(self.DEFAULT_PROVIDERS)

    def evaluate_provider(self, provider):
        capacity_score = min(1.0, provider.get("capacity_gb", 0) / 10000.0)
        cost_score = max(0.0, 1.0 - provider.get("monthly_cost_eur", 0.0) / 50.0)
        security_score = float(provider.get("security_score", 0.0))
        api_score = float(provider.get("api_compatibility", 0.0))
        local_usage = float(provider.get("local_disk_usage", 1.0))
        local_disk_score = max(0.0, 1.0 - local_usage)

        composite = (
            0.25 * capacity_score
            + 0.20 * cost_score
            + 0.25 * security_score
            + 0.15 * api_score
            + 0.15 * local_disk_score
        )

        return {
            "provider": provider["name"],
            "composite_score": round(composite, 4),
            "capacity_score": round(capacity_score, 4),
            "cost_score": round(cost_score, 4),
            "security_score": round(security_score, 4),
            "api_score": round(api_score, 4),
            "local_disk_score": round(local_disk_score, 4),
        }

    def rank_providers(self):
        ranked = [self.evaluate_provider(p) for p in self.providers]
        ranked.sort(key=lambda x: x["composite_score"], reverse=True)
        return ranked

    def recommend_provider(self):
        ranked = self.rank_providers()
        return ranked[0] if ranked else None

    def step(self, inputs):
        return {
            "primitive": "AUTONOMOUS_STORAGE_PROVIDER_EVALUATION_ENGINE",
            "provider_count": len(self.providers),
            "recommendation": self.recommend_provider(),
            "ranked_providers": self.rank_providers(),
        }
