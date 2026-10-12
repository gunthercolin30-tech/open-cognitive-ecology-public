def criteria():
    return {
      "schema_version":"P006-1","experiment_id":"exp-alpha",
      "decision_set":["GO","GO_WITH_CHANGES","RETHINK","STOP_COMPONENT"],
      "conditions":[
        {"id":"needs_change","description":"bounded defect requiring correction","expected":True,"severity":"CHANGE"},
        {"id":"confidence_collapse","description":"evidence invalidates central assumption","expected":True,"severity":"RETHINK"},
        {"id":"hard_safety_failure","description":"higher-order constraint violated","expected":True,"severity":"STOP"},
      ],
    }
def observations(criteria_hash, campaign=None, **values):
    base={"needs_change":False,"confidence_collapse":False,"hard_safety_failure":False}
    base.update(values)
    return {"experiment_id":"exp-alpha","criteria_hash":criteria_hash,"values":base,"campaign":campaign,
            "provenance":{"source":"test"},"configuration":{"campaign":"fixture"}}
