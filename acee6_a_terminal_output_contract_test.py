from acee6_a_hardening_contract import TERMINAL_OUTPUTS, terminal_output
from acee6_transaction_state_contract import SUCCESS_MARKER, TERMINAL_STATES


def main():
    assert set(TERMINAL_OUTPUTS) == set(TERMINAL_STATES)
    assert terminal_output("COMMITTED") == SUCCESS_MARKER
    for state in TERMINAL_STATES - {"COMMITTED"}:
        assert terminal_output(state) != SUCCESS_MARKER
    assert terminal_output("WRITING") is None
    print("ACEE6_A_TERMINAL_OUTPUT_CONTRACT_OK")


if __name__ == "__main__":
    main()
