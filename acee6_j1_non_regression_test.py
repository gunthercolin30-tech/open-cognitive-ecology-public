from ontology.acee_installation_executor import AceeInstallationExecutor
for name in ("build_final_report", "inspect_replay", "inspect_replay_registry", "recover_transaction", "recover_incomplete_transactions", "step"):
    assert hasattr(AceeInstallationExecutor, name), name
print("ACEE6_J1_NON_REGRESSION_OK")
