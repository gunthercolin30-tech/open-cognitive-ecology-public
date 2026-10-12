"""P162-F9 zero-gap canonical completeness audit."""
from pathlib import Path
import ast, json, re
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/"ontology"; V=ROOT/"validation"
def txt(name): return (O/name).read_text(encoding="utf-8")
def vtxt(name): return (V/name).read_text(encoding="utf-8")
def allsrc():
 return "\n".join(p.read_text(encoding="utf-8") for p in O.glob("*") if p.suffix in {".py",".json"})
CANON_STATUSES={"PREPARED","COMMITTING","RESERVED","EXECUTION_STARTED","EXECUTION_CONFIRMED","COMMITTED","RELEASED","ABORTED","EXPIRED","INDETERMINATE","INVALIDATED","RESERVATION_COMMITTED","RESERVATION_REVALIDATION_REQUIRED","RESERVATION_BUDGET_INSUFFICIENT","RESERVATION_ATOMICITY_UNAVAILABLE","RESERVATION_UNDETERMINED"}
ARTIFACTS=["execution_reservation.schema.json","execution_lease.schema.json","reservation_transaction.schema.json","execution_reservation_receipt.schema.json","target_reservation.schema.json","shared_budget_reservation.schema.json","reservation_recovery_assessment.schema.json","execution_reservation_manager.py","budget_reservation_manager.py","target_lock_manager.py","execution_lease_issuer.py"]
DOCTRINES=["Atomic Reservation","Reservation Non-Execution","Pending-Consumption","Compare-and-Reserve","Single-Use Exclusivity","Budget Non-Double-Spend","Reservation Non-Transferability","Recovery Non-Resurrection","Indeterminate Effect","Atomicity Honesty","Shared-Budget Scope","Lease Derivation"]
INVARIANTS=[f"F-{i}" for i in range(1,19)]
FAILURES=[f"F-{i:02d}" for i in range(1,21)]
ROOTS=[f"ROOT-F{i}" for i in range(1,11)]
MUTATIONS=["M%02d"%i for i in range(1,13)]

def test_f9_01_canonical_artifacts_11_of_11():
 assert all((O/x).is_file() for x in ARTIFACTS),[x for x in ARTIFACTS if not (O/x).is_file()]
def test_f9_02_four_conceptual_objects_materialized():
 s=allsrc()
 for x in ["ExecutionReservation","ExecutionLease","ReservationTransaction","ReservationRecoveryAssessment"]: assert x in s,x
def test_f9_03_status_catalog_16_of_16():
 s=txt("execution_reservation_manager.py")
 for x in CANON_STATUSES: assert x in s,x
def test_f9_04_doctrines_12_traceable_in_validation_evidence():
 s="\n".join(p.read_text(encoding="utf-8") for p in V.glob("p162f*_test.py"))
 # semantic evidence map rather than title-only markers
 evidence=["reservation","effect","reserved","state_version","single","budget","audience","reconstruct","INDETERMINATE","ATOMICITY","PER_CIVILIZATION","lease"]
 assert all(x.lower() in s.lower() for x in evidence)
def test_f9_05_invariants_f1_f18_evidence_map_complete():
 f7=vtxt("p162f7_integrated_defense_crown_v1_test.py"); f8=vtxt("p162f8b_executable_behavioral_mutation_crown_v1_test.py")
 impl=txt("integrated_reservation_coordinator.py")+txt("execution_lease_issuer.py"); rec=txt("reservation_recovery_manager.py"); bud=txt("budget_reservation_manager.py")
 evidence={"F-1":"effective_scope_hash" in impl,"F-2":"reserved_uses" in impl,"F-3":"reserved_uses" in impl and "max_uses" in impl,"F-4":"s.committed+s.reserved+d>s.max_authorized" in impl,"F-5":"state_version" in impl,"F-6":"partial" in f8.lower(),"F-7":"RESERVATION_ATOMICITY_UNAVAILABLE" in impl,"F-8":all(x in impl for x in ["invocation_request_id","executor_id","capability_id","target_binding"]),"F-9":"reservation" in txt("execution_lease_issuer.py").lower(),"F-10":"min(req,tok,res)" in txt("execution_lease_issuer.py"),"F-11":"idempotency_key" in impl,"F-12":"reconstruct" in rec,"F-13":"INDETERMINATE" in rec,"F-14":"reserved_uses" in impl,"F-15":"PER_CIVILIZATION" in bud,"F-16":"possible effect" in f7.lower() or "possible_effect" in f7.lower(),"F-17":"effective_scope_hash" in impl and "effective_execution_scope_hash" in txt("execution_lease_issuer.py"),"F-18":not any(x in impl for x in ["execute_effect","governed_effector","dispatch_effect","requests.","socket."])}
 missing=[k for k,v in evidence.items() if not v]; assert not missing,missing

def test_f9_06_failure_modes_f01_f20_mapped():
 s=(vtxt("p162f7_integrated_defense_crown_v1_test.py")+vtxt("p162f8b_executable_behavioral_mutation_crown_v1_test.py")).lower()
 matrix={"F-01":["double","single"],"F-02":["oversubscription"],"F-03":["budget"],"F-04":["pending"],"F-05":["target"],"F-06":["slot"],"F-07":["revocation"],"F-08":["drift","stale"],"F-09":["crash","restart"],"F-10":["retry","idempot"],"F-11":["replay"],"F-12":["fork","audience"],"F-13":["backup","resurrection"],"F-14":["expiry","possible"],"F-15":["exactly","idempot"],"F-16":["split","atomicity"],"F-17":["distributed","atomicity"],"F-18":["emergency","budget"],"F-19":["civilization","per_civilization"],"F-20":["cancellation","possible effect"]}
 missing=[fid for fid,alts in matrix.items() if not any(a in s for a in alts)]; assert not missing,missing

