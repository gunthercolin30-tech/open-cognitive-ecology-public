from oif2g_test_support import *
for missing in ("runtime-health","validation-report","civilizational-state"):
 r=validator((missing,)).validate(MANIFEST_DIR/"portal_pilot.yaml"); assert not r.valid; assert any(e.code=="unknown_provider" for e in r.errors)
print("OIF2G_DEGRADATION_OK")
