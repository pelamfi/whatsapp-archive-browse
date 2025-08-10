"""Test environment utilities."""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional
from zipfile import ZipFile

import pytest

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

    _created_dirs: set[Path]

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

        demo_path = Path(__file__).parent.parent.parent / "demo-chat"
        if demo_path.exists():
            shutil.copytree(demo_path, to_dir, dirs_exist_ok=True)
            # Normalize line endings BEFORE setting timestamps to avoid changing modification times
            for file_path in to_dir.rglob("*.txt"):
                self.normalize_line_endings(file_path)
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
        Filter the _chat.txt file to keep 2 first lines (chat name) and the specified line range.
        Updates the file modification time after editing.

        Args:
            chat_dir: Directory containing the _chat.txt file
            start_line: First line to keep (1-based, excluding the chat name line)
            end_line: Last line to keep (1-based, excluding the chat name line)
            timestamp: Unix timestamp to set after modifying (use TIMESTAMPS)
        """
        chat_file = chat_dir / "_chat.txt"
        with open(chat_file, "r", encoding="utf-8", newline="") as f:
            lines = f.readlines()

        # Always keep first line (chat name) and the specified range
        selected_lines = lines[0:2] + lines[start_line - 1 : end_line]

        with open(chat_file, "w", encoding="utf-8", newline="") as f:
            f.writelines(selected_lines)

        # Update timestamps after modification
        self.set_chat_timestamps(chat_dir, timestamp)

    def insert_chat_lines(self, chat_dir: Path, after_line: int, lines_to_insert: list[str], timestamp: float) -> None:
        """
        Insert lines into the _chat.txt file after the specified line number.
        Updates the file modification time after editing.

        Args:
            chat_dir: Directory containing the _chat.txt file
            after_line: Line number after which to insert (1-based)
            lines_to_insert: List of lines to insert (should include newlines)
            timestamp: Unix timestamp to set after modifying (use TIMESTAMPS)
        """
        chat_file = chat_dir / "_chat.txt"
        with open(chat_file, "r", encoding="utf-8", newline="") as f:
            existing_lines = f.readlines()

        # Insert new lines after the specified position
        new_lines = existing_lines[:after_line] + lines_to_insert + existing_lines[after_line:]

        with open(chat_file, "w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)

        # Update timestamps after modification
        self.set_chat_timestamps(chat_dir, timestamp)

    def normalize_line_endings(self, file_path: Path) -> None:
        """
        Normalize line endings in a text file to LF (Unix style) to ensure
        consistent behavior across platforms. Only modifies the file if changes are needed.

        Args:
            file_path: Path to the file to normalize
        """
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            original_content = f.read()

        # Replace CRLF with LF
        normalized_content = original_content.replace("\r\n", "\n")

        # Only write if content changed to avoid updating modification time unnecessarily
        if normalized_content != original_content:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(normalized_content)

    def copy_css_to_workspace(self, timestamp: float) -> None:
        """
        Copy the CSS file to src/resources in the test environment
        with a fixed timestamp.

        Args:
            timestamp: Unix timestamp to set for the CSS file
        """
        # Create src/resources in test environment
        resources_dir = self.base_dir / "src" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        self._created_dirs.add(resources_dir)

        # Get source CSS file path
        source_css = Path(__file__).parent.parent.parent / "src" / "resources" / "browseability-generator.css"

        if not source_css.exists():
            raise FileNotFoundError(f"CSS file not found at {source_css}")

        # Copy to test environment
        dest_css = resources_dir / "browseability-generator.css"
        shutil.copy2(source_css, dest_css)

        # Set fixed timestamp
        self.set_file_timestamps(dest_css, timestamp)

    def create_zip_archive(
        self, source_dir: Path, zip_path: Optional[Path] = None, timestamp: float = TIMESTAMPS["BASE"]
    ) -> Path:
        """
        Create a ZIP archive from a directory with consistent timestamps.

        Args:
            source_dir: Directory to archive
            zip_path: Optional path for the ZIP file. If None, creates in base_dir.
            timestamp: Unix timestamp to set for both zip file and entries (use TIMESTAMPS)

        Returns:
            Path to the created ZIP file
        """
        if zip_path is None:
            zip_path = self.base_dir / f"{source_dir.name}.zip"

        # Convert Unix timestamp to DOS date_time tuple for ZIP entries
        date = datetime.fromtimestamp(timestamp)
        date_time = (date.year, date.month, date.day, date.hour, date.minute, date.second)

        with ZipFile(zip_path, "w") as zf:
            for path in source_dir.rglob("*"):
                if path.is_file():
                    rel_path = path.relative_to(source_dir)
                    zinfo = zf.getinfo(str(rel_path)) if str(rel_path) in zf.namelist() else None
                    if zinfo is None:
                        zf.write(path, rel_path)
                        zinfo = zf.getinfo(str(rel_path))
                    zinfo.date_time = date_time

        # Set the timestamp on the ZIP file itself
        os.utime(zip_path, (timestamp, timestamp))

        return zip_path

    @property
    def path(self) -> Path:
        """Get the base directory path."""
        return self.base_dir


@pytest.fixture
def test_env() -> Generator[ChatTestEnvironment, Any, None]:
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
