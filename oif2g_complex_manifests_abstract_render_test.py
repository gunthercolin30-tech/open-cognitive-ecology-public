from oif2g_test_support import *
from oif.interface.abstract_renderer import render_abstract
for name in NAMES:
 r=validator().validate(MANIFEST_DIR/(name+".yaml")); assert r.valid; assert render_abstract(r.manifest)==render_abstract(r.manifest)
print("OIF2G_ABSTRACT_RENDER_OK")
