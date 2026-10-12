from acee6_transaction_state_contract import ALLOWED_TRANSITIONS, STATES, SUCCESS_STATE


def main():
    seen = {"RECEIVED"}
    pending = ["RECEIVED"]
    while pending:
        state = pending.pop(0)
        for target in ALLOWED_TRANSITIONS[state]:
            if target not in seen:
                seen.add(target)
                pending.append(target)
    assert seen == set(STATES)
    assert {source for source, targets in ALLOWED_TRANSITIONS.items() if SUCCESS_STATE in targets} == {"COMMITTING"}
    print("ACEE6_A_STATE_REACHABILITY_OK")


if __name__ == "__main__":
    main()
