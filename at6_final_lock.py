#!/usr/bin/env python3
"""Codex-compliant final lock for AT6."""
from __future__ import annotations
from ontology.unexpected_prediction_detector import UnexpectedPredictionDetector
READY_OR_SYNTHETIC_CONTEXT={"falsification_protocols":[{"protocol_id":"lock_p1","prediction_id":"rf_collective_surprise","category":"collective","prediction":"RF* predicts surprising collective governance continuity under partial node disruption.","protocol_scores":{"discriminative_power":0.8,"measurement_readiness":0.7,"falsifiability_score":0.78},"signature_id":"lock_s1"}]}
def main():
    r=UnexpectedPredictionDetector().step(inputs=READY_OR_SYNTHETIC_CONTEXT,persist=False)
    assert r["primitive"]=="UNEXPECTED_PREDICTION_DETECTOR"; assert r["step"]=="AT6"; assert r["status"]=="UNEXPECTED_PREDICTIONS_DETECTED"
    assert r["unexpected_prediction_count"]>=1; assert isinstance(r["unexpected_predictions"],list)
    assert r["functional_conclusion_only"] is True; assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven"]: assert r[k] is False
    print("AT6_FINAL_LOCK_OK")
if __name__=="__main__": main()
