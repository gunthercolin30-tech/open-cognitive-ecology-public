"""Bounded G5 regression tests; synthetic inputs and in-memory effects only."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock
from types import SimpleNamespace
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "p162_g5_under_test", ROOT / "ontology/governed_effector_adapter.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def inputs(lease="L1", reservation="R1", claim_hash="CH1", key="K1"):
    target = {"path": "synthetic-target"}
    claim = SimpleNamespace(lease_id=lease, reservation_id=reservation,
                            claim_hash=claim_hash, adapter_id="A1")
    handle = SimpleNamespace(lease_id=lease, reservation_id=reservation,
                             claim_hash=claim_hash, adapter_id="A1",
                             effector_id="E1", handle_id="H1",
                             operation_id="WRITE", target_binding=target)
    credential = SimpleNamespace(lease_id=lease, reservation_id=reservation,
                                 claim_hash=claim_hash, adapter_id="A1",
                                 effector_id="E1", handle_id="H1",
                                 allowed_operation="WRITE", target_binding=target,
                                 broker_use_id="B1", credential_ref="opaque-test-ref")
    return dict(claim=claim, handle=handle, brokered_use=credential,
                registry_entry=dict(status="ACTIVE", adapter_id="A1",
                                    adapter_hash="AH1", effector_id="E1"),
                capability_id="C1", capability_version="1", effect_class="TEST",
                final_state=dict(lease_current=True, reservation_current=True,
                                 revoked=False, target_current=True,
                                 critical_preconditions_satisfied=True,
                                 security_state="VERIFIED", adapter_attestation="AH1"),
                idempotency_key=key, now_iso="2026-11-08T12:00:00+00:00")


class ReplayHardeningTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.calls_lock = Lock()

    def effect(self, **kwargs):
        with self.calls_lock:
            self.calls.append(kwargs)
        return {"effect_status": "EFFECT_CONFIRMED"}

    def adapter(self, effect=None):
        return MODULE.GovernedEffectorAdapter(
            adapter_id="A1", adapter_version="1", adapter_hash="AH1",
            effector_id="E1", effector_callable=effect or self.effect,
            allowed_effect_classes=["TEST"])

    def test_changed_key_cannot_replay(self):
        a = self.adapter()
        self.assertEqual(a.execute(**inputs())["status"], "EFFECT_CONFIRMED")
        self.assertEqual(a.execute(**inputs(key="K2"))["reason"], "effect_attempt_replay")
        self.assertEqual(len(self.calls), 1)

    def test_same_key_cannot_replay(self):
        a = self.adapter()
        a.execute(**inputs())
        self.assertEqual(a.execute(**inputs())["reason"], "effect_attempt_replay")
        self.assertEqual(len(self.calls), 1)

    def test_same_lease_cannot_be_rebound_to_new_reservation(self):
        a = self.adapter()
        a.execute(**inputs())
        self.assertEqual(a.execute(**inputs(reservation="R2", key="K2"))["reason"],
                         "effect_attempt_replay")
        self.assertEqual(len(self.calls), 1)

    def test_same_reservation_cannot_be_rebound_to_new_lease(self):
        a = self.adapter()
        a.execute(**inputs())
        self.assertEqual(a.execute(**inputs(lease="L2", key="K2"))["reason"],
                         "effect_attempt_replay")
        self.assertEqual(len(self.calls), 1)

    def test_distinct_rights_can_use_same_correlation_key(self):
        a = self.adapter()
        self.assertEqual(a.execute(**inputs())["status"], "EFFECT_CONFIRMED")
        other = inputs(lease="L2", reservation="R2", claim_hash="CH2")
        self.assertEqual(a.execute(**other)["status"], "EFFECT_CONFIRMED")
        self.assertEqual(len(self.calls), 2)

    def test_concurrent_distinct_keys_allow_one_effect(self):
        a = self.adapter()
        barrier = Barrier(16)
        def worker(i):
            barrier.wait(timeout=10)
            return a.execute(**inputs(key="K" + str(i)))["status"]
        with ThreadPoolExecutor(max_workers=16) as pool:
            results = list(pool.map(worker, range(16)))
        self.assertEqual(results.count("EFFECT_CONFIRMED"), 1)
        self.assertEqual(results.count("EXECUTION_BLOCKED_AT_FINAL_RECHECK"), 15)
        self.assertEqual(len(self.calls), 1)

    def test_unknown_outcomes_never_release_rights(self):
        for failure in (TimeoutError, RuntimeError, None):
            with self.subTest(failure=failure):
                calls = []
                def effect(**kw):
                    calls.append(kw)
                    if failure:
                        raise failure("synthetic failure after possible effect")
                    return {"unexpected": True}
                a = self.adapter(effect)
                first = a.execute(**inputs())
                self.assertEqual(first["status"], "EFFECT_STATE_INDETERMINATE")
                self.assertIs(first["blind_retry_allowed"], False)
                self.assertEqual(a.execute(**inputs(key="K2"))["reason"], "effect_attempt_replay")
                self.assertEqual(len(calls), 1)

    def test_partial_effect_never_releases_rights(self):
        a = self.adapter(lambda **kw: {"effect_status": "EFFECT_PARTIAL"})
        self.assertEqual(a.execute(**inputs())["status"], "EFFECT_PARTIAL")
        self.assertEqual(a.execute(**inputs(key="K2"))["reason"], "effect_attempt_replay")

    def test_chain_identity_substitutions_block_before_effect(self):
        for obj, field in (("handle", "lease_id"), ("handle", "reservation_id"),
                           ("brokered_use", "lease_id"),
                           ("brokered_use", "reservation_id"),
                           ("brokered_use", "claim_hash")):
            with self.subTest(obj=obj, field=field):
                kw = inputs()
                setattr(kw[obj], field, "OTHER")
                self.assertEqual(self.adapter().execute(**kw)["status"],
                                 "EXECUTION_BLOCKED_AT_FINAL_RECHECK")
        self.assertEqual(self.calls, [])

    def test_invalid_identity_is_blocked(self):
        for field in ("lease", "reservation", "claim_hash", "key"):
            for value in (None, "", " ", 1, True, []):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.adapter().execute(**inputs(**{field: value}))["status"],
                                     "EXECUTION_BLOCKED_AT_FINAL_RECHECK")
        self.assertEqual(self.calls, [])

    def test_revocation_before_attempt_blocks_without_consuming_local_guard(self):
        a = self.adapter()
        kw = inputs()
        kw["final_state"]["revoked"] = True
        self.assertEqual(a.execute(**kw)["reason"], "last_second_revocation")
        self.assertEqual(self.calls, [])
        # A fresh verified input is needed; the first call never reached dispatch.
        self.assertEqual(a.execute(**inputs())["status"], "EFFECT_CONFIRMED")

    def test_reentrant_effector_cannot_dispatch_again(self):
        nested = []
        def effect(**kw):
            self.calls.append(kw)
            nested.append(a.execute(**inputs(key="nested")))
            return {"effect_status": "EFFECT_CONFIRMED"}
        a = self.adapter(effect)
        self.assertEqual(a.execute(**inputs())["status"], "EFFECT_CONFIRMED")
        self.assertEqual(nested[0]["reason"], "effect_attempt_replay")
        self.assertEqual(len(self.calls), 1)


if __name__ == "__main__":
    unittest.main()
