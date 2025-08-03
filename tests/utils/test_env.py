"""Test environment utilities."""

import os
import pytest
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from datetime import datetime
import time

# Predefined timestamps for consistent file modification times across systems
TIMESTAMPS = {
    "BASE": datetime(2020, 1, 1, 0, 0, 0).timestamp(),  # 2020-01-01 00:00:00
    "BACKUP1": datetime(2020, 2, 1, 0, 0, 0).timestamp(),  # 2020-02-01 00:00:00
    "BACKUP2": datetime(2020, 3, 1, 0, 0, 0).timestamp(),  # 2020-03-01 00:00:00
}

class ChatTestEnvironment:
    """
    Test environment with temporary directory management and utility functions.
    Provides methods for creating and managing test input/output directories.
    """
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self._created_dirs = set()

    def create_input_dir(self, name: str = "input") -> Path:
        """Create a new input directory under the test environment."""
        dir_path = self.base_dir / name
        dir_path.mkdir(exist_ok=True)
        self._created_dirs.add(dir_path)
        return dir_path

    def create_output_dir(self, name: str = "output") -> Path:
        """Create a new output directory under the test environment."""
        dir_path = self.base_dir / name
        dir_path.mkdir(exist_ok=True)
        self._created_dirs.add(dir_path)
        return dir_path

    def copy_demo_chat(self, to_dir: Optional[Path], timestamp: float) -> Path:
        """
        Copy demo chat data to specified directory or to a new input directory
        and set modification times for all copied files.

        Args:
            to_dir: Target directory for the copy, or None to create a new input dir
            timestamp: Unix timestamp to set for all copied files (use TIMESTAMPS)

        Returns:
            Path to the directory containing the copied data
        """
        if to_dir is None:
            to_dir = self.create_input_dir()

        demo_path = (Path(__file__).parent.parent.parent / "demo-chat")
        if demo_path.exists():
            shutil.copytree(demo_path, to_dir, dirs_exist_ok=True)
            self.set_chat_timestamps(to_dir, timestamp)
        return to_dir

    def duplicate_chat(self, source_dir: Path, new_name: str) -> Path:
        """
        Create a duplicate of a chat directory with a new name.
        Useful for testing duplicate chat handling.
        """
        target_dir = self.base_dir / new_name
        shutil.copytree(source_dir, target_dir)
        self._created_dirs.add(target_dir)
        return target_dir

    def create_chat_backup(self, original_dir: Path, suffix: str = "_backup") -> Path:
        """
        Create a backup copy of a chat directory, simulating a second backup of the same chat.
        """
        return self.duplicate_chat(original_dir, f"{original_dir.name}{suffix}")

    def set_file_timestamps(self, file_path: Path, timestamp: float) -> None:
        """
        Set both access and modification times of a file to a specific timestamp.
        
        Args:
            file_path: Path to the file to modify
            timestamp: Unix timestamp to set (can use TIMESTAMPS dictionary)
        """
        os.utime(file_path, (timestamp, timestamp))

    def set_chat_timestamps(self, chat_dir: Path, timestamp: float) -> None:
        """
        Set timestamps for all files in a chat directory.
        
        Args:
            chat_dir: Path to the chat directory
            timestamp: Unix timestamp to set (can use TIMESTAMPS dictionary)
        """
        for root, _, files in os.walk(chat_dir):
            for file in files:
                file_path = Path(root) / file
                self.set_file_timestamps(file_path, timestamp)

    def filter_chat_lines(self, chat_dir: Path, start_line: int, end_line: int, timestamp: float) -> None:
        """
        Filter the _chat.txt file to keep line 1 (chat name) and the specified line range.
        Updates the file modification time after editing.
        
        Args:
            chat_dir: Directory containing the _chat.txt file
            start_line: First line to keep (1-based, excluding the chat name line)
            end_line: Last line to keep (1-based, excluding the chat name line)
            timestamp: Unix timestamp to set after modifying (use TIMESTAMPS)
        """
        chat_file = chat_dir / "_chat.txt"
        with open(chat_file, "r") as f:
            lines = f.readlines()
        
        # Always keep first line (chat name) and the specified range
        selected_lines = [lines[0]] + lines[start_line - 1:end_line]
        
        with open(chat_file, "w") as f:
            f.writelines(selected_lines)
        
        # Update timestamps after modification
        self.set_chat_timestamps(chat_dir, timestamp)

    @property
    def path(self) -> Path:
        """Get the base directory path."""
        return self.base_dir

@pytest.fixture
def test_env():
    """
    Create a test environment with temporary directory that's automatically cleaned up.
    
    Usage:
        def test_something(test_env):
            # Create input and output dirs
            input_dir = test_env.create_input_dir()
            output_dir = test_env.create_output_dir()
            
            # Copy demo chat
            test_env.copy_demo_chat(input_dir)
            
            # Create a backup
            backup_dir = test_env.create_chat_backup(input_dir)
            
            # Run your test...
    """
    test_dir = tempfile.mkdtemp()
    env = ChatTestEnvironment(test_dir)
    yield env
    shutil.rmtree(test_dir)
