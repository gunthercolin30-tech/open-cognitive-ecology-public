# P162-PC4: fail-closed journal reading and monotone recovery

This refinement reuses `ReservationRecoveryJournal` (P162-F5) in the G6/PC4
restart path. A JSON `null` record previously raised `AttributeError` rather
than returning a conservative assessment. A late `RESERVATION_COMMITTED`
could also replace a reconstructed `CONSUMED` state with `RESERVED`.

Journal reading now returns `INDETERMINATE` for non-object records, invalid
UTF-8, duplicate keys, non-finite numbers, boolean sequence numbers, missing
final newlines, unreadable files, symlinks and non-regular files. Opened file
descriptors are closed on both valid and rejected paths. New append calls
cannot override chain metadata or append to corrupt history. The governed
append path still uses its caller's preissued filesystem context.

Reconstruction cannot reduce the risk already observed for a reservation.
Invalid backup states remain indeterminate. Recovery never gains replay or
resume permission from any of these changes. This is P162-F F-12/F-13 and
PC4 defensive hardening; it is not P162-L or the global PC4 acceptance.

## Validate in the public clone

```bash
python3 reservation_recovery_manager_fast_acceptance_suite.py
python3 p162_pc4_recovery_final_lock.py
```

Both commands use only the Python standard library and disposable test
journals. The lock-named command explicitly prints that the P162 global lock
has not been executed.

## Install in the existing private macOS project

Download `tools/refine_reservation_recovery_manager_p162_pc4.py` to Downloads.
The installer checks inventory and exact module SHA256, refuses unknown local
changes, verifies a `.py.bak`, replaces files atomically and rolls back completed
writes on failure. It adds tests and a bounded check without changing inventory
or granting runtime authority.

```bash
cd ~/open-cognitive-ecology
python3 ~/Downloads/refine_reservation_recovery_manager_p162_pc4.py --check
python3 ~/Downloads/refine_reservation_recovery_manager_p162_pc4.py
python3 reservation_recovery_manager_fast_acceptance_suite.py
python3 final_lock.py p162_pc4_recovery
python3 -m validation.p162_pc4_durable_reconstruction_authority_test
python3 -m validation.p162_pc4_concurrent_positive_recovery_test
```

The last two suites need the private runtime/test fixtures; their canonical
result remains HOLD. Do not run them against the smaller public clone.

Rollback of the module, if needed:

```bash
cd ~/open-cognitive-ecology
cp -p ontology/reservation_recovery_manager.py.cdbac9f7725cd70d.py.bak ontology/reservation_recovery_manager.py
```

Tests remain to preserve the counterexamples and are expected to fail against
the original implementation. Evidence is in the adjacent JSON report: 17 new
tests, 43 existing F5-F7 tests, four PC4 script suites and three detected
protection-removal mutants. macOS execution is not inferred from Linux results.

This does not certify concurrent writers, independent checkpoint continuity,
protected authority issuance, or automatic restart. Continue the PC4 integrated
causal and authority path before considering canonical closure; run full
`python3 -m validation.main` at the required major milestone.
