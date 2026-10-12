#!/usr/bin/env python3
from __future__ import annotations
from math import isfinite
from typing import Any, Mapping
CANONICAL_ID="P003"; VERSION="1.0.0"
INV={"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def num(v,n,nonnegative=False):
    if isinstance(v,bool): raise ValueError(f"{n}: numeric required")
    try: x=float(v)
    except (TypeError,ValueError): raise ValueError(f"{n}: finite numeric required") from None
    if not isfinite(x) or (nonnegative and x<0): raise ValueError(f"{n}: invalid numeric value")
    return x
def text(v,n):
    if not isinstance(v,str) or not v.strip(): raise ValueError(f"{n}: non-empty string required")
    return v.strip()
def mapping(v,n):
    if not isinstance(v,Mapping) or not v: raise ValueError(f"{n}: non-empty mapping required")
    return dict(v)
class DevelopmentEvidenceRoadmap:
    def evaluate(self,milestone):
        if not isinstance(milestone,Mapping): raise ValueError("milestone: mapping required")
        r=dict(milestone)
        mid=text(r.get("milestone_id"),"milestone_id"); prop=text(r.get("expected_property"),"expected_property"); output=text(r.get("measurable_output"),"measurable_output")
        evidence=mapping(r.get("evidence"),"evidence"); baseline=mapping(r.get("baseline"),"baseline"); provenance=mapping(r.get("provenance"),"provenance"); resources=mapping(r.get("resources"),"resources")
        deps=r.get("dependencies")
        if not isinstance(deps,(list,tuple)) or not deps: raise ValueError("dependencies: non-empty list required")
        deps=sorted(set(text(x,"dependencies") for x in deps))
        ev=num(evidence.get("measured_value"),"evidence.measured_value"); bv=num(baseline.get("measured_value"),"baseline.measured_value")
        hh=num(resources.get("human_hours"),"resources.human_hours",True)
        ub=num(r.get("uncertainty_before"),"uncertainty_before",True); ua=num(r.get("uncertainty_after"),"uncertainty_after",True)
        if ub>1 or ua>1: raise ValueError("uncertainty values must be in [0,1]")
        nr=r.get("non_regression")
        if not isinstance(nr,bool): raise ValueError("non_regression: boolean required")
        conf=r.get("confidence")
        if conf is None: cs="UNKNOWN"
        else:
            c=num(conf,"confidence")
            if not 0<=c<=1: raise ValueError("confidence must be in [0,1]")
            cs="LOW" if c<.5 else "SUFFICIENT"
        rule=r.get("comparison","higher_is_better")
        if rule=="higher_is_better": bs=ev>bv
        elif rule=="lower_is_better": bs=ev<bv
        elif rule=="equal_or_better": bs=ev>=bv
        else: raise ValueError("comparison: unsupported rule")
        eliminated=ub-ua; efficiency=(eliminated/hh if hh>0 else None)
        reasons=[]
        if not bs: reasons.append("BASELINE_NOT_SATISFIED")
        if not nr: reasons.append("NON_REGRESSION_FAILED")
        if eliminated<=0: reasons.append("NO_IMPORTANT_UNCERTAINTY_ELIMINATED")
        if efficiency is None: reasons.append("HUMAN_HOURS_NOT_MEASURABLE")
        if cs=="UNKNOWN": reasons.append("CONFIDENCE_UNKNOWN")
        if cs=="LOW": reasons.append("CONFIDENCE_LOW")
        decision="UNKNOWN" if cs in ("UNKNOWN","LOW") or efficiency is None else ("REJECTED" if reasons else "ACCEPTED")
        return {"canonical_id":CANONICAL_ID,"version":VERSION,"milestone_id":mid,"expected_property":prop,"measurable_output":output,"evidence":evidence,"baseline":baseline,"baseline_satisfied":bs,"provenance":provenance,"resources":resources,"dependencies":deps,"non_regression":nr,"uncertainty_before":ub,"uncertainty_after":ua,"important_uncertainty_eliminated":eliminated,"human_hours":hh,"uncertainty_eliminated_per_human_hour":efficiency,"confidence_state":cs,"decision":decision,"reasons":sorted(reasons),**INV}
