from math import isfinite

LEVELS = tuple((f"M{i}", name) for i, name in enumerate((
    "assumed_problem","confirmed_pain","real_data_or_problem","accepted_pilot",
    "measured_value","payment","renewal","second_paying_customer",
    "repeatable_sale","scalable_channel")))
INDEX = {level:i for i,(level,_) in enumerate(LEVELS)}
EXTERNAL = frozenset(f"M{i}" for i in range(1,10))

class ProductMarketEvidenceLadder:
    def __init__(self, confidence_threshold=0.50):
        if isinstance(confidence_threshold,bool) or not isinstance(confidence_threshold,(int,float)):
            raise ValueError("confidence_threshold must be numeric")
        if not isfinite(float(confidence_threshold)) or not 0 <= float(confidence_threshold) <= 1:
            raise ValueError("confidence_threshold out of range")
        self.confidence_threshold=float(confidence_threshold)

    @staticmethod
    def _confidence(v):
        return not isinstance(v,bool) and isinstance(v,(int,float)) and isfinite(float(v)) and 0 <= float(v) <= 1

    @staticmethod
    def _refs(v):
        return isinstance(v,list) and bool(v) and all(isinstance(x,str) and x.strip() for x in v)

    @staticmethod
    def _valid_external_evidence(v, refs):
        if not isinstance(v,dict):
            return False
        required=("origin_type","origin_id","observed_at","artifact_ref")
        if not all(isinstance(v.get(k),str) and v[k].strip() for k in required):
            return False
        if v["origin_type"].strip().lower() in {"oce_internal","internal","self","synthetic","test_fixture_untrusted"}:
            return False
        return v["artifact_ref"].strip() in {x.strip() for x in refs}

    def evaluate(self,payload):
        if not isinstance(payload,dict): raise ValueError("payload must be mapping")
        market_id=payload.get("market_id")
        claimed=payload.get("claimed_level")
        evidence=payload.get("market_evidence")
        if not isinstance(market_id,str) or not market_id.strip(): raise ValueError("market_id required")
        if claimed not in INDEX: raise ValueError("claimed_level must be M0..M9")
        if not isinstance(evidence,dict): raise ValueError("market_evidence required")
        if not isinstance(payload.get("provenance"),dict) or not payload["provenance"]: raise ValueError("provenance required")
        if not isinstance(payload.get("configuration"),dict) or not payload["configuration"]: raise ValueError("configuration required")
        if not isinstance(payload.get("dependencies"),list): raise ValueError("dependencies list required")
        rows=[]; cumulative=True; highest=None; external_signal=False
        for level,meaning in LEVELS:
            item=evidence.get(level)
            if not isinstance(item,dict):
                state,reason="UNKNOWN","market_evidence_missing"
            else:
                sat=item.get("satisfied"); conf=item.get("confidence"); refs=item.get("evidence_refs")
                source=item.get("source"); refutations=item.get("refutation_refs",[])
                external_evidence=item.get("external_evidence")
                if not isinstance(sat,bool): state,reason="INVALID","satisfied_must_be_boolean"
                elif not self._confidence(conf): state,reason="UNKNOWN","confidence_missing_or_invalid"
                elif float(conf) < self.confidence_threshold: state,reason="UNKNOWN","low_confidence"
                elif not self._refs(refs): state,reason="UNKNOWN","evidence_refs_missing"
                elif not isinstance(refutations,list) or not all(isinstance(x,str) and x.strip() for x in refutations):
                    state,reason="INVALID","refutation_refs_invalid"
                elif refutations: state,reason="NOT_SUPPORTED","explicit_refutation_present"
                elif any(x.strip()==f"market_claim:{market_id}" for x in refs):
                    state,reason="NOT_SUPPORTED","self_support_forbidden"
                elif level in EXTERNAL and source!="external":
                    state,reason="NOT_SUPPORTED","external_market_signal_required"
                elif level in EXTERNAL and not self._valid_external_evidence(external_evidence, refs):
                    state,reason="UNKNOWN","external_evidence_provenance_required"
                elif sat: state,reason="SUPPORTED","market_evidence_corresponds"
                else: state,reason="NOT_SUPPORTED","market_evidence_falsifies_or_fails"
            attained=cumulative and state=="SUPPORTED"
            if attained:
                highest=level
                if level in EXTERNAL: external_signal=True
            else: cumulative=False
            rows.append({"level":level,"meaning":meaning,"state":state,"reason":reason,"attained":attained})
        hi=INDEX[highest] if highest is not None else -1
        return {"canonical_id":"P005","market_id":market_id,"claimed_level":claimed,
                "highest_attained_level":highest,"claim_authorized":highest is not None and INDEX[claimed] <= hi,
                "market_priority_authorized":bool(external_signal and hi >= INDEX["M1"]),
                "external_market_signal_present":external_signal,"levels":rows,
                "functional_conclusion_only":True,"phenomenology_undetermined":True}
