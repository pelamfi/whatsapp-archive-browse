"""
Scanner module that builds a VFS by scanning directories and zip files.
"""

import os
import time
from pathlib import Path
from typing import Optional

from src.chat_data import ChatFile
from src.vfs import VFS
from src.zip_utils import is_whatsapp_archive, list_zip_contents


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

            # Handle ZIP files
            if filename.endswith(".zip"):
                zip_path = Path(full_path)
                if is_whatsapp_archive(zip_path):
                    # Add ZIP file itself
                    zip_file = ChatFile(
                        path=relative_path,
                        size=os.path.getsize(full_path),
                        modification_timestamp=os.path.getmtime(full_path),
                        exists=True,
                    )
                    vfs.add_file(zip_file)

                    # Add ZIP contents
                    zip_id = zip_file.id
                    for zip_info in list_zip_contents(zip_path):
                        chat_file = ChatFile(
                            path=zip_info.filename,
                            size=zip_info.file_size,
                            modification_timestamp=time.mktime(zip_info.date_time + (0, 0, -1)),
                            parent_zip=zip_id,
                            exists=True,
                        )
                        vfs.add_file(chat_file)
                continue

            # Regular files
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
