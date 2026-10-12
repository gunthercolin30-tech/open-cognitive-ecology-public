from oif2g_test_support import *
from oif.interface.abstract_renderer import render_abstract
from oif.interface.complex_manifest_profile import validate_complex_profile
for name in NAMES:
 r=validator().validate(MANIFEST_DIR/(name+".yaml")); assert r.valid,(name,[e.code for e in r.errors]); p=validate_complex_profile(r.manifest); assert p.valid,p.errors; assert p.tab_count>=3; assert not r.manifest.operations and not r.manifest.permissions; assert render_abstract(r.manifest).source_sha256==r.manifest.sha256()
print("OIF2G_FUNCTIONAL_OK")
