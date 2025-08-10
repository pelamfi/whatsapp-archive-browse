"""Test VFS scanning functionality."""

import os
import tempfile
from pathlib import Path
from typing import Generator
from zipfile import ZipFile

import pytest

from src.vfs_scanner import scan_directory_to_vfs


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


def test_scan_directory_basic(temp_dir: Path) -> None:
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
    vfs = scan_directory_to_vfs(Path(temp_dir))

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
    new_vfs = scan_directory_to_vfs(Path(temp_dir), preserve_vfs=vfs)

    # Verify removed file is preserved but marked as non-existent
    preserved_file = new_vfs.get_by_path("file1.txt")
    assert preserved_file is not None
    assert not preserved_file.exists


def test_scan_zip_file(temp_dir: Path) -> None:
    """Test scanning a directory containing a WhatsApp chat ZIP archive."""
    # Create a WhatsApp chat ZIP
    zip_path = Path(temp_dir) / "chat.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("_chat.txt", "chat content")
        zf.writestr("media/image1.jpg", b"fake image")

    # Create initial VFS
    vfs = scan_directory_to_vfs(Path(temp_dir))

    # Verify ZIP file is found
    zip_files = vfs.find_by_name("chat.zip")
    assert len(zip_files) == 1
    zip_file = next(iter(zip_files))
    assert zip_file.exists
    assert not zip_file.parent_zip

    # Verify ZIP contents are found
    chat_files = vfs.find_by_name("_chat.txt")
    assert len(chat_files) == 1
    chat_file = next(iter(chat_files))
    assert chat_file.parent_zip == zip_file.id

    # Verify content can be read
    content, size = vfs.open_file(chat_file)
    assert content.read().decode() == "chat content"
    assert size == len("chat content")

    # Verify media file
    media_files = vfs.find_by_name("image1.jpg")
    assert len(media_files) == 1
    media_file = next(iter(media_files))
    assert media_file.parent_zip == zip_file.id


def test_scan_non_whatsapp_zip(temp_dir: Path) -> None:
    """Test that ZIP files without _chat.txt are not indexed."""
    # Create a non-WhatsApp ZIP
    zip_path = Path(temp_dir) / "other.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("document.txt", "some content")

    # Create initial VFS
    vfs = scan_directory_to_vfs(Path(temp_dir))

    # Verify ZIP file is not indexed
    zip_files = vfs.find_by_name("other.zip")
    assert len(zip_files) == 0