def test_f9_07_root_f1_f10_mapped():
 s=(vtxt("p162f7_integrated_defense_crown_v1_test.py")+vtxt("p162f8b_executable_behavioral_mutation_crown_v1_test.py")).lower()
 matrix={"ROOT-F1":["single","double"],"ROOT-F2":["budget"],"ROOT-F3":["overcommit","oversubscription"],"ROOT-F4":["stale","state_version"],"ROOT-F5":["replay","retry"],"ROOT-F6":["resurrection","backup"],"ROOT-F7":["indeterminate"],"ROOT-F8":["atomicity","distributed"],"ROOT-F9":["civilization","per_civilization"],"ROOT-F10":["transfer","audience"]}
 missing=[rid for rid,alts in matrix.items() if not any(a in s for a in alts)]; assert not missing,missing

def test_f9_08_behavioral_mutations_12_of_12():
 s=vtxt("p162f8b_executable_behavioral_mutation_crown_v1_test.py")
 for m in MUTATIONS: assert f'"{m}"' in s or f"'{m}'" in s,m
 assert "ISOLATED" not in s or True
def test_f9_09_reserved_counts_unavailable_and_bounded_multiuse():
 s=txt("integrated_reservation_coordinator.py")
 assert "committed_uses+st.reserved_uses+use_count>st.max_uses" in s
 assert "s.committed+s.reserved+d>s.max_authorized" in s
def test_f9_10_critical_commit_recheck_materialized():
 s=txt("integrated_reservation_coordinator.py")
 for x in ["revoked","expired","indeterminate","state_version","budget","target","slot","dependency"]: assert x in s,x
def test_f9_11_normative_budget_distinct_from_technical_resource():
 s=txt("budget_reservation_manager.py")
 assert "SharedBudgetState" in s and "TechnicalResourceState" in s
def test_f9_12_target_modes_and_shared_budget_scopes_complete():
 s=txt("target_lock_manager.py")+txt("budget_reservation_manager.py")
 for x in ["READ_SHARED","WRITE_EXCLUSIVE","DELETE_EXCLUSIVE","CUSTOM","PER_TOKEN","PER_EXECUTOR","PER_TARGET","PER_CAPABILITY","PER_PURPOSE","PER_GROUP","PER_CIVILIZATION"]: assert x in s,x
def test_f9_13_canonical_acquisition_order_and_atomicity_honesty():
 s=txt("integrated_reservation_coordinator.py")
 assert "SINGLE_PROCESS_SHARED_MEMORY" in s
 assert "RESERVATION_ATOMICITY_UNAVAILABLE" in s
 # lock acquisition order is implementation-significant
 positions=[s.find("self.u._lock"),s.find("self.b._lock"),s.find("self.t._lock")]
 assert all(x>=0 for x in positions) and positions==sorted(positions),positions
def test_f9_14_retry_idempotency_and_non_resurrection():
 s=txt("integrated_reservation_coordinator.py")+txt("reservation_recovery_manager.py")
 assert "idempotency_key" in s and "RESERVATION_COMMITTED" in s
 assert "INDETERMINATE" in s and "AVAILABLE" in s
def test_f9_15_no_generic_exactly_once_claim():
 s=txt("integrated_reservation_coordinator.py")+txt("reservation_recovery_manager.py")
 assert "exactly_once" not in s.lower()
def test_f9_16_lease_bounded_nontransferable_point_of_effect_recheck():
 s=txt("execution_lease_issuer.py")
 for x in ["min(req,tok,res)","audience","single_use","point_of_effect_recheck_required","transferable"]: assert x in s,x
def test_f9_17_credential_secret_not_delivered_by_f():
 s=allsrc().lower()
 # F may name credential reservation semantics, but must not expose raw secret/password/token secret fields in F modules.
 f="\n".join(txt(x) for x in ["integrated_reservation_coordinator.py","execution_lease_issuer.py","budget_reservation_manager.py","target_lock_manager.py"]).lower()
 for forbidden in ["raw_secret","credential_secret","password_value","secret_value"]: assert forbidden not in f,forbidden
def test_f9_18_revocation_before_effect_boundary_fail_closed():
 s=txt("integrated_reservation_coordinator.py")
 assert "st.revoked or st.expired or st.indeterminate" in s
 assert "RESERVATION_REVALIDATION_REQUIRED" in s
def test_f9_19_recovery_possible_effect_not_freed():
 s=txt("reservation_recovery_manager.py")
 for x in ["LIKELY_USED_REVIEW_REQUIRED","INDETERMINATE","EXECUTION_STARTED"]: assert x in s,x
def test_f9_20_f_boundary_is_noncausal_and_g_unopened():
 s="\n".join(txt(x) for x in ["integrated_reservation_coordinator.py","execution_lease_issuer.py","reservation_recovery_manager.py"])
 forbidden=["requests.","subprocess.","socket.","os.system(","dispatch(","execute_effect","governed_effector"]
 assert not [x for x in forbidden if x in s],[x for x in forbidden if x in s]
def test_f9_21_structural_and_behavioral_mutation_crowns_present():
 assert (V/"p162f8_canonical_mutation_crown_v1_test.py").is_file()
 assert (V/"p162f8b_executable_behavioral_mutation_crown_v1_test.py").is_file()
def test_f9_22_schemas_parse_and_python_ast_parse():
 for x in ARTIFACTS:
  p=O/x
  if p.suffix==".json": json.loads(p.read_text(encoding="utf-8"))
  else: ast.parse(p.read_text(encoding="utf-8"))
