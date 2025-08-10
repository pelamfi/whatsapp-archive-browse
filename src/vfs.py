"""
Virtual File System (VFS) for WhatsApp chat archive files.
Provides efficient lookup and management of ChatFile objects.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from src.chat_data import ChatFile, ChatFileID


@dataclass(frozen=True)
class ChatFileSet:
    """Set wrapper for ChatFile objects that uses ID as hash key."""

    _files: Set[ChatFile] = field(default_factory=set)

    def add(self, chat_file: ChatFile) -> None:
        """Add a ChatFile using its ID as the hash key."""
        self._files.add(chat_file)

    def discard(self, chat_file: ChatFile) -> None:
        """Remove a ChatFile if it exists in the set."""
        self._files.discard(chat_file)

    def to_set(self) -> Set[ChatFile]:
        """Convert to a regular set."""
        return set(self._files)


@dataclass
class VFS:
    """Virtual File System for managing ChatFile objects with efficient lookups."""

    # Main repository of all files indexed by their ChatFileID
    files_by_id: Dict[ChatFileID, ChatFile] = field(default_factory=dict)

    # Index for looking up files by their relative path
    files_by_path: Dict[str, ChatFile] = field(default_factory=dict)

    # Index for looking up files by filename (basename)
    files_by_name: Dict[str, ChatFileSet] = field(default_factory=dict)

    def add_file(self, chat_file: ChatFile) -> None:
        """Add a ChatFile to the VFS with all necessary indexing."""
        self.files_by_id[chat_file.id] = chat_file
        self.files_by_path[chat_file.path] = chat_file

        # Add to filename index
        basename = os.path.basename(chat_file.path)
        if basename not in self.files_by_name:
            self.files_by_name[basename] = ChatFileSet()
        self.files_by_name[basename].add(chat_file)

    def get_by_id(self, file_id: ChatFileID) -> Optional[ChatFile]:
        """Get a ChatFile by its ID."""
        return self.files_by_id.get(file_id)

    def get_by_path(self, path: str) -> Optional[ChatFile]:
        """Get a ChatFile by its relative path."""
        return self.files_by_path.get(path)

    def find_by_name(self, filename: str) -> Set[ChatFile]:
        """Find all ChatFiles with the given filename (basename)."""
        file_set = self.files_by_name.get(filename)
        if file_set is None:
            return set()
        return file_set.to_set()

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
        """Mark a file as non-existent by creating a new instance and updating references."""
        if old_file := self.get_by_id(file_id):
            # Create new instance with exists=False
            new_file = ChatFile(
                path=old_file.path,
                size=old_file.size,
                modification_timestamp=old_file.modification_timestamp,
                parent_zip=old_file.parent_zip,
                exists=False,
            )
            # Update references
            self.files_by_id[file_id] = new_file
            self.files_by_path[new_file.path] = new_file
            basename = os.path.basename(new_file.path)
            if basename in self.files_by_name:
                old_set = self.files_by_name[basename]
                new_set = ChatFileSet()
                for f in old_set.to_set():
                    if f.id == file_id:
                        new_set.add(new_file)
                    else:
                        new_set.add(f)
                self.files_by_name[basename] = new_set
