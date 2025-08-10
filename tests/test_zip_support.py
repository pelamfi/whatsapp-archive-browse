"""Test VFS scanning functionality with ZIP files."""

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


def test_scan_directory_with_zip(temp_dir: str) -> None:
    """Test scanning directory with WhatsApp chat archive ZIP."""
    # Create a ZIP file with WhatsApp chat
    zip_path = Path(temp_dir) / "chat.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("_chat.txt", "chat content")
        zf.writestr("media/image.jpg", b"fake image")

    # Create initial VFS
    vfs = scan_directory_to_vfs(Path(temp_dir))

    # Verify ZIP file is found
    zip_file = next(iter(vfs.find_by_name("chat.zip")))
    assert zip_file is not None
    assert zip_file.exists
    assert not zip_file.parent_zip

    # Verify ZIP contents are found
    chat_files = vfs.find_by_name("_chat.txt")
    assert len(chat_files) == 1
    chat_file = next(iter(chat_files))
    assert chat_file.parent_zip == zip_file.id

    # Verify media file is found
    media_files = vfs.find_by_name("image.jpg")
    assert len(media_files) == 1
    media_file = next(iter(media_files))
    assert media_file.parent_zip == zip_file.id

    # Verify file open works
    content, size = vfs.open_file(chat_file)
    assert content.read().decode() == "chat content"
    assert size == len("chat content")


def test_ignore_non_whatsapp_zip(temp_dir: str) -> None:
    """Test that ZIP files without _chat.txt are ignored."""
    # Create a ZIP file without WhatsApp chat
    zip_path = Path(temp_dir) / "other.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("document.txt", "some content")

    # Create initial VFS
    vfs = scan_directory_to_vfs(Path(temp_dir))

    # Verify ZIP file is not indexed
    zip_files = vfs.find_by_name("other.zip")
    assert len(zip_files) == 0
