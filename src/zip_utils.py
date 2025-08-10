"""Utilities for handling ZIP files in the VFS."""

import io
import zipfile
from pathlib import Path
from typing import Optional, Tuple


def is_whatsapp_archive(zip_path: Path) -> bool:
    """Check if a ZIP file contains a WhatsApp chat archive (_chat.txt)."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            return any(name.endswith("_chat.txt") for name in zf.namelist())
    except zipfile.BadZipFile:
        return False


def get_file_from_zip(zip_path: Path, file_path: str) -> Tuple[io.BytesIO, Optional[int]]:
    """Extract a specific file from a ZIP archive into memory.

    Returns:
        Tuple of (file content as BytesIO, file size or None if unknown)
    """
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(file_path)
        return io.BytesIO(zf.read(file_path)), info.file_size


def list_zip_contents(zip_path: Path) -> list[zipfile.ZipInfo]:
    """List contents of a ZIP file."""
    with zipfile.ZipFile(zip_path) as zf:
        return zf.filelist
