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

import multiprocessing as mp, json
def worker(args):
    root_path, i = args
    return AceeArchitectureGenealogy(root=Path(root_path)).step(base(f"ARCH-P{i}","ARCH-A",1),persist=True)["persisted"]
if __name__ == "__main__":
    mp.set_start_method("spawn",force=True)
    with TemporaryDirectory() as tmp:
        AceeArchitectureGenealogy(root=Path(tmp)).step(base(),persist=True)
        with mp.Pool(4) as pool: values=pool.map(worker,[(tmp, i) for i in range(12)])
        assert all(values)
        lines=(Path(tmp)/"acee_runtime/ACEE12_acee_architecture_genealogy/genealogy_history.jsonl").read_text().splitlines()
        assert len(lines)==13 and all(json.loads(x) for x in lines)
    print("ACEE12_MULTIPROCESS_PERSISTENCE_OK")
