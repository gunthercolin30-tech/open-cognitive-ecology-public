from pathlib import Path
import ast,hashlib
STRONG={
 "subprocess.run":"PROCESS","subprocess.Popen":"PROCESS","subprocess.call":"PROCESS",
 "os.system":"PROCESS","socket.socket":"NETWORK","urllib.request.urlopen":"NETWORK",
 "requests.request":"NETWORK","requests.get":"NETWORK","requests.post":"NETWORK",
 "httpx.request":"NETWORK","sqlite3.connect":"DATABASE"
}
WRITE_ATTRS={"write_text":"FILESYSTEM","write_bytes":"FILESYSTEM","unlink":"FILESYSTEM",
"rename":"FILESYSTEM","replace":"FILESYSTEM","mkdir":"FILESYSTEM","rmdir":"FILESYSTEM"}
def _name(n):
 if isinstance(n,ast.Name):return n.id
 if isinstance(n,ast.Attribute):
  x=_name(n.value);return (x+"." if x else "")+n.attr
 return ""
def scan_file(path,root):
 text=path.read_text(encoding="utf-8",errors="ignore")
 try:tree=ast.parse(text)
 except SyntaxError:return {"path":str(path.relative_to(root)),"classification":"REVIEW_REQUIRED","reasons":["SYNTAX_UNPARSED"],"primitives":[]}
 prim=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   nm=_name(n.func)
   if nm in STRONG:prim.append({"primitive":nm,"effect_class":STRONG[nm],"line":n.lineno})
   elif isinstance(n.func,ast.Attribute) and n.func.attr in WRITE_ATTRS:
    prim.append({"primitive":n.func.attr,"effect_class":WRITE_ATTRS[n.func.attr],"line":n.lineno})
   elif nm=="open" and len(n.args)>=2 and isinstance(n.args[1],ast.Constant) and any(x in str(n.args[1].value) for x in ("w","a","x","+")):
    prim.append({"primitive":"open(write)","effect_class":"FILESYSTEM","line":n.lineno})
 mediated=("governed_effector_adapter" in text or "GovernedEffectorAdapter" in text)
 if not prim:cl="NONCAUSAL_NO_STRONG_PRIMITIVE"
 elif mediated:cl="MEDIATED_CANDIDATE"
 else:cl="REVIEW_REQUIRED"
 return {"path":str(path.relative_to(root)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
 "classification":cl,"reasons":[] if cl!="REVIEW_REQUIRED" else ["STRONG_CAUSAL_PRIMITIVE_WITHOUT_PROVEN_G5_MEDIATION"],
 "primitives":prim}
def scan(root):
 out=[]
 for p in sorted((root/"ontology").rglob("*.py")):
  if ".bak" in p.name or "__pycache__" in p.parts:continue
  out.append(scan_file(p,root))
 return out
