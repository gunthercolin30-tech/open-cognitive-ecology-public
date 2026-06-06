from __future__ import annotations

try:
    from rdflib import Graph, URIRef, Literal
except Exception:
    Graph = None
    URIRef = None
    Literal = None


class RDFSemanticMemoryBackend:
    """
    Backend RDF optionnel basé sur rdflib.
    Fonctionne uniquement si rdflib est installé.
    """

    def __init__(self):
        self.available = Graph is not None
        self.graph = Graph() if self.available else None

    def is_available(self):
        return self.available

    def store_triplet(self, subject, predicate, obj):
        if not self.available:
            return {
                "stored": False,
                "reason": "rdflib_not_installed",
            }

        s = URIRef(f"urn:subject:{subject}")
        p = URIRef(f"urn:predicate:{predicate}")
        o = Literal(obj)

        self.graph.add((s, p, o))

        return {
            "stored": True,
            "triple_count": len(self.graph),
        }

    def query_subject(self, subject):
        if not self.available:
            return {
                "available": False,
                "reason": "rdflib_not_installed",
            }

        s = URIRef(f"urn:subject:{subject}")
        results = []

        for subj, pred, obj in self.graph.triples((s, None, None)):
            results.append({
                "subject": subject,
                "predicate": str(pred).replace("urn:predicate:", ""),
                "object": str(obj),
            })

        return {
            "available": True,
            "results": results,
        }

    def step(self, inputs):
        action = inputs.get("action", "status")

        if action == "status":
            return {
                "primitive": "RDF_SEMANTIC_MEMORY_BACKEND",
                "available": self.available,
                "triple_count": len(self.graph) if self.available else 0,
            }

        if action == "store":
            result = self.store_triplet(
                inputs.get("subject", ""),
                inputs.get("predicate", ""),
                inputs.get("object", ""),
            )
            result["primitive"] = "RDF_SEMANTIC_MEMORY_BACKEND"
            return result

        if action == "query":
            result = self.query_subject(inputs.get("subject", ""))
            result["primitive"] = "RDF_SEMANTIC_MEMORY_BACKEND"
            return result

        return {
            "primitive": "RDF_SEMANTIC_MEMORY_BACKEND",
            "error": "unknown_action",
            "action": action,
        }
