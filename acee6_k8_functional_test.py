from acee6_k8_global_certifier import audit
r=audit();assert r['valid'],r['reasons'];assert len(r['reports'])==8;assert len(r['final_locks'])==8
print('ACEE6_K8_FUNCTIONAL_OK')
