from __future__ import annotations

import sys
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology import occ_normative_ir as nir


def sm(tag="A"):
    return {
        "source_id": "SRC." + tag,
        "source_path": "normative/occ1a/example.yaml",
        "source_field": "norms[0]",
        "source_sha256": "a" * 64,
    }


def node(node_id, node_type, **extra):
    out = {
        "node_id": node_id,
        "node_type": node_type,
        "source_map": sm(node_id),
        "formalization_level": "F1",
    }
    out.update(extra)
    return out


def run():
    contract = nir.validate_foundation_contract()
    assert contract["status"] == nir.PASS
    assert contract["reason"] == "OCC1B_NIR_FOUNDATION_OK"

    n1 = node("N1", "NormNode")
    n2 = node("C1", "ConditionNode", condition_state="UNKNOWN")
    graph = {
        "nodes": [n1, n2],
        "edges": [{"source": "N1", "target": "C1", "edge_type": "REQUIRES"}],
        "metadata": {"evaluation_domain": "STATIC"},
        "source_map": {"package": "OCC1A"},
    }
    good = nir.validate_graph(graph)
    assert good["status"] == nir.PASS

    graph2 = {"source_map": {"package": "OCC1A"}, "metadata": {"evaluation_domain": "STATIC"},
              "edges": deepcopy(graph["edges"]), "nodes": deepcopy(graph["nodes"])}
    assert nir.canonical_sha256(graph) == nir.canonical_sha256(graph2)

    bad = deepcopy(n1); bad["node_type"] = "InventedNode"
    assert nir.validate_node(bad)["reason"] == "UNKNOWN_NODE_TYPE"

    orphan = deepcopy(n1); orphan.pop("source_map")
    assert nir.validate_node(orphan)["reason"] == "ORPHAN_NORMATIVE_NODE"

    unknown = deepcopy(n2)
    assert nir.validate_node(unknown)["status"] == nir.PASS
    assert unknown["condition_state"] == "UNKNOWN"

    scope = node("S1", "ScopeNode", dimensions={"subject": "UNKNOWN", "geographic": "GLOBAL"})
    assert nir.validate_node(scope)["reason"] == "IMPLICIT_GLOBAL_SCOPE_FORBIDDEN"

    evidence = node("E1", "EvidenceNode", grants_authority=True)
    assert nir.validate_node(evidence)["reason"] == "EVIDENCE_MUST_NOT_GRANT_AUTHORITY"

    conflict = node("X1", "ConflictNode", arbitrates_conflict=True)
    assert nir.validate_node(conflict)["reason"] == "NIR_CONFLICT_NODE_MUST_NOT_ARBITRATE"

    payload = deepcopy(n1); payload["code"] = "print('x')"
    assert nir.validate_node(payload)["reason"] == "HIDDEN_EXECUTABLE_PAYLOAD"

    broken_edge = {"source": "N1", "target": "MISSING", "edge_type": "REQUIRES"}
    assert nir.validate_edge(broken_edge, ["N1"])["reason"] == "BROKEN_EDGE_REFERENCE"

    unknown_edge = {"source": "N1", "target": "C1", "edge_type": "INVENTS_AUTHORITY"}
    assert nir.validate_edge(unknown_edge, ["N1", "C1"])["reason"] == "UNKNOWN_EDGE_TYPE"

    expr = {"operator": "ALL_OF", "operands": ["N1", {"operator": "NONE_OF", "operands": ["C1"]}]}
    assert nir.validate_constraint_expression(expr)["status"] == nir.PASS

    assert nir.BOUNDARIES["authority_activated"] is False
    assert nir.BOUNDARIES["execution_performed"] is False
    assert nir.BOUNDARIES["occ1c_opened"] is False
    assert nir.BOUNDARIES["p160_opened"] is False
    assert nir.BOUNDARIES["functional_conclusion_only"] is True
    assert nir.BOUNDARIES["phenomenology_undetermined"] is True

    print("P159_OCC1B_NIR_FOUNDATION_V1_FUNCTIONAL_OK")
    print("P159_OCC1B_NIR_FOUNDATION_V1_DETERMINISM_OK")
    print("P159_OCC1B_NIR_FOUNDATION_V1_DEGRADATION_OK")
    print("P159_OCC1B_NIR_FOUNDATION_V1_STAGE_BOUNDARY_OK")
    print("P159_OCC1B_NIR_FOUNDATION_V1_TEST_OK")


if __name__ == "__main__":
    run()
