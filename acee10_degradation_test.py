from ontology.acee_selection_policy import AceeSelectionPolicy
def main():
 r=AceeSelectionPolicy().step(inputs={},persist=False)
 assert r["selection_status"]=="ACEE_SELECTION_DECISION_DEGRADED" and r["selection_decision_ready"] is False and r["decision"]=="repeat"
 assert r["blocking_reasons"]
 print("ACEE10_DEGRADATION_OK")
if __name__=="__main__": main()
