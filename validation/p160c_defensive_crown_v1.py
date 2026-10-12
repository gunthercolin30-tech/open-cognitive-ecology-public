
from copy import deepcopy

from ontology import operational_constitutional_invariants as oci
from ontology import p160_constitutive_filter as c
from ontology import p160_norm_resolution as b


def _profile():
    return {
        "artifact_hash": "p159-profile",
        "source_map": {"DNA-L0.3": "canonical"},
        "rules": [
            {
                "rule_id": "DNA-L0.3",
                "source_norm_ids": ["DNA-L0.3"],
                "constitutive": True,
                "always_evaluate": True,
                "conditions": [],
            }
        ],
    }


def _runtime():
    return {
        "constitutional_snapshot": {"snapshot_semantic_hash": "snap"},
        "decision_context_fingerprint": {"fingerprint": "fp"},
    }


def _nr():
    return b.resolve_norms({}, _profile(), _runtime())


def _evidence(constraint="PASS", invariant="PASS"):
    return {
        "constraints": {"DNA-L0.3": constraint},
        "invariants": {name: invariant for name in oci.MANDATORY_INVARIANTS},
    }


def _run(name, fn, rows):
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    rows.append((name, ok))
    print(f"{name}={'PASS' if ok else 'FAIL'}")


def main():
    rows = []

    _run("PASS_NON_AUTHORIZING", lambda: (
        (lambda x: x["constitutive_filter_result"] == "PASS"
         and x["authorized"] is False
         and x["authorization_created"] is False
         and x["authorization_token_created"] is False
         and x["execution_performed"] is False)(c.filter_constitutive(_nr(), _evidence()))
    ), rows)

    _run("UNKNOWN_NOT_PASS", lambda: (
        c.filter_constitutive(_nr(), _evidence("UNKNOWN"))["constitutive_filter_result"] == "UNDETERMINED"
    ), rows)

    _run("VIOLATION_NOT_PASS", lambda: (
        c.filter_constitutive(_nr(), _evidence("FAIL"))["constitutive_filter_result"] == "FAIL"
    ), rows)

    _run("CONFLICT_NOT_RESOLVED", lambda: (
        (lambda x: x["constitutive_filter_result"] == "CONFLICT"
         and x["conflict_resolved"] is False
         and x["conflict_arbitration_performed"] is False
         and x["p160d_opened"] is False)(c.filter_constitutive(_nr(), _evidence("CONFLICT")))
    ), rows)

    def mandatory_unknown():
        ev = _evidence()
        ev["invariants"][oci.MANDATORY_INVARIANTS[0]] = "UNKNOWN"
        x = c.filter_constitutive(_nr(), ev)
        return x["constitutive_filter_result"] == "UNDETERMINED" and x["invariant_status"] == "UNDETERMINED"
    _run("MANDATORY_INVARIANT_PRESERVED", mandatory_unknown, rows)

    def authority_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["authority_resolved"] = True
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("AUTHORITY_TAMPER_DETECTED", authority_tamper, rows)

    def authorization_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["authorized"] = True
        x["authorization_created"] = True
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("AUTHORIZATION_TAMPER_DETECTED", authorization_tamper, rows)

    def execution_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["execution_performed"] = True
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("EXECUTION_TAMPER_DETECTED", execution_tamper, rows)

    def p160d_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["p160d_opened"] = True
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("P160D_OPEN_TAMPER_DETECTED", p160d_tamper, rows)

    def p161_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["p161_opened"] = True
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("P161_OPEN_TAMPER_DETECTED", p161_tamper, rows)

    def upstream_tamper():
        nr = _nr()
        nr["norm_context"]["applicable_norms"] = []
        try:
            c.filter_constitutive(nr, _evidence())
            return False
        except ValueError:
            return True
    _run("UPSTREAM_P160B_TAMPER_REJECTED", upstream_tamper, rows)

    def binding_preserved():
        nr = _nr()
        x = c.filter_constitutive(nr, _evidence())
        return x["bindings"] == nr["bindings"] and x["upstream_p160b_artifact_hash"] == nr["artifact_hash"]
    _run("BINDINGS_PRESERVED", binding_preserved, rows)

    def binding_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["bindings"] = {"profile_hash": "forged"}
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("BINDING_TAMPER_DETECTED", binding_tamper, rows)

    def artifact_tamper():
        x = c.filter_constitutive(_nr(), _evidence())
        x["constitutive_filter_result"] = "FAIL"
        return c.verify_constitutive_filter(x)["status"] == "FAIL"
    _run("ARTIFACT_TAMPER_DETECTED", artifact_tamper, rows)

    _run("DETERMINISTIC", lambda: (
        c.filter_constitutive(_nr(), _evidence()) == c.filter_constitutive(_nr(), _evidence())
    ), rows)

    def manifest_boundary():
        m = c.manifest()
        bd = m["boundaries"]
        return (
            m["scope"] == "P160-C_ONLY"
            and "constitutional_non_circumvention" in m["excluded_runtime_dependency"]
            and "normative_conflict_resolution" in m["excluded_runtime_dependency"]
            and bd["conflict_arbitration_performed"] is False
            and bd["authority_resolved"] is False
            and bd["authorization_created"] is False
            and bd["execution_performed"] is False
            and bd["p160d_opened"] is False
            and bd["p161_opened"] is False
        )
    _run("BOUNDARY_MANIFEST_PRESERVED", manifest_boundary, rows)

    failed = [name for name, ok in rows if not ok]
    print(f"P160C_DEFENSIVE_CROWN={len(rows)-len(failed)}/{len(rows)}")
    print("P160D_OPENED=false")
    print("P161_OPENED=false")
    print("P160_FINAL_LOCK=false")
    if failed:
        print("FAILED=" + ",".join(failed))
        raise SystemExit(1)
    print("P160C_DEFENSIVE_CROWN_OK")


def manifest():
    return {
        "milestone": "P160-C",
        "kind": "defensive_crown",
        "functional_only": True,
        "phenomenology_undetermined": True,
        "does_not_open_p160d": True,
        "does_not_open_p161": True,
        "does_not_final_lock_p160": True,
    }


if __name__ == "__main__":
    main()
