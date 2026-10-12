from ontology.multi_rf_registry import MultiRFRegistry


def build_context():
    registry = MultiRFRegistry().step(
        inputs={"rf_records": [
            {"rf_id": "RF-A"}, {"rf_id": "RF-B"}, {"rf_id": "RF-C"},
        ]},
        persist=False,
    )
    base = {
        "memory_record_id": "MEM-FOUNDATION",
        "memory_namespace": "civilization",
        "memory_scope": "distributed",
        "origin_rf_id": "RF-A",
        "origin_lineage_id": "LINEAGE-1",
        "writer_id": "RF-A",
        "replica_ids": ["RF-A", "RF-B", "RF-C"],
        "acknowledged_replica_ids": ["RF-A", "RF-B", "RF-C"],
        "provenance_chain": [{"source": "AW8-SYNTHETIC", "actor": "RF-A"}],
        "transmission_chain": [{"from": "GEN-1", "to": "GEN-2"}],
        "retention_policy": {"mode": "governed"},
        "forgetting_policy": {"mode": "governed", "authorized": False},
        "availability_score": 1.0,
        "loss_tolerance_score": 0.67,
        "provenance_coverage": 1.0,
        "lineage_preservation_score": 1.0,
        "future_openness_preservation_score": 0.95,
        "created_at_utc": "2026-07-01T00:00:00Z",
        "updated_at_utc": "2026-07-12T00:00:00Z",
    }
    v1 = dict(base, version_id="MEM-FOUNDATION-V1", parent_version_ids=[], content={"axiom": "non-closure", "generation": 1})
    v2 = dict(base, version_id="MEM-FOUNDATION-V2", parent_version_ids=["MEM-FOUNDATION-V1"], content={"axiom": "non-closure", "generation": 2})
    return {"multi_rf_registry": registry, "memory_records": [v1, v2]}
