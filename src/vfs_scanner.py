"""
Scanner module that builds a VFS by scanning directories and zip files.
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

from src.chat_data import ChatFile
from src.vfs import VFS
from src.zip_utils import is_whatsapp_archive, list_zip_contents

logger = logging.getLogger(__name__)


# Track scan progress
class ScanProgress:
    def __init__(self) -> None:
        self.chat_files = 0
        self.zip_files = 0
        self.last_log_time = 0.0

    def log_if_needed(self, current_dir: str) -> None:
        current_time = time.time()
        if current_time - self.last_log_time >= 1.0:  # Log at most once per second
            self.last_log_time = current_time
            logger.debug(f"Scanning {current_dir}")
            logger.debug(f"Found {self.chat_files} chat files and {self.zip_files} zip archives")


def scan_directory_to_vfs(base_path: Path, preserve_vfs: Optional[VFS] = None) -> VFS:
    """
    Scan directory and build a VFS containing all discovered files.

    Args:
        directory: Root directory to scan
        preserve_vfs: Optional existing VFS to preserve file history

    Returns:
        VFS containing all discovered files
    """
    logger.info(f"Scanning directory: {base_path}")
    vfs = VFS(base_path)
    progress = ScanProgress()

    # First pass: scan physical files
    for root, _, files in os.walk(base_path):
        progress.log_if_needed(os.path.relpath(root, base_path))

        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, base_path)

            logger.debug(f"Processing file: {relative_path}")

            # Track chat files
            if filename == "_chat.txt":
                progress.chat_files += 1

            # Handle ZIP files
            if filename.endswith(".zip"):
                zip_path = Path(full_path)
                if is_whatsapp_archive(zip_path):
                    progress.zip_files += 1
                    logger.debug(f"Found WhatsApp archive: {relative_path}")

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
                    logger.debug(f"Processing contents of {relative_path}")
                    for zip_info in list_zip_contents(zip_path):
                        chat_file = ChatFile(
                            path=zip_info.filename,
                            size=zip_info.file_size,
                            modification_timestamp=time.mktime(zip_info.date_time + (0, 0, -1)),
                            parent_zip=zip_id,
                            exists=True,
                        )
                        vfs.add_file(chat_file)
                        if zip_info.filename.endswith("_chat.txt"):
                            progress.chat_files += 1
                    logger.debug(f"Finished processing ZIP: {relative_path}")
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
        logger.debug("Preserving history from existing VFS")
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

    logger.info(f"Scan complete. Found {progress.chat_files} chat files and {progress.zip_files} ZIP archives")
    return vfs
