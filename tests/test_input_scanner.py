import pytest
import os
import shutil
from datetime import datetime
from src.input_scanner import scan_input_directory, find_chat_files, remove_duplicate_messages
from src.chat_data import Chat, ChatName, Message, ChatFile

def test_find_chat_files(tmp_path):
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
    with open(demo_path, 'r', encoding='utf-8') as f:
        content = f.read().replace('Space Rocket', 'Galaxy Defender')
    chat2.write_text(content, encoding='utf-8')
    
    # Find and verify chat files are returned in chronological order
    files = find_chat_files(str(tmp_path))
    assert len(files) == 2
    assert files[0][0] == str(chat1)  # Older file first
    assert files[1][0] == str(chat2)  # Newer file second

def test_remove_duplicate_messages():
    """Test duplicate message removal from a chat"""
    chat = Chat(chat_name=ChatName("test"))
    msg1 = Message(timestamp="12:00", sender="Alice", content="Hi", year=2023)
    msg2 = Message(timestamp="12:00", sender="Alice", content="Hi", year=2023)  # Duplicate
    msg3 = Message(timestamp="12:01", sender="Bob", content="Hello", year=2023)
    
    chat.messages = [msg1, msg2, msg3]
    remove_duplicate_messages(chat)
    
    assert len(chat.messages) == 2
    assert chat.messages[0].sender == "Alice"
    assert chat.messages[1].sender == "Bob"

def test_scan_input_directory_finds_chats(tmp_path):
    """Test that scanner finds and processes chat files"""
    # Copy demo chat to test directory
    chat_dir = tmp_path / "backup"
    chat_dir.mkdir()
    shutil.copy("demo-chat/_chat.txt", chat_dir / "_chat.txt")
    
    # Scan directory and verify it found the chat
    chat_data = scan_input_directory(str(tmp_path))
    assert len(chat_data.chats) == 1  # Found one chat
    assert len(next(iter(chat_data.chats.values())).messages) > 0  # Has messages
