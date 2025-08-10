"""
Scanner module that builds a VFS by scanning directories and zip files.
"""

import os
from typing import Optional

from src.chat_data import ChatFile
from src.vfs import VFS


def scan_directory_to_vfs(directory: str, preserve_vfs: Optional[VFS] = None) -> VFS:
    """
    Scan directory and build a VFS containing all discovered files.

    Args:
        directory: Root directory to scan
        preserve_vfs: Optional existing VFS to preserve file history

    Returns:
        VFS containing all discovered files
    """
    vfs = VFS()

    # First pass: scan physical files
    for root, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, directory)

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
                # File no longer exists in input, preserve it but mark as non-existent
                existing_file.exists = False
                vfs.add_file(existing_file)

    return vfs
