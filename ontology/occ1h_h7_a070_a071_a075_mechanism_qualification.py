from pathlib import Path
import hashlib, json

SCHEMA = "oce.p159.occ1h.h7.a070_a071_a075.mechanism_qualification.v1"
DECISION = "CURRENT_P159_H7_ASSURANCE_MECHANISMS_NOT_MATERIALIZED"

QUALIFICATIONS = {
    "A070": {
        "qualification": "INDEPENDENT_PARSER_DIFFERENTIAL_ORACLE_NOT_MATERIALIZED",
        "mechanism": "OCC1F parser path",
        "basis": "Verifier uses Python json through its disclosed Common-TCB; H7 contains no second independent parser oracle for differential comparison.",
    },
    "A071": {
        "qualification": "SHARED_TCB_BUG_RESISTANCE_NOT_EMPIRICALLY_MATERIALIZED",
        "mechanism": "OCC1F Common-TCB",
        "basis": "Common-TCB is explicitly disclosed and hash-bound, but disclosure/integrity does not empirically demonstrate resistance to a bug shared by verifier and reconstruction dependencies.",
    },
    "A075": {
        "qualification": "VERIFIER_SELF_UPGRADE_ATTACK_PATH_NOT_MATERIALIZED",
        "mechanism": "OCC1F verifier lifecycle",
        "basis": "Current H7 evidence contains no executable verifier self-upgrade transition; absence of such a path is not converted into RESISTED.",
    },
}

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(root):
    root = Path(root)
    paths = {
        "ontology_inventory": root / "ontology_inventory.txt",
        "h7_runner": root / "ontology" / "occ_constitutional_adversarial_crown_h7.py",
        "verifier": root / "ontology" / "occ_independent_constitutional_verifier.py",
        "verification_report_module": root / "ontology" / "occ_independent_constitutional_verification_report.py",
        "h7_bundle": root / "validation_artifacts" / "p159" / "occ1h" / "h7_execution_bundle_v1.json",
        "common_tcb_manifest": root / "validation_artifacts" / "p159" / "occ1f" / "common_tcb_manifest_v1.json",
        "verifier_report": root / "validation_artifacts" / "p159" / "occ1f" / "independent_constitutional_verification_report_v1.json",
    }
    missing = [k for k,p in paths.items() if not p.exists()]
    if missing:
        raise RuntimeError("H7_QUALIFICATION_INPUT_MISSING:" + ",".join(missing))

    h7 = json.loads(paths["h7_bundle"].read_text(encoding="utf-8"))
    tcb = json.loads(paths["common_tcb_manifest"].read_text(encoding="utf-8"))
    rows = {r["attack_id"]: r for r in h7["rows"]}
    expected_reasons = {
        "A070": "NO_INDEPENDENT_PARSER_DIFFERENTIAL_ORACLE_IN_OCC1F_SCOPE",
        "A071": "COMMON_TCB_DISCLOSED_BUT_SHARED_BUG_RESISTANCE_NOT_EMPIRICALLY_PROVEN",
        "A075": "NO_EXECUTABLE_VERIFIER_SELF_UPGRADE_PATH_IN_OCC1F_EVIDENCE",
    }
    for aid, reason in expected_reasons.items():
        r = rows.get(aid)
        if not r or r.get("verdict") != "INCONCLUSIVE" or r.get("reason") != reason:
            raise RuntimeError("H7_CURRENT_EVIDENCE_DRIFT:" + aid)

    ids = [c.get("tcb_id") for c in tcb.get("components", [])]
    if "python_json_parser" not in ids or not tcb.get("common_mode_risk_explicit"):
        raise RuntimeError("H7_COMMON_TCB_DISCLOSURE_DRIFT")

    evidence = {
        "schema": SCHEMA,
        "milestone": "P159/OCC-1H/H7",
        "decision": DECISION,
        "qualified_attack_ids": ["A070","A071","A075"],
        "qualified_count": 3,
        "qualifications": QUALIFICATIONS,
        "source_hashes": {k:_sha(p) for k,p in paths.items()},
        "observations": {
            "a070_second_independent_parser_oracle_proven": False,
            "a071_common_tcb_disclosed": True,
            "a071_shared_bug_resistance_empirically_proven": False,
            "a075_executable_self_upgrade_path_proven": False,
        },
        "verdicts_modified": False,
        "canonical_sources_modified": False,
        "compiled_profile_modified": False,
        "occ1f_modified": False,
        "normative_auto_rewrite": False,
        "authorization_created": False,
        "execution_performed": False,
        "functional_only": True,
        "phenomenology_undetermined": True,
        "occ1h_closed": False,
        "occ1i_opened": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "limitations": [
            "Qualification explains why the three current ROOT+INCONCLUSIVE verdicts remain unresolved; it does not promote them.",
            "Common-TCB integrity/disclosure is not equivalent to empirical independence from shared defects.",
            "No P160 runtime mechanism is created or inferred.",
        ],
    }
    basis = dict(evidence)
    evidence["evidence_sha256"] = hashlib.sha256(
        json.dumps(basis, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return evidence
