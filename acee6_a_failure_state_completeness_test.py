from acee6_transaction_state_contract import ALLOWED_TRANSITIONS, TERMINAL_STATES


def reachable(start, targets):
    pending = [start]
    seen = set()
    while pending:
        state = pending.pop()
        if state in seen:
            continue
        seen.add(state)
        if state in targets:
            return True
        pending.extend(ALLOWED_TRANSITIONS[state])
    return False


def main():
    safe = {"REJECTED", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}
    for state in ALLOWED_TRANSITIONS:
        if state not in TERMINAL_STATES:
            assert reachable(state, safe), state
    assert reachable("ROLLING_BACK", {"ROLLED_BACK", "ROLLBACK_FAILED", "STATE_CORRUPTED"})
    print("ACEE6_A_FAILURE_STATE_COMPLETENESS_OK")


if __name__ == "__main__":
    main()
