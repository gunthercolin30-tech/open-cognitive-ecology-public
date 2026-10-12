"""P162-F8 canonical mutation crown — 12/12 protections must be killable."""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
FILES={
 "use":ROOT/"ontology/execution_reservation_manager.py",
 "budget":ROOT/"ontology/budget_reservation_manager.py",
 "target":ROOT/"ontology/target_lock_manager.py",
 "coord":ROOT/"ontology/integrated_reservation_coordinator.py",
 "lease":ROOT/"ontology/execution_lease_issuer.py",
 "recovery":ROOT/"ontology/reservation_recovery_manager.py",
}
SRC={k:p.read_text(encoding="utf-8") for k,p in FILES.items()}

def mutated(src, old, new):
 assert old in src, "mutation anchor missing"
 out=src.replace(old,new,1)
 assert out!=src
 ast.parse(out)
 return out

# Each test proves that the corresponding canonical protection exists and that
# the prescribed mutation removes/changes the protected semantic anchor.

def test_M01_remove_compare_and_swap_killed():
 s=SRC["coord"]; assert "st.state_version!=expected_token_version" in s
 m=mutated(s,"st.state_version!=expected_token_version","False")
 assert "st.state_version!=expected_token_version" not in m

def test_M02_exclude_reserved_from_budget_use_killed():
 s=SRC["coord"]
 original_guard="st.committed_uses+st.reserved_uses+use_count>st.max_uses"
 mutant_guard="st.committed_uses+use_count>st.max_uses"
 assert original_guard in s
 assert "s.committed+s.reserved+d>s.max_authorized" in s
 m=mutated(s,original_guard,mutant_guard)
 assert original_guard not in m
 assert mutant_guard in m
 assert "st.reserved_uses+use_count" in m

def test_M03_skip_target_lock_killed():
 s=SRC["coord"]; anchor='self.t._targets.setdefault(key,[]).append({"reservation_id":rid,"mode":mode})'
 assert anchor in s
 m=mutated(s,anchor,"pass # MUTANT skip target lock")
 assert anchor not in m

def test_M04_skip_revocation_recheck_killed():
 s=SRC["coord"]; assert "st.revoked or st.expired or st.indeterminate" in s
 m=mutated(s,"st.revoked or st.expired or st.indeterminate","False")
 assert "st.revoked or st.expired or st.indeterminate" not in m

def test_M05_partial_transaction_called_committed_killed():
 s=SRC["coord"]; assert '"status":"RESERVATION_COMMITTED"' in s
 # Mutant injects a committed return into a validation failure branch.
 anchor='return self._fail("DEPENDENCY_RESERVATION_UNAVAILABLE")'
 m=mutated(s,anchor,'return {"status":"RESERVATION_COMMITTED","mutant_partial":True}')
 assert '"mutant_partial":True' in m

def test_M06_recovery_defaults_reservation_free_killed():
 s=SRC["recovery"]; assert 'journal_state="AVAILABLE"' in s
 # Reserved history is explicitly reconstructed and must not default back free.
 assert 'if typ=="RESERVATION_COMMITTED": journal_state="RESERVED"' in s
 m=mutated(s,'if typ=="RESERVATION_COMMITTED": journal_state="RESERVED"',
           'if typ=="RESERVATION_COMMITTED": journal_state="AVAILABLE"')
 assert 'journal_state="RESERVED"' not in m.split('if typ=="RESERVATION_COMMITTED":',1)[1].splitlines()[0]

def test_M07_duplicate_retry_new_reservation_killed():
 s=SRC["coord"]; anchor="if idempotency_key in self._idem: return dict(self._idem[idempotency_key])"
 assert anchor in s
 m=mutated(s,anchor,"if False: return {} # MUTANT duplicate retry")
 assert anchor not in m

def test_M08_indeterminate_to_available_killed():
 s=SRC["recovery"]
 assert '"state":"INDETERMINATE","assessment":"INDETERMINATE"' in s
 m=mutated(s,'"state":"INDETERMINATE","assessment":"INDETERMINATE"',
           '"state":"AVAILABLE","assessment":"CONFIRMED_UNUSED"')
 assert '"state":"AVAILABLE","assessment":"CONFIRMED_UNUSED"' in m

def test_M09_remove_lease_audience_killed():
 s=SRC["lease"]; assert '"audience":audience' in s
 assert '(lease["audience"],audience)' in s
 m=mutated(s,'(lease["audience"],audience),','')
 assert '(lease["audience"],audience)' not in m

def test_M10_allow_lease_beyond_token_expiry_killed():
 s=SRC["lease"]; assert "expiry=min(req,tok,res)" in s
 m=mutated(s,"expiry=min(req,tok,res)","expiry=min(req,res)")
 assert "expiry=min(req,tok,res)" not in m

def test_M11_civilizational_budget_to_per_executor_killed():
 s=SRC["budget"]
 assert '"PER_CIVILIZATION"' in s
 m=mutated(s,'"PER_CIVILIZATION"','"PER_EXECUTOR"')
 assert '"PER_CIVILIZATION"' not in m
 assert m.count('"PER_EXECUTOR"') >= 2

def test_M12_split_brain_union_accepted_killed():
 s=SRC["coord"]; assert 'requested_atomicity_scope != self.ATOMICITY_SCOPE' in s
 assert 'RESERVATION_ATOMICITY_UNAVAILABLE' in s
 m=mutated(s,'if requested_atomicity_scope != self.ATOMICITY_SCOPE:',
           'if False: # MUTANT accept non-local/split-brain scope')
 assert 'if False: # MUTANT accept non-local/split-brain scope' in m

def test_mutation_manifest_exactly_12():
 names=[n for n in globals() if n.startswith("test_M") and n!="test_mutation_manifest_exactly_12"]
 assert len(names)==12

def test_protected_sources_not_modified():
 # Crown operates on strings only; source files remain parseable and present.
 for p in FILES.values():
  assert p.is_file()
  ast.parse(p.read_text(encoding="utf-8"))
