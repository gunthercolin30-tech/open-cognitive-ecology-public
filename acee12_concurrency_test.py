from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_architecture_genealogy import AceeArchitectureGenealogy

def base(aid="ARCH-A", parent=None, generation=0, rollback="not_rolled_back"):
    return {
        "architecture_id": aid,
        "architecture": {"architecture_id": aid, "modules": ["m1", "m2"], "parameters": {"x": 1}},
        "parent_architecture_id": parent,
        "generation_id": generation,
        "mutation_id": "MUT-1" if parent else None,
        "selection_decision": {"selection_id": "SEL-1", "decision": "accept"},
        "causal_analysis": {"analysis_id": "CAUSAL-1"},
        "impact_evaluation": {"evaluation_id": "IMPACT-1"},
        "rollback_status": rollback,
        "continuity_evidence": {"lineage_integrity": 0.91},
        "diversity_evidence": {"lineage_diversity_score": 0.82},
        "inheritance_evidence": {"inheritance_fidelity": 0.93},
        "timestamp_utc": "2026-07-13T20:00:00Z",
    }

from concurrent.futures import ThreadPoolExecutor
import json
with TemporaryDirectory() as tmp:
    root=Path(tmp); g=AceeArchitectureGenealogy(root=root); g.step(base(),persist=True)
    def work(i): return AceeArchitectureGenealogy(root=root).step(base(f"ARCH-{i}","ARCH-A",1),persist=True)
    with ThreadPoolExecutor(max_workers=8) as ex: results=list(ex.map(work,range(20)))
    assert all(r["persisted"] for r in results)
    lines=(root/"acee_runtime/ACEE12_acee_architecture_genealogy/genealogy_history.jsonl").read_text().splitlines()
    assert len(lines)==21 and all(json.loads(x) for x in lines)
print("ACEE12_CONCURRENCY_OK")
