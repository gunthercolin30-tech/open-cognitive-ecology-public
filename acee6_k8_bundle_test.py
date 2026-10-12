from acee6_k8_global_certifier import certify,verify_bundle
x=certify(True);assert x['verification']['valid'],x['verification'];assert verify_bundle(__import__('pathlib').Path(x['bundle_path']))['valid']
print('ACEE6_K8_BUNDLE_OK')
