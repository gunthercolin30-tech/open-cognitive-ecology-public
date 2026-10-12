from __future__ import annotations

"""Stable ACEE6-A public contract snapshot and empirical traceability map."""

PUBLIC_SCHEMA_VERSION = "1.0.0"
PRIMITIVE = "ACEE6_A_CONTRACT_SNAPSHOT"

PUBLIC_CONTRACT = {
    "acee6_test_requirements_registry": {
        "constants": (
            "PUBLIC_SCHEMA_VERSION", "PRIMITIVE", "RISK_FAMILIES",
            "STAGES", "SEVERITIES", "TEST_REQUIREMENTS",
        ),
        "callables": (
            "requirements_by_stage", "requirements_by_family",
            "registry_summary",
        ),
    },
    "acee6_transaction_state_contract": {
        "constants": (
            "PUBLIC_SCHEMA_VERSION", "PRIMITIVE", "STATES",
            "TERMINAL_STATES", "SUCCESS_STATE", "SUCCESS_MARKER",
            "ALLOWED_TRANSITIONS", "RECOVERY_POLICY",
            "MANDATORY_COMMIT_EVIDENCE", "EPISTEMIC_GUARDS",
        ),
        "callables": (
            "can_transition", "validate_transition_path",
            "is_success_state", "recovery_action",
        ),
    },
    "acee6_a_hardening_contract": {
        "constants": (
            "PUBLIC_SCHEMA_VERSION", "PRIMITIVE", "INTERNAL_SUBSTAGES",
            "TERMINAL_OUTPUTS", "QUARANTINE_STATES",
            "BOUNDED_LOOP_POLICY", "PROHIBITED_LOOPS",
            "FAILURE_DISPOSITION", "REQUIREMENT_DEPENDENCIES",
        ),
        "callables": (
            "terminal_output", "loop_allowed", "failure_disposition",
        ),
    },
}

EMPIRICAL_TRACEABILITY = {
    "manifest_admission": {"origin": "ACEE5", "evidence": ("manifest binding", "replay resistance")},
    "path_security": {"origin": "ACEE5/ACEE11/ACEE17", "evidence": ("symlink escape", "canonicalization")},
    "transaction_plan": {"origin": "ACEE4/ACEE11", "evidence": ("duplicate phase", "target collision")},
    "backup_integrity": {"origin": "ACEE5/ACEE11", "evidence": ("backup swap", "hash verification")},
    "file_write": {"origin": "ACEE11/ACEE19", "evidence": ("multifile atomicity", "atomic persistence")},
    "compilation": {"origin": "OCE refiners", "evidence": ("py_compile", "syntax rejection")},
    "registry_inventory": {"origin": "OCE refiners", "evidence": ("inventory updates", "registry preservation")},
    "validation_orchestration": {"origin": "ACEE7", "evidence": ("command guard", "timeouts and warnings")},
    "global_validation": {"origin": "validation.main/ACEE20", "evidence": ("error_count zero", "global certification")},
    "fault_injection": {"origin": "ACEE11/ACEE19", "evidence": ("atomic failure cleanup", "rollback injection")},
    "rollback": {"origin": "ACEE11", "evidence": ("restoration", "rollback hash verification")},
    "atomicity_durability": {"origin": "ACEE11/ACEE13/ACEE19", "evidence": ("fsync", "append-only history")},
    "concurrency_isolation": {"origin": "ACEE11/ACEE13/ACEE19", "evidence": ("threads", "multiprocess")},
    "recovery_replay": {"origin": "ACEE13/ACEE16", "evidence": ("restart continuity", "hash-chain restart")},
    "corruption_tamper": {"origin": "ACEE13/ACEE14/ACEE16", "evidence": ("middle corruption", "SHA-256 integrity")},
    "module_boundaries": {"origin": "ACEE4/ACEE5/ACEE7/ACEE11", "evidence": ("non-execution boundary", "rollback distinction")},
    "public_contract": {"origin": "ACEE5/AW14", "evidence": ("API snapshot", "schema compatibility")},
    "fuzz_property": {"origin": "AW12/ACEE5", "evidence": ("deterministic fuzz", "input immutability")},
    "performance_resources": {"origin": "AW14/ACEE5", "evidence": ("performance regression", "history scalability")},
    "mutation_longitudinal": {"origin": "AW14/ACEE20", "evidence": ("mutation score", "1000-cycle stability")},
}

FUNCTIONAL_CONCLUSION_ONLY = True
PHENOMENOLOGY_UNDETERMINED = True
