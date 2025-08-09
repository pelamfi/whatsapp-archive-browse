"""
Tests for metadata updater2 module.
"""

import os
import time
from pathlib import Path

from src.chat_data2 import Chat2, ChatData2, ChatName2, Message2
from src.metadata_updater2 import update_metadata2


def test_metadata_update2(tmp_path: Path) -> None:
    """Test the atomic update process for metadata files"""
    # Create test data
    chat_data = ChatData2()
    chat_data.chats[ChatName2("Test")] = Chat2(
        chat_name=ChatName2("Test"),
        messages=[Message2(timestamp="12:00", sender="Alice", content="Hi", year=2025)],
    )

    # First update - creates new file
    update_metadata2(chat_data, str(tmp_path))
    assert os.path.exists(os.path.join(tmp_path, "browseability-generator-chat-data.json"))
    assert not os.path.exists(os.path.join(tmp_path, "browseability-generator-chat-data-BACKUP.json"))

    # Second update - should create backup
    chat_data.chats[ChatName2("Test")].messages.append(
        Message2(timestamp="12:01", sender="Bob", content="Hello", year=2025)
    )

    # Sleep for a moment to ensure file timestamps will be different
    time.sleep(0.1)
    update_metadata2(chat_data, str(tmp_path))

    assert os.path.exists(os.path.join(tmp_path, "browseability-generator-chat-data.json"))
    assert os.path.exists(os.path.join(tmp_path, "browseability-generator-chat-data-BACKUP.json"))

    # Third update - should replace old backup
    old_backup_time = os.path.getmtime(os.path.join(tmp_path, "browseability-generator-chat-data-BACKUP.json"))
    chat_data.chats[ChatName2("Test")].messages.append(
        Message2(timestamp="12:02", sender="Alice", content="Bye", year=2025)
    )

    # Sleep for a moment to ensure file timestamps will be different
    time.sleep(0.1)
    update_metadata2(chat_data, str(tmp_path))

    new_backup_time = os.path.getmtime(os.path.join(tmp_path, "browseability-generator-chat-data-BACKUP.json"))
    assert new_backup_time > old_backup_time

    # Verify the final content
    with open(os.path.join(tmp_path, "browseability-generator-chat-data.json"), "r", encoding="utf-8") as f:
        final_json = f.read()
    final_data = ChatData2.from_json(final_json)
    assert len(final_data.chats[ChatName2("Test")].messages) == 3
