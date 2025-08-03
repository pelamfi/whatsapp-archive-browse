"""
Unit tests for metadata updater. Focus on the atomic update process.
Full integration tests will be added in step 10.
"""

import os
import pytest
from src.metadata_updater import update_metadata
from src.chat_data import ChatData, Chat, ChatName, Message

def test_metadata_update(tmp_path):
    """Test the atomic update process for metadata files"""
    # Create test data
    chat_data = ChatData(chats={
        ChatName("Test"): Chat(
            chat_name=ChatName("Test"),
            messages=[
                Message(timestamp="12:00", sender="Alice", content="Hi", year=2025)
            ]
        )
    })
    chat_data.timestamp = "2025-08-03 14:28:38"  # Set fixed timestamp
    
    # First update - creates new file
    update_metadata(chat_data, str(tmp_path))
    assert os.path.exists(os.path.join(tmp_path, 'browseability-generator-chat-data.json'))
    assert not os.path.exists(os.path.join(tmp_path, 'browseability-generator-chat-data-BACKUP.json'))
    
    # Second update - should create backup
    chat_data.chats[ChatName("Test")].messages.append(
        Message(timestamp="12:01", sender="Bob", content="Hello", year=2025)
    )
    update_metadata(chat_data, str(tmp_path))
    assert os.path.exists(os.path.join(tmp_path, 'browseability-generator-chat-data.json'))
    assert os.path.exists(os.path.join(tmp_path, 'browseability-generator-chat-data-BACKUP.json'))
    
    # Third update - should replace old backup
    old_backup_time = os.path.getmtime(os.path.join(tmp_path, 'browseability-generator-chat-data-BACKUP.json'))
    # Sleep for a moment to ensure file timestamps will be different
    import time
    time.sleep(0.1)
    chat_data.chats[ChatName("Test")].messages.append(
        Message(timestamp="12:02", sender="Alice", content="Bye", year=2025)
    )
    update_metadata(chat_data, str(tmp_path))
    new_backup_time = os.path.getmtime(os.path.join(tmp_path, 'browseability-generator-chat-data-BACKUP.json'))
    assert new_backup_time > old_backup_time
    
    # Verify the final content
    with open(os.path.join(tmp_path, 'browseability-generator-chat-data.json'), 'r') as f:
        final_json = f.read()
    final_data = ChatData.from_json(final_json)
    assert len(final_data.chats[ChatName("Test")].messages) == 3
