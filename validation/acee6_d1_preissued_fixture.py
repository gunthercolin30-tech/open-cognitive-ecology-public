"""Test-only explicit FIFO of preissued governed filesystem contexts.

The caller supplies the complete sequence BEFORE executing the test subject.
Never mint authority from a request. Never use this in production.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Tuple

SLOTS = {
    'FS_CREATE_DIR': ('p162g6_c02_parent_create', 'p162g6_index1_backup_parent_create',
                      'p162g6_index2_journal_parent_create', 'p162g6_c02_candidate_parent_create',
                      'p162g6_index2_inventory_parent_create'),
    'FS_WRITE_REPLACE_BYTES': ('p162g6_c02_write_replace', 'p162g6_c02_candidate_write_replace',
                               'p162g6_index2_inventory_restore'),
    'FS_APPEND_BYTES': ('p162g6_index2_journal_append',),
    'FS_COPY2': ('p162g6_index1_backup_copy2',),
    'FS_REMOVE_FILE': ('p162g6_index2_inventory_remove', 'p162g6_index2_target_remove'),
}

@dataclass(frozen=True)
class ExpectedEffect:
    operation: str
    target: Path
    source: Optional[Path] = None

class PreissuedD1Fixture:
    def __init__(self, root: Path, expected: Tuple[ExpectedEffect, ...]):
        from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
        from ontology.governed_filesystem_effector import GovernedFilesystemEffector
        from ontology.scoped_handle_broker import ScopedHandleBroker
        self.root = Path(root).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError('root_not_directory')
        if not isinstance(expected, tuple) or not expected:
            raise ValueError('explicit_nonempty_expected_effects_required')
        self._expected = []
        self._next = 0
        broker = ScopedHandleBroker()
        effector = GovernedFilesystemEffector(root_registry={'repo': str(self.root)}, handle_broker=broker)
        adapter = 'acee6-d1-test-only'
        effector_id = 'p162g6-filesystem-effector'
        now = datetime.now(timezone.utc)
        for i, item in enumerate(expected):
            if not isinstance(item, ExpectedEffect) or item.operation not in SLOTS:
                raise ValueError('unsupported_explicit_effect')
            target = Path(item.target).resolve()
            try:
                target_rel = target.relative_to(self.root).as_posix()
            except ValueError as exc:
                raise ValueError('target_outside_test_root') from exc
            source = Path(item.source).resolve() if item.source is not None else None
            if item.operation == 'FS_COPY2' and source is None:
                raise ValueError('copy_source_required')
            if item.operation != 'FS_COPY2' and source is not None:
                raise ValueError('source_not_allowed_for_operation')
            if source is not None:
                try:
                    source_rel = source.relative_to(self.root).as_posix()
                except ValueError as exc:
                    raise ValueError('source_outside_test_root') from exc
                binding = {'source': 'filesystem://repo/' + source_rel,
                           'destination': 'filesystem://repo/' + target_rel}
            else:
                binding = 'filesystem://repo/' + target_rel
            claim = SimpleNamespace(lease_id='d1-lease-%d' % i,
                                    reservation_id='d1-res-%d' % i,
                                    claim_hash='d1-claim-%d' % i, adapter_id=adapter)
            lease = {'lease_id': claim.lease_id, 'reservation_id': claim.reservation_id,
                     'operation_id': item.operation,
                     'expires_at': (now + timedelta(minutes=10)).isoformat().replace('+00:00','Z')}
            scope = {'ambient_authority': False, 'child_inheritance': False, 'transferable': False}
            issued = broker.issue(claim=claim, lease=lease,
                                  registry_entry={'adapter_id': adapter, 'effector_id': effector_id},
                                  requested_scope=scope, authorized_scope=scope,
                                  target_binding=binding, audience=adapter,
                                  now_iso=now.isoformat().replace('+00:00','Z'))
            if issued.get('status') != 'HANDLE_ISSUED':
                raise RuntimeError('test_handle_preissuance_failed:' + str(issued.get('reason')))
            slots = {slot: [issued['handle']] for slot in SLOTS[item.operation]}
            context = GovernedFilesystemEffectContext(slots=slots, effector=effector,
                      root_id='repo', root_path=self.root, adapter_id=adapter,
                      effector_id=effector_id, source_root_id='repo', source_root_path=self.root)
            self._expected.append((item.operation, target, source, context))

    def __call__(self, operation, target, source=None):
        if self._next >= len(self._expected):
            raise RuntimeError('no_preissued_context_remaining')
        exp_op, exp_target, exp_source, context = self._expected[self._next]
        actual_source = Path(source).resolve() if source is not None else None
        if actual_source is not None and actual_source != exp_source:
            raise RuntimeError('preissued_context_source_mismatch')
        if (operation, Path(target).resolve()) != (exp_op, exp_target):
            raise RuntimeError('preissued_context_sequence_mismatch')
        self._next += 1
        return context

    def assert_exhausted(self):
        if self._next != len(self._expected):
            raise AssertionError('unused_preissued_contexts')
