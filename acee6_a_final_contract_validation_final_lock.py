from acee6_a_contract_snapshot import FUNCTIONAL_CONCLUSION_ONLY, PHENOMENOLOGY_UNDETERMINED, PUBLIC_CONTRACT
from acee6_a_final_contract_validation_suite import main as suite_main


def main():
    suite_main()
    assert FUNCTIONAL_CONCLUSION_ONLY is True
    assert PHENOMENOLOGY_UNDETERMINED is True
    assert set(PUBLIC_CONTRACT) == {
        "acee6_test_requirements_registry",
        "acee6_transaction_state_contract",
        "acee6_a_hardening_contract",
    }
    print("ACEE6_A3_FINAL_CONTRACT_VALIDATION_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
