"""
Tests for input scanner2 module.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from src.chat_data2 import ChatData2, ChatFile2
from src.input_scanner2 import find_chat_files2, scan_input_directory2


def test_find_chat_files2(tmp_path: Path) -> None:
    """Test that find_chat_files finds _chat.txt files and sorts them by mtime"""
    # Copy demo chat file twice with different names
    demo_path = "demo-chat/_chat.txt"
    chat1_dir = tmp_path / "backup1"
    chat2_dir = tmp_path / "backup2"
    chat1_dir.mkdir()
    chat2_dir.mkdir()

    # First backup - Space Rocket chat
    chat1 = chat1_dir / "_chat.txt"
    shutil.copy(demo_path, chat1)
    old_time = datetime.now().timestamp() - 86400  # Yesterday
    os.utime(chat1, (old_time, old_time))

    # Second backup - Galaxy Defender chat (modified copy)
    chat2 = chat2_dir / "_chat.txt"
    with open(demo_path, "r", encoding="utf-8") as f:
        content = f.read().replace("Space Rocket", "Galaxy Defender")
    chat2.write_text(content, encoding="utf-8")

    # Find and verify chat files are returned in chronological order
    files = find_chat_files2(str(tmp_path))
    assert len(files) == 2
    assert any(f.path.endswith(str(chat1.relative_to(tmp_path))) for f in files)  # Older file first
    assert any(f.path.endswith(str(chat2.relative_to(tmp_path))) for f in files)  # Newer file second


def test_scan_input_directory2_finds_chats(tmp_path: Path) -> None:
    """Test that scanner finds and processes chat files"""
    # Copy demo chat to test directory
    chat_dir = tmp_path / "backup"
    chat_dir.mkdir()
    shutil.copy("demo-chat/_chat.txt", chat_dir / "_chat.txt")

    # Scan directory and verify it found the chat
    chat_data = scan_input_directory2(str(tmp_path))
    assert len(chat_data.chats) == 1  # Found one chat
    assert len(next(iter(chat_data.chats.values())).messages) > 0  # Has messages
