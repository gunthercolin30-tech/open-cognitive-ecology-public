from validation import p159_occ1k_r9ai_fl_b12_fresh_global_nonregression_v1 as a
def base(): return {"prepared_at_ns":100,"r9ah_sha256":a.sha(a.AH)}
def test_fresh_success(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)["fl_b12"]=="PASS"
def test_stale_blocks(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",100)["fl_b12"]=="INCONCLUSIVE"
def test_missing_success_marker_blocks(): assert a.assess(base(),"done\n",101)["fl_b12"]=="INCONCLUSIVE"
def test_failure_marker_blocks(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\nFAST_ACCEPTANCE_FAILED\n",101)["fl_b12"]=="INCONCLUSIVE"
def test_r9ah_anchor_required():
 p=base();p["r9ah_sha256"]="0"*64;assert a.assess(p,"FAST_ACCEPTANCE_ALL_OK\n",101)["fl_b12"]=="INCONCLUSIVE"
def test_debt_not_closed(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)["assurance_debt_closed"] is False
def test_meta_not_claimed(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)["meta_assurance_complete"] is False
def test_no_lock(): 
 x=a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101);assert not x["lock_ready"] and not x["lock_granted"]
def test_no_p160b(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)["p160b_opened"] is False
def test_deterministic(): assert a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)==a.assess(base(),"FAST_ACCEPTANCE_ALL_OK\n",101)
