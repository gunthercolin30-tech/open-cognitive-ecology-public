from ontology.bifurcation_detector import BifurcationDetector
def obs(i,a,b,c,q=.95): return {"timestamp_utc": f"2027-01-{i:02d}T00:00:00Z", "state_vector":{"a":a,"b":b,"c":c}, "data_quality":q}
def main():
    e=BifurcationDetector()
    assert e.step(inputs={},persist=False)["bifurcation_status"]=="FUNCTIONAL_BIFURCATION_UNDETERMINED"
    stable=[obs(i,.5+.01*(i%2),.5,.5) for i in range(1,8)]
    assert e.step(inputs={"observations":stable},persist=False)["bifurcation_status"]=="NO_DEVELOPMENTAL_TRANSITION"
    low=[obs(i,.8 if i<4 else .2,.8 if i<4 else .2,.8 if i<4 else .2,q=.1) for i in range(1,8)]
    assert e.step(inputs={"observations":low},persist=False)["bifurcation_status"]=="FUNCTIONAL_BIFURCATION_UNDETERMINED"
    invalid=[obs(3,.8,.8,.8),obs(1,.8,.8,.8),obs(2,.2,.2,.2),obs(4,.2,.2,.2),obs(5,.2,.2,.2),obs(6,.2,.2,.2)]
    assert e.step(inputs={"observations":invalid},persist=False)["bifurcation_status"]=="FUNCTIONAL_BIFURCATION_UNDETERMINED"
    fluct=[obs(1,.5,.5,.5),obs(2,.5,.5,.5),obs(3,.9,.1,.9),obs(4,.5,.5,.5),obs(5,.5,.5,.5),obs(6,.5,.5,.5)]
    assert e.step(inputs={"observations":fluct},persist=False)["bifurcation_status"] not in {"FUNCTIONAL_BIFURCATION_DETECTED","FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED"}
    progressive=[obs(i,.2+.09*i,.3+.07*i,.4+.05*i) for i in range(1,8)]
    assert e.step(inputs={"observations":progressive},persist=False)["bifurcation_status"] in {"FUNCTIONAL_PROGRESSIVE_TRANSITION_DETECTED","NO_DEVELOPMENTAL_TRANSITION","FUNCTIONAL_FLUCTUATION_DETECTED"}
    print("AV4_DEGRADATION_OK")
if __name__=="__main__": main()
