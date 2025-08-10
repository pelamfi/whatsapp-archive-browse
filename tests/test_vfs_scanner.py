"""Test VFS scanning functionality."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.vfs_scanner import scan_directory_to_vfs


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


def test_scan_directory_basic(temp_dir: str) -> None:
    """Test basic directory scanning with file preservation."""
    test_files = {
        "file1.txt": b"content1",
        "subdir/file2.txt": b"content2",
        "_chat.txt": b"chat content",
    }

    # Create test files
    for path, content in test_files.items():
        full_path = Path(temp_dir) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)

    # Create initial VFS
    vfs = scan_directory_to_vfs(temp_dir)

    # Verify all files are found and exist
    assert len(vfs.files_by_id) == len(test_files)
    for path in test_files:
        chat_file = vfs.get_by_path(path)
        assert chat_file is not None
        assert chat_file.exists
        assert chat_file.path == path
        assert chat_file.size == len(test_files[path])

    # Verify file lookup by name works
    chat_files = vfs.find_by_name("_chat.txt")
    assert len(chat_files) == 1
    chat_file = next(iter(chat_files))
    assert chat_file.path == "_chat.txt"

    # Remove a file and rescan with preservation
    os.unlink(os.path.join(temp_dir, "file1.txt"))
    new_vfs = scan_directory_to_vfs(temp_dir, preserve_vfs=vfs)

    # Verify removed file is preserved but marked as non-existent
    preserved_file = new_vfs.get_by_path("file1.txt")
    assert preserved_file is not None
    assert not preserved_file.exists
