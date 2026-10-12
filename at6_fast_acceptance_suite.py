#!/usr/bin/env python3
"""Fast acceptance suite for AT6 unexpected_prediction_detector."""
from __future__ import annotations
import py_compile
from pathlib import Path
from ontology.unexpected_prediction_detector import UnexpectedPredictionDetector
ROOT=Path.home()/"open-cognitive-ecology"; MODULE=ROOT/"ontology"/"unexpected_prediction_detector.py"
READY_CONTEXT={"falsification_protocols":[
 {"protocol_id":"p1","prediction_id":"rf_topology_nonclosure","category":"topological","prediction":"RF* predicts non-closure topological invariance where classical functional role accounts predict convergence.","protocol_scores":{"discriminative_power":0.86,"measurement_readiness":0.75,"falsifiability_score":0.8},"signature_id":"s1"},
 {"protocol_id":"p2","prediction_id":"rf_structural_expected","category":"structural","prediction":"RF* predicts reference frame structural preservation under controlled perturbation.","protocol_scores":{"discriminative_power":0.55,"measurement_readiness":0.7,"falsifiability_score":0.65},"signature_id":"s2"},
]}
def guards(r):
    assert r["functional_conclusion_only"] is True; assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"]: assert r[k] is False; assert r["epistemic_guards"][k] is False
    assert r["epistemic_guards"]["functional_conclusion_only"] is True
def test_compile():
    c=Path("/private/tmp/oce_at6_unexpected_prediction_detector.pyc"); c.parent.mkdir(parents=True,exist_ok=True); py_compile.compile(str(MODULE),cfile=str(c),doraise=True)
def test_ready_context():
    r=UnexpectedPredictionDetector().step(inputs=READY_CONTEXT,persist=False)
    assert r["primitive"]=="UNEXPECTED_PREDICTION_DETECTOR"; assert r["step"]=="AT6"; assert r["status"]=="UNEXPECTED_PREDICTIONS_DETECTED"
    assert r["prediction_count"]>=2; assert r["unexpected_prediction_count"]>=2; assert isinstance(r["unexpected_predictions"],list)
    assert any(x["classification"] in {"new","counter_intuitive","surprising"} for x in r["unexpected_predictions"])
    for x in r["unexpected_predictions"]: assert x["claim_scope"]=="functional_prediction_only"; assert 0.0<=x["surprise_score"]<=1.0
    guards(r)
def test_degradation_context():
    r=UnexpectedPredictionDetector().step(inputs={},persist=False)
    assert r["step"]=="AT6"; assert r["unexpected_prediction_count"]>=1; assert r["persisted"] is False; guards(r)
def test_summary():
    r=UnexpectedPredictionDetector().step(inputs=READY_CONTEXT,persist=False); s=r["unexpected_prediction_summary"]
    assert s["unexpected_prediction_count"]==r["unexpected_prediction_count"]; assert 0.0<=s["mean_surprise_score"]<=1.0; assert isinstance(s["classification_counts"],dict)
def main():
    test_compile(); test_ready_context(); test_degradation_context(); test_summary(); print("AT6_FAST_ACCEPTANCE_ALL_OK")
if __name__=="__main__": main()
