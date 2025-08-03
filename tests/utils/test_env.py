"""Test environment utilities."""

import os
import pytest
import shutil
import tempfile
from pathlib import Path
from typing import Optional

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

    def copy_demo_chat(self, to_dir: Optional[Path] = None) -> Path:
        """
        Copy demo chat data to specified directory or to a new input directory.
        Returns the directory containing the copied data.
        """
        if to_dir is None:
            to_dir = self.create_input_dir()

        demo_path = (Path(__file__).parent.parent.parent / "demo-chat")
        if demo_path.exists():
            shutil.copytree(demo_path, to_dir, dirs_exist_ok=True)
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
