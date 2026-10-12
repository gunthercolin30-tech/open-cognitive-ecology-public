from pathlib import Path
import ast,tempfile
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
from ontology import occ_constitutional_adversarial_crown_h8 as h8

def _run_node():
 tree=ast.parse(Path(h8.__file__).read_text(encoding="utf-8"))
 return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run")

def test_a079_reuses_bounded_context_not_ambient_copy2():
 run=_run_node(); calls=[]
 for n in ast.walk(run):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute): calls.append(n.func.attr)
 assert "copy2_from" in calls
 assert "copy2" not in calls

def test_bounded_copy2_from_preserves_bytes_and_mode():
 with tempfile.TemporaryDirectory() as td:
  base=Path(td); src=base/"source.json"; src.write_text('{"x":1}\n',encoding="utf-8"); src.chmod(0o640)
  ctx=BoundedFilesystemValidationContext(prefix="oce-i77-a079-")
  try:
   dst=ctx.copy2_from(src,Path("repo")/"profile.json")
   assert dst.read_bytes()==src.read_bytes()
   assert (dst.stat().st_mode & 0o777)==(src.stat().st_mode & 0o777)
   assert str(dst).startswith(str(ctx.root))
  finally: ctx.remove_tree()

def test_bounded_copy2_from_rejects_symlink_source():
 with tempfile.TemporaryDirectory() as td:
  base=Path(td); real=base/"real"; real.write_text("x"); link=base/"link"; link.symlink_to(real)
  ctx=BoundedFilesystemValidationContext(prefix="oce-i77-a079-")
  try:
   try: ctx.copy2_from(link,"repo/profile")
   except PermissionError as e: assert "symlink source forbidden" in str(e)
   else: raise AssertionError("symlink source accepted")
  finally: ctx.remove_tree()

def test_bounded_copy2_from_rejects_escape():
 with tempfile.TemporaryDirectory() as td:
  src=Path(td)/"s"; src.write_text("x")
  ctx=BoundedFilesystemValidationContext(prefix="oce-i77-a079-")
  try:
   try: ctx.copy2_from(src,"../escape")
   except PermissionError as e: assert "sandbox escape forbidden" in str(e)
   else: raise AssertionError("sandbox escape accepted")
  finally: ctx.remove_tree()
