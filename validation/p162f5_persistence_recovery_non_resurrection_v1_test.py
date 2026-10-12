import json
from ontology.reservation_recovery_manager import ReservationRecoveryJournal,ASSESSMENTS

def j(tmp_path): return ReservationRecoveryJournal(tmp_path/"journal.jsonl")

def test_assessment_catalog():
 assert set(ASSESSMENTS)=={"CONFIRMED_UNUSED","CONFIRMED_USED","LIKELY_USED_REVIEW_REQUIRED","INDETERMINATE"}

def test_crash_before_commit_creates_no_right(tmp_path):
 r=j(tmp_path).reconstruct("r")
 assert r["state"]=="AVAILABLE" and r["assessment"]=="CONFIRMED_UNUSED"

def test_committed_reservation_survives_restart(tmp_path):
 p=tmp_path/"j"; a=ReservationRecoveryJournal(p); a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 b=ReservationRecoveryJournal(p); r=b.reconstruct("r")
 assert r["state"]=="RESERVED" and r["assessment"]=="INDETERMINATE"

def test_confirmed_effect_is_used(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});a.append({"type":"EXECUTION_STARTED","reservation_id":"r"});a.append({"type":"EXECUTION_CONFIRMED","reservation_id":"r"})
 r=a.reconstruct("r");assert r["state"]=="CONSUMED" and r["assessment"]=="CONFIRMED_USED"

def test_started_without_receipt_not_unused(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});a.append({"type":"EXECUTION_STARTED","reservation_id":"r"})
 r=a.reconstruct("r");assert r["assessment"]=="LIKELY_USED_REVIEW_REQUIRED" and r["assessment"]!="CONFIRMED_UNUSED"

def test_explicit_indeterminate_blocks_blind_retry(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});a.append({"type":"EFFECT_INDETERMINATE","reservation_id":"r"})
 r=a.idempotent_recover("r");assert r["state"]=="INDETERMINATE" and r["assessment"]=="INDETERMINATE"

def test_old_available_backup_cannot_resurrect_reserved(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 r=a.reconstruct("r",{"state":"AVAILABLE"});assert r["state"]=="RESERVED"

def test_old_available_backup_cannot_resurrect_consumed(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});a.append({"type":"EXECUTION_CONFIRMED","reservation_id":"r"})
 r=a.reconstruct("r",{"state":"AVAILABLE"});assert r["state"]=="CONSUMED" and r["assessment"]=="CONFIRMED_USED"

def test_higher_risk_backup_is_preserved(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 r=a.reconstruct("r",{"state":"INDETERMINATE"});assert r["state"]=="INDETERMINATE" and r["assessment"]=="INDETERMINATE"

def test_cancellation_after_possible_effect_preserves_history(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"});a.append({"type":"CANCEL_AFTER_POSSIBLE_EFFECT","reservation_id":"r"})
 r=a.reconstruct("r");assert r["state"]=="INDETERMINATE"

def test_truncated_or_corrupt_journal_fails_closed(tmp_path):
 p=tmp_path/"j";a=ReservationRecoveryJournal(p);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 with p.open("a",encoding="utf-8") as f:f.write("{broken")
 r=ReservationRecoveryJournal(p).reconstruct("r");assert r["state"]=="INDETERMINATE" and r["assessment"]=="INDETERMINATE"

def test_hash_chain_tamper_fails_closed(tmp_path):
 p=tmp_path/"j";a=ReservationRecoveryJournal(p);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 d=json.loads(p.read_text());d["reservation_id"]="other";p.write_text(json.dumps(d)+"\n")
 r=ReservationRecoveryJournal(p).reconstruct("r");assert r["state"]=="INDETERMINATE"

def test_recovery_is_deterministic_and_non_effecting(tmp_path):
 a=j(tmp_path);a.append({"type":"RESERVATION_COMMITTED","reservation_id":"r"})
 x=a.reconstruct("r");y=ReservationRecoveryJournal(a.path).reconstruct("r")
 assert x==y and x["authorization_created"] is False and x["capability_accessed"] is False and x["execution_performed"] is False
 assert not hasattr(a,"execute") and not hasattr(a,"dispatch")
