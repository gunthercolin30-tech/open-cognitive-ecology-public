from ontology import occ_p159_final_lock as fl
from ontology import occ_p159_final_lock_postlock_verifier as pv
def main(filesystem_effect_context=None):
 r=fl.root();x=pv.verify(r);out=r/fl.ART_ROOT/"p159_postlock_verification_v1.json";fl.atomic_json(out,x,filesystem_effect_context);print("P159_OCC1K_"+x["status"]);print("checks=%d/%d"%(sum(v is True for v in x["checks"].values()),len(x["checks"])));print("P159_FINAL_LOCK="+str(x.get("p159_final_lock",False)).lower());print("P160_OPENED=false");print("REPORT="+str(out));raise SystemExit(0 if x["status"]=="POST_LOCK_VERIFIED" else 2)
if __name__=="__main__":main()
