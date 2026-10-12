from acee6_k3_mutation_runner import run,verify
r=run(limit=1)["report"]; r["report_hash"]="0"*64; assert not verify(r)["valid"]
print("ACEE6_K3_REPORT_TAMPER_OK")
