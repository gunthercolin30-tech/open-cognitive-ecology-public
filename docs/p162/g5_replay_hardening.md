# P162-G5: prevent replay through a changed idempotency key

The supplied `GovernedEffectorAdapter` keyed its attempt guard by lease,
reservation **and caller-selected idempotency key**. Repeating the same right
with a different key produced a second injected effect. This violates P162-G
G-3/G-12 and the lease replay protections required by G-01/G-18.

The refinement consumes both lease and reservation identities under one lock
before dispatch. Different correlation keys, a substituted reservation, or a
substituted lease cannot bypass that adapter object's guard. It also verifies
lease/reservation/claim bindings throughout the handle/credential chain.
Timeouts, exceptions and partial or unknown effects do not release the guard.
Distinct rights still execute: the tests include positive controls.

This is a bounded in-process repair. It does not authenticate caller-supplied
objects, provide persistent anti-replay across restarts/adapter objects, or
close PC4/PC5, P162-J/K, or P162-L. Those require their own integrated evidence.

## Public clone validation

```bash
python3 governed_effector_adapter_fast_acceptance_suite.py
python3 p162_g5_replay_final_lock.py
```

These commands need only the Python standard library. The lock-named entry
point verifies this bounded refinement; it explicitly does not seal P162.

## Private macOS installation

Download `tools/refine_governed_effector_adapter_p162_g5_replay.py` to Downloads.
The installer defaults to `Path.home() / "open-cognitive-ecology"` and requires
the existing module's inventory entry and exact source SHA256. It refuses
unknown local edits, creates a verified `.py.bak` before replacing the module,
supports `--check`, performs atomic file replacements, and rolls back completed
writes if a later write fails. No network operations or inventory rewrite.

```bash
cd ~/open-cognitive-ecology
python3 ~/Downloads/refine_governed_effector_adapter_p162_g5_replay.py --check
python3 ~/Downloads/refine_governed_effector_adapter_p162_g5_replay.py
python3 governed_effector_adapter_fast_acceptance_suite.py
python3 final_lock.py p162_g5_replay
```

For the existing private regression tests (pytest required):

```bash
python3 -m pytest -q validation/p162g5_governed_effector_mediation_v1_test.py tests/test_p162_g5_replay_hardening.py
```

To restore the original module after installation:

```bash
cd ~/open-cognitive-ecology
cp -p ontology/governed_effector_adapter.py.7fdc3b9878cd3bb0.py.bak ontology/governed_effector_adapter.py
```

The installed tests remain for traceability; after rollback they are expected
to detect the original defect. No deletion or public synchronization is needed.

## Evidence and next gate

See `g5_replay_hardening_evidence.json` for hashes, 12 new passing tests, 64
existing passing functional tests and mutation probes. One historical F
manifest test was explicitly excluded because its protected manifest was not
supplied. macOS execution remains independent and has not been claimed.

Next: continue the G6/PC4 causal path using the supplied current runtime;
integrate durable replay and recovery evidence before considering closure.
Full `python3 -m validation.main` remains a major-checkpoint validation, not a
substitute for this bounded evidence or a source of execution authority.
