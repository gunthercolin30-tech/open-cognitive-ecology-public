"""
Internet Controlled Gateway
"""

PRIMITIVE = "internet_controlled_gateway"

DEPENDENCIES = [
    "world_model",
    "uncertainty_awareness",
    "evaluation",
    "monitoring",
    "epistemic_viability",
]


class InternetControlledGateway:
    def __init__(self, allowed_domains=None, max_queries=10):
        self.allowed_domains = list(allowed_domains or [])
        self.max_queries = int(max_queries)
        self.query_count = 0
        self.access_log = []

    def is_domain_allowed(self, domain):
        if not self.allowed_domains:
            return True
        return domain in self.allowed_domains

    def authorize(self, domain):
        if self.query_count >= self.max_queries:
            return False
        return self.is_domain_allowed(domain)

    def register_query(self, domain, query):
        if not self.authorize(domain):
            return {
                "authorized": False,
                "reason": "access_denied",
                "domain": domain,
                "query": query,
            }

        self.query_count += 1
        event = {
            "authorized": True,
            "domain": domain,
            "query": query,
            "query_index": self.query_count,
            "remaining_budget": self.max_queries - self.query_count,
        }
        self.access_log.append(event)
        return event

    def trust_score(self):
        if self.max_queries <= 0:
            return 0.0
        return max(0.0, 1.0 - self.query_count / self.max_queries)

    def diagnostics(self):
        return {
            "primitive": PRIMITIVE,
            "query_count": self.query_count,
            "max_queries": self.max_queries,
            "allowed_domains": list(self.allowed_domains),
            "trust_score": self.trust_score(),
            "events_logged": len(self.access_log),
        }
