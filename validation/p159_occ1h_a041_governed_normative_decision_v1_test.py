from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation_artifacts/p159/occ1h/a041/a041_governed_normative_decision_v1.json'
def load(): return json.loads(P.read_text(encoding='utf-8'))
def test_a041_human_governed_decision_exact():
 d=load(); assert d['human_confirmation']['confirmed'] is True; assert d['authority_id']=='OCE-HUMAN-INITIAL-001'; assert len(d['normative_decisions'])==4
def test_a041_sunset_semantics_fail_closed_and_historical():
 d=load(); n=d['normative_decisions']; assert n['D2_sunset_parameter']['field']=='sunset_at'; assert n['D3_authoritative_time_reference']['dependent_actions_fail_closed_while_temporal_inconsistency_unresolved'] is True; assert n['D4_post_sunset_effect']['prospective_normative_effect']=='INACTIVE'; assert n['D4_post_sunset_effect']['historical_records_immutable'] is True
def test_a041_decision_does_not_self_implement():
 d=load(); b=d['boundaries']; assert b['decision_distinct_from_activation']; assert b['decision_distinct_from_implementation']; assert not b['canonical_source_modified']; assert not b['runtime_modified']; assert not b['rrp21_opened']; assert not b['rrp22_opened']; assert not b['occ1h_closed']; assert not b['p160_opened']
