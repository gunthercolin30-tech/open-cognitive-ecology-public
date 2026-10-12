from __future__ import annotations

"""Machine-readable ACEE6 validation requirements.

This file is a development and certification contract. It does not execute an
installation and does not grant installation authority.
"""

PUBLIC_SCHEMA_VERSION = "1.0.0"
PRIMITIVE = "ACEE6_TEST_REQUIREMENTS_REGISTRY"

RISK_FAMILIES = (
    "manifest_admission",
    "path_security",
    "transaction_plan",
    "backup_integrity",
    "file_write",
    "compilation",
    "registry_inventory",
    "validation_orchestration",
    "global_validation",
    "fault_injection",
    "rollback",
    "atomicity_durability",
    "concurrency_isolation",
    "recovery_replay",
    "corruption_tamper",
    "module_boundaries",
    "public_contract",
    "fuzz_property",
    "performance_resources",
    "mutation_longitudinal",
)

STAGES = tuple("ABCDEFGHIJK")
SEVERITIES = ("critical", "high", "medium")


def _req(test_id, family, severity, stage, marker, *, fast=False,
         rollback=False, timeout=30, dependencies=()):
    return {
        "test_id": test_id,
        "risk_family": family,
        "severity": severity,
        "mandatory_stage": stage,
        "timeout_seconds": timeout,
        "rollback_required_on_failure": rollback,
        "eligible_for_fast_suite": fast,
        "eligible_for_full_validation": True,
        "dependencies": tuple(dependencies),
        "expected_marker": marker,
    }


