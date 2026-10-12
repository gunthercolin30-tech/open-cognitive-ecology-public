from pathlib import Path
import pytest
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext

def test_create_write_cleanup():
    c=BoundedFilesystemValidationContext(prefix="oce-test-bounded-"); root=c.root
    assert c.write_text("repo/a.txt","x").read_text()=="x"; c.remove_tree(); assert not root.exists()

def test_traversal_absolute_rejected(tmp_path):
    c=BoundedFilesystemValidationContext(prefix="oce-test-bounded-")
    try:
        with pytest.raises(PermissionError): c.write_text("../escape.txt","x")
        with pytest.raises(PermissionError): c.write_text(str(tmp_path/"escape.txt"),"x")
    finally: c.remove_tree()

def test_symlink_escape_rejected(tmp_path):
    c=BoundedFilesystemValidationContext(prefix="oce-test-bounded-"); outside=tmp_path/"outside"; outside.mkdir(); (c.root/"link").symlink_to(outside,target_is_directory=True)
    try:
        with pytest.raises(PermissionError): c.write_text("link/x.txt","x")
        assert not (outside/"x.txt").exists()
    finally: c.remove_tree()

def test_copy_file_tree_and_symlink_source_rejected(tmp_path):
    f=tmp_path/"src.txt"; f.write_text("a"); d=tmp_path/"srcdir"; d.mkdir(); (d/"b.txt").write_text("b"); link=tmp_path/"link"; link.symlink_to(f)
    c=BoundedFilesystemValidationContext(prefix="oce-test-bounded-")
    try:
        assert c.copy2_from(f,"repo/f.txt").read_text()=="a"
        assert (c.copytree_from(d,"repo/d")/"b.txt").read_text()=="b"
        with pytest.raises(PermissionError): c.copy2_from(link,"repo/link")
    finally: c.remove_tree()

def test_closed_rejects_effect():
    c=BoundedFilesystemValidationContext(prefix="oce-test-bounded-"); c.remove_tree()
    with pytest.raises(RuntimeError): c.write_text("x","y")
