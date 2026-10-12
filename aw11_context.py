from aw10_context import build_context as build_aw10_context
from ontology.ecology_dashboard import EcologyDashboard


def build_context():
    context = build_aw10_context()
    context["ecology_dashboard"] = EcologyDashboard().step(
        inputs=context,
        persist=False,
    )
    return context
