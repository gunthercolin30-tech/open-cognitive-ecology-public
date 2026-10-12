from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from ontology.execution_reservation_manager import AtomicReservationManager, AuthorizationUseState
from ontology.execution_lease_issuer import ExecutionLeaseIssuer
from ontology.reservation_recovery_manager import ReservationRecoveryJournal
from ontology.governed_execution_adapter import assess_execution_boundary
from ontology.governed_execution_handoff_projection import GovernedExecutionHandoffProjection

NOW = datetime(2026, 10, 2, 12, 0, 0, tzinfo=timezone.utc)


def setup_env(tmp_path):
    rm = AtomicReservationManager()
    rm.put_authorization_state(AuthorizationUseState("tok", 2))
    reservation = rm.reserve(
        idempotency_key="rk",
        invocation_request_id="inv",
        token_id="tok",
        effective_scope_hash="SH",
        executor_id="EX",
        capability_id="CAP",
        operation_id="OP",
        target_binding={"id": "T"},
        expected_state_version=0,
    )
    journal = ReservationRecoveryJournal(tmp_path / "reservation.journal")
    journal.append({"type": "RESERVATION_COMMITTED", "reservation_id": reservation["reservation_id"]})
    issuer = ExecutionLeaseIssuer()
    lease = issuer.issue(
        idempotency_key="lk",
        reservation=reservation,
        invocation_request_hash="IH",
        capability_instance_id="CI",
        audience="A",
        issued_at=NOW,
        requested_expires_at=NOW + timedelta(minutes=5),
        token_expires_at=NOW + timedelta(minutes=5),
        reservation_expires_at=NOW + timedelta(minutes=5),
    )
    projector = GovernedExecutionHandoffProjection(
        reservation_manager=rm, lease_issuer=issuer, recovery_journal=journal
    )
    return rm, reservation, journal, issuer, lease, projector


def call(projector, lease, reservation):
    return projector.project_once(
        lease=lease,
        reservation=reservation,
        audience="A",
        executor_id="EX",
        capability_instance_id="CI",
        operation_id="OP",
        target_binding={"id": "T"},
        now=NOW + timedelta(seconds=1),
    )


def test_functional_projection_feeds_g1(tmp_path):
    rm, reservation, journal, issuer, lease, projector = setup_env(tmp_path)
    result = call(projector, lease, reservation)
    assert result.status == "HANDOFF_PROJECTED"
    assert result.lease["reservation_status"] == "RESERVED"
    assert result.lease["used"] is False
    assert result.lease["revoked"] is False
    registry = {
        "adapter_id": "A", "adapter_version": "1", "adapter_hash": "AH",
        "effector_id": "EF", "capability_ids": ["CAP"], "operation_ids": ["OP"],
        "status": "ACTIVE",
    }
    boundary = assess_execution_boundary(
        lease=result.lease,
        registry_entry=registry,
        executor_instance_id="EX",
        capability_instance_id="CI",
        capability_id="CAP",
        operation_id="OP",
        invocation_request_hash="IH",
        effective_execution_scope_hash="SH",
        now_iso=(NOW + timedelta(seconds=2)).isoformat(),
    )
    assert boundary.status == "EXECUTION_NOT_STARTED"
    assert issuer.validate_for_handoff(
        lease, audience="A", executor_id="EX", capability_instance_id="CI",
        operation_id="OP", target_binding={"id": "T"}, now=NOW + timedelta(seconds=2)
    ) == "LEASE_REPLAY"


def test_degradation_second_handoff_blocked(tmp_path):
    _, reservation, _, _, lease, projector = setup_env(tmp_path)
    assert call(projector, lease, reservation).status == "HANDOFF_PROJECTED"
    second = call(projector, lease, reservation)
    assert second.status == "HANDOFF_BLOCKED"
    assert second.lease is None


def test_degradation_revoked_authorization_blocked(tmp_path):
    rm, reservation, _, _, lease, projector = setup_env(tmp_path)
    state = rm.state("tok")
    rm.put_authorization_state(
        AuthorizationUseState(
            state.token_id, state.max_uses, state.committed_uses, state.reserved_uses,
            state.state_version, True, state.expired, state.indeterminate
        )
    )
    result = call(projector, lease, reservation)
    assert result.status == "HANDOFF_BLOCKED"
    assert result.reason == "authorization_revoked"


def test_degradation_noncurrent_durable_reservation_blocked(tmp_path):
    _, reservation, journal, _, lease, projector = setup_env(tmp_path)
    journal.append({"type": "EXECUTION_STARTED", "reservation_id": reservation["reservation_id"]})
    result = call(projector, lease, reservation)
    assert result.status == "HANDOFF_BLOCKED"
    assert result.reason == "reservation_not_current"


def test_degradation_binding_drift_blocked(tmp_path):
    _, reservation, _, _, lease, projector = setup_env(tmp_path)
    bad = dict(reservation)
    bad["target_binding"] = {"id": "OTHER"}
    result = call(projector, lease, bad)
    assert result.status == "HANDOFF_BLOCKED"
    assert result.reason == "target_binding_mismatch"


def test_concurrent_handoff_exactly_one_projection(tmp_path):
    _, reservation, _, _, lease, projector = setup_env(tmp_path)
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda _: call(projector, lease, reservation), range(24)))
    assert sum(x.status == "HANDOFF_PROJECTED" for x in results) == 1
    assert sum(x.status == "HANDOFF_BLOCKED" for x in results) == 23


def test_non_regression_no_input_mutation(tmp_path):
    _, reservation, _, _, lease, projector = setup_env(tmp_path)
    before_reservation = dict(reservation)
    before_lease = dict(lease)
    call(projector, lease, reservation)
    assert reservation == before_reservation
    assert lease == before_lease
