"""
Scanner module that builds a VFS by scanning directories and zip files.
"""

import os
from pathlib import Path
from typing import Optional

from src.chat_data import ChatFile
from src.vfs import VFS


def scan_directory_to_vfs(base_path: Path, preserve_vfs: Optional[VFS] = None) -> VFS:
    """
    Scan directory and build a VFS containing all discovered files.

    Args:
        directory: Root directory to scan
        preserve_vfs: Optional existing VFS to preserve file history

    Returns:
        VFS containing all discovered files
    """
    vfs = VFS(base_path)

    # First pass: scan physical files
    for root, _, files in os.walk(base_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, base_path)

            chat_file = ChatFile(
                path=relative_path,
                size=os.path.getsize(full_path),
                modification_timestamp=os.path.getmtime(full_path),
                exists=True,
            )
            vfs.add_file(chat_file)

    # Second pass: preserve history from existing VFS if provided
    if preserve_vfs:
        for existing_file in preserve_vfs.files_by_id.values():
            if vfs.get_by_path(existing_file.path) is None:
                # File no longer exists in input, create new instance with exists=False
                nonexistent_file = ChatFile(
                    path=existing_file.path,
                    size=existing_file.size,
                    modification_timestamp=existing_file.modification_timestamp,
                    parent_zip=existing_file.parent_zip,
                    exists=False,
                )
                vfs.add_file(nonexistent_file)

    return vfs