TEST_REQUIREMENTS = (
    # Manifest admission
    _req("ACEE6-MAN-001", "manifest_admission", "critical", "B", "ACEE6_MANIFEST_HASH_OK", fast=True),
    _req("ACEE6-MAN-002", "manifest_admission", "critical", "B", "ACEE6_MANIFEST_TAMPER_BLOCKED", fast=True),
    _req("ACEE6-MAN-003", "manifest_admission", "critical", "B", "ACEE6_SCHEMA_COMPATIBILITY_OK"),
    _req("ACEE6-MAN-004", "manifest_admission", "critical", "B", "ACEE6_MANIFEST_REPLAY_BLOCKED"),
    _req("ACEE6-MAN-005", "manifest_admission", "high", "B", "ACEE6_MANIFEST_EXPIRY_OK"),
    _req("ACEE6-MAN-006", "manifest_admission", "critical", "B", "ACEE6_ROOT_BINDING_OK"),
    _req("ACEE6-MAN-007", "manifest_admission", "critical", "B", "ACEE6_CANDIDATE_BINDING_OK"),
    _req("ACEE6-MAN-008", "manifest_admission", "high", "B", "ACEE6_DRY_RUN_DIFF_OK"),

    # Path security
    _req("ACEE6-PATH-001", "path_security", "critical", "B", "ACEE6_OUTSIDE_ROOT_BLOCKED", fast=True),
    _req("ACEE6-PATH-002", "path_security", "critical", "H", "ACEE6_SYMLINK_ESCAPE_BLOCKED"),
    _req("ACEE6-PATH-003", "path_security", "critical", "H", "ACEE6_PARENT_SYMLINK_BLOCKED"),
    _req("ACEE6-PATH-004", "path_security", "critical", "H", "ACEE6_TOCTOU_PATH_SWAP_BLOCKED"),
    _req("ACEE6-PATH-005", "path_security", "high", "H", "ACEE6_MACOS_CANONICALIZATION_OK"),
    _req("ACEE6-PATH-006", "path_security", "high", "H", "ACEE6_UNICODE_ALIAS_BLOCKED"),
    _req("ACEE6-PATH-007", "path_security", "critical", "B", "ACEE6_TARGET_COLLISION_BLOCKED"),
    _req("ACEE6-PATH-008", "path_security", "critical", "H", "ACEE6_HARDLINK_ALIAS_BLOCKED"),

    # Transaction plan
    _req("ACEE6-PLAN-001", "transaction_plan", "critical", "B", "ACEE6_PLAN_COMPLETENESS_OK", fast=True),
    _req("ACEE6-PLAN-002", "transaction_plan", "critical", "B", "ACEE6_PLAN_ORDER_OK"),
    _req("ACEE6-PLAN-003", "transaction_plan", "critical", "B", "ACEE6_DUPLICATE_STEP_BLOCKED"),
    _req("ACEE6-PLAN-004", "transaction_plan", "critical", "B", "ACEE6_DUPLICATE_TRANSACTION_BLOCKED"),
    _req("ACEE6-PLAN-005", "transaction_plan", "critical", "B", "ACEE6_CONTRADICTORY_OPERATION_BLOCKED"),
    _req("ACEE6-PLAN-006", "transaction_plan", "high", "B", "ACEE6_TEST_PLAN_REQUIRED"),

    # Backups
    _req("ACEE6-BAK-001", "backup_integrity", "critical", "D", "ACEE6_BACKUP_CREATED", rollback=True),
    _req("ACEE6-BAK-002", "backup_integrity", "critical", "D", "ACEE6_BACKUP_HASH_OK", rollback=True),
    _req("ACEE6-BAK-003", "backup_integrity", "critical", "G", "ACEE6_BACKUP_SWAP_BLOCKED", rollback=True),
    _req("ACEE6-BAK-004", "backup_integrity", "critical", "D", "ACEE6_BACKUP_SYMLINK_BLOCKED", rollback=True),
    _req("ACEE6-BAK-005", "backup_integrity", "high", "D", "ACEE6_NEW_FILE_BACKUP_SEMANTICS_OK", rollback=True),
    _req("ACEE6-BAK-006", "backup_integrity", "high", "D", "ACEE6_MODE_PRESERVATION_OK", rollback=True),

    # File writes
    _req("ACEE6-WRITE-001", "file_write", "critical", "D", "ACEE6_ATOMIC_WRITE_OK", rollback=True),
    _req("ACEE6-WRITE-002", "file_write", "critical", "D", "ACEE6_MULTIFILE_WRITE_OK", rollback=True),
    _req("ACEE6-WRITE-003", "file_write", "critical", "G", "ACEE6_PARTIAL_WRITE_RECOVERED", rollback=True),
    _req("ACEE6-WRITE-004", "file_write", "critical", "G", "ACEE6_DISK_FULL_RECOVERED", rollback=True),
    _req("ACEE6-WRITE-005", "file_write", "high", "D", "ACEE6_INVALID_ENCODING_BLOCKED", rollback=True),
    _req("ACEE6-WRITE-006", "file_write", "critical", "G", "ACEE6_TEMPORARY_CLEANUP_OK", rollback=True),

    # Compilation
    _req("ACEE6-COMP-001", "compilation", "critical", "D", "ACEE6_TARGET_COMPILE_OK", fast=True, rollback=True),
    _req("ACEE6-COMP-002", "compilation", "critical", "D", "ACEE6_SYNTAX_ERROR_ROLLBACK_OK", rollback=True),
    _req("ACEE6-COMP-003", "compilation", "critical", "E", "ACEE6_INFRA_COMPILE_OK", rollback=True),
    _req("ACEE6-COMP-004", "compilation", "high", "D", "ACEE6_IMPORT_FAILURE_BLOCKED", rollback=True),
    _req("ACEE6-COMP-005", "compilation", "high", "D", "ACEE6_COMPILE_TIMEOUT_OK", rollback=True),

    # Registries and inventories
    _req("ACEE6-REG-001", "registry_inventory", "critical", "E", "ACEE6_ROOT_REGISTRY_UPDATED", rollback=True),
    _req("ACEE6-REG-002", "registry_inventory", "critical", "E", "ACEE6_ONTOLOGY_REGISTRY_UPDATED", rollback=True),
    _req("ACEE6-REG-003", "registry_inventory", "critical", "E", "ACEE6_INVENTORY_TXT_UPDATED", rollback=True),
    _req("ACEE6-REG-004", "registry_inventory", "critical", "E", "ACEE6_INVENTORY_PY_UPDATED", rollback=True),
    _req("ACEE6-REG-005", "registry_inventory", "critical", "E", "ACEE6_ONTOLOGY_INVENTORY_UPDATED", rollback=True),
    _req("ACEE6-REG-006", "registry_inventory", "high", "E", "ACEE6_GLOBAL_CATALOG_UPDATED", rollback=True),
    _req("ACEE6-REG-007", "registry_inventory", "critical", "E", "ACEE6_EXISTING_ENTRIES_PRESERVED", rollback=True),
    _req("ACEE6-REG-008", "registry_inventory", "critical", "E", "ACEE6_NO_SELF_DEPENDENCY", rollback=True),
    _req("ACEE6-REG-009", "registry_inventory", "high", "E", "ACEE6_SEMANTIC_REGISTRY_COHERENCE_OK", rollback=True),
    _req("ACEE6-REG-010", "registry_inventory", "high", "E", "ACEE6_REGISTRY_IDEMPOTENCE_OK", rollback=True),

    # Validation orchestration
    _req("ACEE6-VAL-001", "validation_orchestration", "critical", "F", "ACEE6_FAST_GUARD_OK", rollback=True),
    _req("ACEE6-VAL-002", "validation_orchestration", "critical", "F", "ACEE6_FAST_ACCEPTANCE_OK", rollback=True),
    _req("ACEE6-VAL-003", "validation_orchestration", "critical", "F", "ACEE6_FINAL_LOCK_OK", rollback=True),
    _req("ACEE6-VAL-004", "validation_orchestration", "critical", "F", "ACEE6_FUNCTIONAL_TESTS_OK", rollback=True),
    _req("ACEE6-VAL-005", "validation_orchestration", "critical", "F", "ACEE6_DEGRADATION_TESTS_OK", rollback=True),
    _req("ACEE6-VAL-006", "validation_orchestration", "critical", "F", "ACEE6_NON_REGRESSION_OK", rollback=True),
    _req("ACEE6-VAL-007", "validation_orchestration", "high", "F", "ACEE6_SPECIALIZED_TESTS_OK", rollback=True),
    _req("ACEE6-VAL-008", "validation_orchestration", "high", "F", "ACEE6_TIMEOUT_HANDLING_OK", rollback=True),
    _req("ACEE6-VAL-009", "validation_orchestration", "high", "F", "ACEE6_WARNING_CLASSIFICATION_OK", rollback=True),
    _req("ACEE6-VAL-010", "validation_orchestration", "high", "F", "ACEE6_LARGE_OUTPUT_HANDLING_OK", rollback=True),

    # Global validation
    _req("ACEE6-GLOB-001", "global_validation", "critical", "F", "ACEE6_VALIDATION_MAIN_OK", rollback=True, timeout=300),
    _req("ACEE6-GLOB-002", "global_validation", "critical", "F", "ACEE6_ERROR_COUNT_ZERO", rollback=True),
    _req("ACEE6-GLOB-003", "global_validation", "critical", "F", "ACEE6_FAILED_CALLS_ZERO", rollback=True),
    _req("ACEE6-GLOB-004", "global_validation", "critical", "F", "ACEE6_REPORT_TRANSACTION_BOUND", rollback=True),
    _req("ACEE6-GLOB-005", "global_validation", "critical", "F", "ACEE6_STALE_REPORT_BLOCKED", rollback=True),

    # Fault injection and rollback
    _req("ACEE6-FAULT-001", "fault_injection", "critical", "G", "ACEE6_FAIL_BEFORE_BACKUP_OK", rollback=True),
    _req("ACEE6-FAULT-002", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_BACKUP_OK", rollback=True),
    _req("ACEE6-FAULT-003", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_WRITE_OK", rollback=True),
    _req("ACEE6-FAULT-004", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_COMPILE_OK", rollback=True),
    _req("ACEE6-FAULT-005", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_REGISTRY_OK", rollback=True),
    _req("ACEE6-FAULT-006", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_TESTS_OK", rollback=True),
    _req("ACEE6-FAULT-007", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_GLOBAL_VALIDATION_OK", rollback=True),
    _req("ACEE6-FAULT-008", "fault_injection", "critical", "G", "ACEE6_FAIL_DURING_REPORT_OK", rollback=True),

    _req("ACEE6-RB-001", "rollback", "critical", "G", "ACEE6_EXISTING_FILES_RESTORED", rollback=True),
    _req("ACEE6-RB-002", "rollback", "critical", "G", "ACEE6_NEW_FILES_REMOVED", rollback=True),
    _req("ACEE6-RB-003", "rollback", "critical", "G", "ACEE6_METADATA_RESTORED", rollback=True),
    _req("ACEE6-RB-004", "rollback", "critical", "G", "ACEE6_ROLLBACK_FAILURE_REPORTED", rollback=True),
    _req("ACEE6-RB-005", "rollback", "critical", "G", "ACEE6_NO_FALSE_COMPLETE_AFTER_ROLLBACK", rollback=True),

    # Atomicity and durability
    _req("ACEE6-ATOM-001", "atomicity_durability", "critical", "C", "ACEE6_PREPARED_JOURNAL_DURABLE", rollback=True),
    _req("ACEE6-ATOM-002", "atomicity_durability", "critical", "C", "ACEE6_WRITE_AHEAD_ORDER_OK", rollback=True),
    _req("ACEE6-ATOM-003", "atomicity_durability", "critical", "D", "ACEE6_FILE_FSYNC_OK", rollback=True),
    _req("ACEE6-ATOM-004", "atomicity_durability", "critical", "D", "ACEE6_DIRECTORY_FSYNC_OK", rollback=True),
    _req("ACEE6-ATOM-005", "atomicity_durability", "critical", "J", "ACEE6_COMMIT_REPORT_DURABLE"),
    _req("ACEE6-ATOM-006", "atomicity_durability", "critical", "I", "ACEE6_TRUNCATED_JOURNAL_DETECTED", rollback=True),

    # Concurrency and isolation
    _req("ACEE6-CONC-001", "concurrency_isolation", "critical", "H", "ACEE6_THREAD_ISOLATION_OK", rollback=True),
    _req("ACEE6-CONC-002", "concurrency_isolation", "critical", "H", "ACEE6_MULTIPROCESS_ISOLATION_OK", rollback=True),
    _req("ACEE6-CONC-003", "concurrency_isolation", "critical", "H", "ACEE6_SAME_TARGET_SERIALIZED", rollback=True),
    _req("ACEE6-CONC-004", "concurrency_isolation", "high", "H", "ACEE6_LOCK_TIMEOUT_OK", rollback=True),
    _req("ACEE6-CONC-005", "concurrency_isolation", "critical", "H", "ACEE6_ABANDONED_LOCK_RECOVERY_OK", rollback=True),
    _req("ACEE6-CONC-006", "concurrency_isolation", "critical", "H", "ACEE6_NO_DEADLOCK", rollback=True),

    # Recovery and replay
    _req("ACEE6-REC-001", "recovery_replay", "critical", "I", "ACEE6_RESUME_PREPARED_OK", rollback=True),
    _req("ACEE6-REC-002", "recovery_replay", "critical", "I", "ACEE6_RESUME_WRITING_OK", rollback=True),
    _req("ACEE6-REC-003", "recovery_replay", "critical", "I", "ACEE6_RESUME_TESTING_OK", rollback=True),
    _req("ACEE6-REC-004", "recovery_replay", "critical", "I", "ACEE6_ALREADY_COMMITTED_IDEMPOTENT"),
    _req("ACEE6-REC-005", "recovery_replay", "critical", "I", "ACEE6_ALREADY_ROLLED_BACK_IDEMPOTENT"),
    _req("ACEE6-REC-006", "recovery_replay", "critical", "I", "ACEE6_TRANSACTION_ID_COLLISION_BLOCKED"),

    # Corruption and tamper
    _req("ACEE6-CORR-001", "corruption_tamper", "critical", "I", "ACEE6_JOURNAL_CORRUPTION_DETECTED", rollback=True),
    _req("ACEE6-CORR-002", "corruption_tamper", "critical", "I", "ACEE6_HASH_CHAIN_CORRUPTION_DETECTED", rollback=True),
    _req("ACEE6-CORR-003", "corruption_tamper", "critical", "H", "ACEE6_CANDIDATE_TAMPER_BLOCKED", rollback=True),
    _req("ACEE6-CORR-004", "corruption_tamper", "critical", "H", "ACEE6_BACKUP_TAMPER_BLOCKED", rollback=True),
    _req("ACEE6-CORR-005", "corruption_tamper", "critical", "J", "ACEE6_FINAL_REPORT_TAMPER_DETECTED"),

    # Boundaries
    _req("ACEE6-BND-001", "module_boundaries", "critical", "A", "ACEE6_DOES_NOT_GENERATE_CODE", fast=True),
    _req("ACEE6-BND-002", "module_boundaries", "critical", "A", "ACEE6_DOES_NOT_SELECT_CANDIDATE", fast=True),
    _req("ACEE6-BND-003", "module_boundaries", "critical", "A", "ACEE6_REQUIRES_ACEE5_AUTHORITY", fast=True),
    _req("ACEE6-BND-004", "module_boundaries", "critical", "F", "ACEE6_DELEGATES_VALIDATION_TO_ACEE7"),
    _req("ACEE6-BND-005", "module_boundaries", "critical", "G", "ACEE6_DELEGATES_ROLLBACK_TO_ACEE11"),
    _req("ACEE6-BND-006", "module_boundaries", "critical", "A", "ACEE6_ACEE4_ACEE11_ROLLBACK_SEMANTICS_SEPARATE", fast=True),

    # Public contract
    _req("ACEE6-API-001", "public_contract", "critical", "J", "ACEE6_PUBLIC_SCHEMA_OK", fast=True),
    _req("ACEE6-API-002", "public_contract", "critical", "J", "ACEE6_INPUT_IMMUTABILITY_OK"),
    _req("ACEE6-API-003", "public_contract", "critical", "J", "ACEE6_SUCCESS_STATUS_OK"),
    _req("ACEE6-API-004", "public_contract", "critical", "J", "ACEE6_FAILURE_STATUS_OK"),
    _req("ACEE6-API-005", "public_contract", "critical", "J", "ACEE6_EPISTEMIC_GUARDS_OK", fast=True),
    _req("ACEE6-API-006", "public_contract", "high", "J", "ACEE6_API_SNAPSHOT_OK"),

    # Fuzz/property
    _req("ACEE6-FUZZ-001", "fuzz_property", "high", "K", "ACEE6_MANIFEST_FUZZ_OK", timeout=120),
    _req("ACEE6-FUZZ-002", "fuzz_property", "high", "K", "ACEE6_PATH_FUZZ_OK", timeout=120),
    _req("ACEE6-FUZZ-003", "fuzz_property", "high", "K", "ACEE6_PLAN_FUZZ_OK", timeout=120),
    _req("ACEE6-FUZZ-004", "fuzz_property", "high", "K", "ACEE6_ATOMICITY_PROPERTY_OK", timeout=120),
    _req("ACEE6-FUZZ-005", "fuzz_property", "high", "K", "ACEE6_ROLLBACK_PROPERTY_OK", timeout=120),

    # Performance/resources
    _req("ACEE6-PERF-001", "performance_resources", "medium", "K", "ACEE6_SINGLE_TARGET_PERFORMANCE_OK", timeout=120),
    _req("ACEE6-PERF-002", "performance_resources", "medium", "K", "ACEE6_HUNDRED_TARGET_SCALABILITY_OK", timeout=300),
    _req("ACEE6-PERF-003", "performance_resources", "high", "K", "ACEE6_MEMORY_LEAK_OK", timeout=300),
    _req("ACEE6-PERF-004", "performance_resources", "high", "K", "ACEE6_FILE_DESCRIPTOR_LEAK_OK", timeout=300),
    _req("ACEE6-PERF-005", "performance_resources", "medium", "K", "ACEE6_JOURNAL_GROWTH_OK", timeout=300),

    # Mutation/longitudinal
    _req("ACEE6-MUT-001", "mutation_longitudinal", "high", "K", "ACEE6_MUTATION_SCORE_OK", timeout=600),
    _req("ACEE6-LONG-001", "mutation_longitudinal", "high", "K", "ACEE6_100_TRANSACTION_OK", timeout=600),
    _req("ACEE6-LONG-002", "mutation_longitudinal", "high", "K", "ACEE6_1000_TRANSACTION_OK", timeout=1800),
    _req("ACEE6-LONG-003", "mutation_longitudinal", "high", "K", "ACEE6_HASH_DRIFT_OK", timeout=600),
    _req("ACEE6-LONG-004", "mutation_longitudinal", "high", "K", "ACEE6_DECISION_STABILITY_OK", timeout=600),
)


def requirements_by_stage(stage):
    return tuple(item for item in TEST_REQUIREMENTS if item["mandatory_stage"] == stage)


def requirements_by_family(family):
    return tuple(item for item in TEST_REQUIREMENTS if item["risk_family"] == family)


def registry_summary():
    return {
        "primitive": PRIMITIVE,
        "public_schema_version": PUBLIC_SCHEMA_VERSION,
        "requirement_count": len(TEST_REQUIREMENTS),
        "risk_family_count": len(RISK_FAMILIES),
        "stage_count": len(STAGES),
        "critical_count": sum(r["severity"] == "critical" for r in TEST_REQUIREMENTS),
        "fast_eligible_count": sum(r["eligible_for_fast_suite"] for r in TEST_REQUIREMENTS),
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
