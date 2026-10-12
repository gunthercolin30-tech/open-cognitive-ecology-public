"""P162-G6 G-side handoff projection over native P162-F authorities.

This component is non-effecting. It consumes the already-defined F4 single-use
handoff exactly once, verifies durable F5 reservation state and live
authorization state, then emits the minimal G1-compatible lease view.

It never mints an authorization, reservation, lease, execution claim, scoped
handle or credential, and never calls an effector.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class HandoffProjection:
    status: str
    reason: str | None
    lease: dict[str, Any] | None


class GovernedExecutionHandoffProjection:
    def __init__(self, *, reservation_manager: Any, lease_issuer: Any, recovery_journal: Any):
        self._reservation_manager = reservation_manager
        self._lease_issuer = lease_issuer
        self._recovery_journal = recovery_journal

    def project_once(
        self,
        *,
        lease: Mapping[str, Any],
        reservation: Mapping[str, Any],
        audience: str,
        executor_id: str,
        capability_instance_id: str,
        operation_id: str,
        target_binding: Any,
        now: Any,
    ) -> HandoffProjection:
        required_reservation = (
            "reservation_id",
            "authorization_token_id",
            "status",
            "executor_id",
            "operation_id",
            "target_binding",
        )
        required_lease = (
            "lease_id",
            "reservation_id",
            "lease_nonce",
            "executor_id",
            "capability_instance_id",
            "operation_id",
            "target_binding",
            "audience",
        )
        if any(k not in reservation for k in required_reservation):
            return self._blocked("reservation_incomplete")
        if any(k not in lease for k in required_lease):
            return self._blocked("lease_incomplete")
        if lease["reservation_id"] != reservation["reservation_id"]:
            return self._blocked("reservation_binding_mismatch")
        if lease["executor_id"] != reservation["executor_id"]:
            return self._blocked("executor_binding_mismatch")
        if lease["operation_id"] != reservation["operation_id"]:
            return self._blocked("operation_binding_mismatch")
        if lease["target_binding"] != reservation["target_binding"]:
            return self._blocked("target_binding_mismatch")

        state_reader = getattr(self._reservation_manager, "state", None)
        validate = getattr(self._lease_issuer, "validate_for_handoff", None)
        consume = getattr(self._lease_issuer, "mark_handoff_once", None)
        reconstruct = getattr(self._recovery_journal, "reconstruct", None)
        if not all(callable(x) for x in (state_reader, validate, consume, reconstruct)):
            return self._blocked("native_authority_unavailable")

        # F5 durable authority: only a currently RESERVED reconstructed state may cross.
        recovered = reconstruct(reservation["reservation_id"])
        if not isinstance(recovered, dict):
            return self._blocked("reservation_state_indeterminate")
        if recovered.get("state") != "RESERVED":
            return self._blocked("reservation_not_current")

        # Live authorization authority, not a copied/synthetic flag.
        auth = state_reader(reservation["authorization_token_id"])
        if auth is None:
            return self._blocked("authorization_state_unknown")
        if bool(getattr(auth, "revoked", True)):
            return self._blocked("authorization_revoked")
        if bool(getattr(auth, "expired", True)):
            return self._blocked("authorization_expired")
        if bool(getattr(auth, "indeterminate", True)):
            return self._blocked("authorization_indeterminate")

        verdict = validate(
            dict(lease),
            audience=audience,
            executor_id=executor_id,
            capability_instance_id=capability_instance_id,
            operation_id=operation_id,
            target_binding=target_binding,
            now=now,
        )
        if verdict != "LEASE_CURRENT_FOR_HANDOFF":
            return self._blocked(str(verdict).lower())

        # F4 is the authority for single-use handoff. This is the only state transition
        # performed here; it grants no execution right and performs no external effect.
        if consume(lease["lease_id"]) is not True:
            return self._blocked("lease_replay")

        # Fail closed on state changes racing with handoff consumption.
        recovered_after = reconstruct(reservation["reservation_id"])
        auth_after = state_reader(reservation["authorization_token_id"])
        if not isinstance(recovered_after, dict) or recovered_after.get("state") != "RESERVED":
            return self._blocked("reservation_changed_during_handoff")
        if auth_after is None:
            return self._blocked("authorization_state_unknown_after_handoff")
        if (
            bool(getattr(auth_after, "revoked", True))
            or bool(getattr(auth_after, "expired", True))
            or bool(getattr(auth_after, "indeterminate", True))
        ):
            return self._blocked("authorization_changed_during_handoff")

        # G1 expects a boundary snapshot. `used=False` means the lease was not replayed
        # when this one-shot handoff was admitted. The F4 nonce is already consumed,
        # so a second projection cannot reproduce this snapshot.
        projected = dict(lease)
        projected["reservation_status"] = reservation["status"]
        projected["used"] = False
        projected["revoked"] = False
        return HandoffProjection("HANDOFF_PROJECTED", None, projected)

    @staticmethod
    def _blocked(reason: str) -> HandoffProjection:
        return HandoffProjection("HANDOFF_BLOCKED", reason, None)
