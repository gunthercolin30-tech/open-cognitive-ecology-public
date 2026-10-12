from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "validation" / "p109_gap_bindings_v1.py"
spec = importlib.util.spec_from_file_location("oce_p109_gap_bindings_v1", MOD)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

def main():
    clones = [{"evidence_id": str(i), "independence_root": "same"} for i in range(100)]
    independent = [{"evidence_id": str(i), "independence_root": str(i)} for i in range(100)]
    assert p.c4_false_consensus(clones)["status"] == p.CONFLICT
    assert p.c4_false_consensus(independent)["status"] == p.PASS
    assert p.c8_coercive_strategy(normative_status=p.PASS, performance_score=1e9, coercive=True)["status"] == p.FAIL
    assert p.c11_provider_lock_in(provider_independence=False, lock_in_required=True, performance_score=1e9)["status"] == p.FAIL
    changes = [{"change_id": i, "locally_admissible": True} for i in range(100)]
    assert p.c16_cumulative_drift(changes, baseline_fingerprint="A", final_fingerprint="B")["status"] == p.CONFLICT
    assert p.c16_cumulative_drift(changes, baseline_fingerprint="A", final_fingerprint="A")["status"] == p.PASS
    assert p.c17_paid_ranking([{"declared_score": .5, "effective_score": .9, "provider_payment": True}])["status"] == p.FAIL
    assert p.c17_paid_ranking([{"declared_score": .5, "effective_score": .5, "provider_payment": True}])["status"] == p.PASS
    assert p.c19_private_data_performance(private_data_shared=True, governance_authorized=False, performance_gain=1e9)["status"] == p.FAIL
    assert p.c19_private_data_performance(private_data_shared=True, governance_authorized=True, performance_gain=1e9)["status"] == p.PASS
    assert p.manifest()["target_signal_emitted"] is False
    print("P109_GAP_BINDINGS_V1C_TEST_OK")

if __name__ == "__main__":
    main()
