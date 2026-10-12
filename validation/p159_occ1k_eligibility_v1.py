from ontology import occ_p159_final_lock as fl
def main(filesystem_effect_context=None):
 r=fl.root();x=fl.evaluate_eligibility(r);fl.atomic_json(r/fl.ELIG_REL,x,filesystem_effect_context);print("P159_OCC1K_ELIGIBILITY_"+x["status"]);print("checks=%d/%d"%(sum(v is True for v in x["checks"].values()),len(x["checks"])));print("P159_FINAL_LOCK=false");print("P160_OPENED=false");print("REPORT="+str(r/fl.ELIG_REL));raise SystemExit(0 if x["status"]=="ELIGIBLE" else 2)
if __name__=="__main__":main()
