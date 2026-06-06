from ontology.autonomous_web_navigation_engine import (
    AutonomousWebNavigationEngine,
)

PRIMITIVE = "autonomous_host_discovery_and_selection_orchestrator"

class AutonomousHostDiscoveryAndSelectionOrchestrator:

    DEFAULT_TARGETS = [
        "https://www.oracle.com/cloud/free/",
        "https://github.com/features/actions",
        "https://www.scaleway.com/",
        "https://www.hetzner.com/",
    ]

    def __init__(self):
        self.navigator = AutonomousWebNavigationEngine(max_pages=2)

    def _discover(self):
        candidates = []

        for url in self.DEFAULT_TARGETS:
            try:
                result = self.navigator.step({"url": url})

                if result.get("success"):
                    candidates.append({
                        "name": url,
                        "feasibility": 0.80,
                        "monthly_cost": 0,
                        "pages_visited": result.get("pages_visited", 0),
                    })
            except Exception:
                pass

        return candidates

    def step(self, state=None):
        state = state or {}

        discovered_hosts = state.get("discovered_hosts")

        autonomous_discovery_used = False

        if not discovered_hosts:
            discovered_hosts = self._discover()
            autonomous_discovery_used = True

        if not discovered_hosts:
            discovered_hosts = [{
                "name": "fallback_candidate",
                "feasibility": 0.50,
                "monthly_cost": 0,
            }]

        discovered_hosts.sort(
            key=lambda x: float(x.get("feasibility", 0.0)),
            reverse=True,
        )

        best = discovered_hosts[0]

        return {
            "primitive": PRIMITIVE,
            "candidate_host_count": len(discovered_hosts),
            "best_candidate": best["name"],
            "deployment_feasibility": best["feasibility"],
            "estimated_monthly_cost": best["monthly_cost"],
            "autonomous_discovery_used": autonomous_discovery_used,
            "selection_ready": best["feasibility"] >= 0.70,
        }