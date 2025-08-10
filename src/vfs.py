"""
Virtual File System (VFS) for WhatsApp chat archive files.
Provides efficient lookup and management of ChatFile objects.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from src.chat_data import ChatFile, ChatFileID


@dataclass
class VFS:
    """Virtual File System for managing ChatFile objects with efficient lookups."""

    # Main repository of all files indexed by their ChatFileID
    files_by_id: Dict[ChatFileID, ChatFile] = field(default_factory=dict)

    # Index for looking up files by their relative path
    files_by_path: Dict[str, ChatFile] = field(default_factory=dict)

    # Index for looking up files by filename (basename)
    files_by_name: Dict[str, Set[ChatFile]] = field(default_factory=lambda: dict())

    def add_file(self, chat_file: ChatFile) -> None:
        """Add a ChatFile to the VFS with all necessary indexing."""
        self.files_by_id[chat_file.id] = chat_file
        self.files_by_path[chat_file.path] = chat_file

        # Add to filename index
        basename = os.path.basename(chat_file.path)
        if basename not in self.files_by_name:
            self.files_by_name[basename] = set()
        self.files_by_name[basename].add(chat_file)

    def get_by_id(self, file_id: ChatFileID) -> Optional[ChatFile]:
        """Get a ChatFile by its ID."""
        return self.files_by_id.get(file_id)

    def get_by_path(self, path: str) -> Optional[ChatFile]:
        """Get a ChatFile by its relative path."""
        return self.files_by_path.get(path)

    def find_by_name(self, filename: str) -> Set[ChatFile]:
        """Find all ChatFiles with the given filename (basename)."""
        return self.files_by_name.get(filename, set())

    def exists(self, file_id: ChatFileID) -> bool:
        """Check if a file exists in the VFS."""
        file = self.get_by_id(file_id)
        return file is not None and file.exists

    def remove_file(self, chat_file: ChatFile) -> None:
        """Remove a ChatFile from all indexes."""
        if chat_file.id in self.files_by_id:
            del self.files_by_id[chat_file.id]

        if chat_file.path in self.files_by_path:
            del self.files_by_path[chat_file.path]

        basename = os.path.basename(chat_file.path)
        if basename in self.files_by_name:
            self.files_by_name[basename].discard(chat_file)
            if not self.files_by_name[basename]:
                del self.files_by_name[basename]

    def mark_nonexistent(self, file_id: ChatFileID) -> None:
        """Mark a file as non-existent without removing it from indexes."""
        if file := self.get_by_id(file_id):
            file.exists = False
