"""
Tests for the media locator module.
"""

from pathlib import Path

from src.chat_data import Chat, ChatData, ChatFile, ChatName, Message
from src.media_locator import find_media_file, process_media_dependencies
from src.vfs import VFS


def test_find_media_file_same_dir(tmp_path: Path) -> None:
    """Test finding media file in the same directory as chat file."""
    vfs = VFS()
    vfs.base_path = tmp_path

    # Create chat file
    chat_file_path = "export1/_chat.txt"
    chat_file = ChatFile(
        path=chat_file_path,
        size=100,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(chat_file)

    # Create media file in same directory
    media_file = ChatFile(
        path="export1/photo.jpg",
        size=200,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(media_file)

    # Create media file in different directory
    other_media = ChatFile(
        path="export2/photo.jpg",
        size=300,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(other_media)

    # Should find media in same directory
    result = find_media_file(vfs, "photo.jpg", chat_file_path)
    assert result is not None
    assert result.path == "export1/photo.jpg"


def test_find_media_file_fallback(tmp_path: Path) -> None:
    """Test finding media file by name when not in same directory."""
    vfs = VFS()
    vfs.base_path = tmp_path

    chat_file = ChatFile(
        path="export1/_chat.txt",
        size=100,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(chat_file)

    media_file = ChatFile(
        path="export2/photo.jpg",
        size=200,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(media_file)

    # Should find media in other directory
    result = find_media_file(vfs, "photo.jpg", chat_file.path)
    assert result is not None
    assert result.path == "export2/photo.jpg"


def test_process_media_dependencies(tmp_path: Path) -> None:
    """Test processing media dependencies across multiple messages."""
    vfs = VFS()
    vfs.base_path = tmp_path

    chat_file = ChatFile(
        path="export1/_chat.txt",
        size=100,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(chat_file)

    media1 = ChatFile(
        path="export1/photo1.jpg",
        size=200,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(media1)

    media2 = ChatFile(
        path="export2/photo2.jpg",
        size=300,
        modification_timestamp=1000.0,
        exists=True,
    )
    vfs.add_file(media2)

    # Create chat data with messages referencing media
    chat_data = ChatData()
    chat = Chat(chat_name=ChatName("Test Chat"))
    chat_data.chats[chat.chat_name] = chat

    # Add messages with media references
    msg1 = Message(
        timestamp="1.1.2022 12:00",
        sender="User1",
        content="Photo 1",
        year=2022,
        input_file_id=chat_file.id,
        media_name="photo1.jpg",
    )
    msg2 = Message(
        timestamp="1.1.2022 12:01",
        sender="User2",
        content="Photo 2",
        year=2022,
        input_file_id=chat_file.id,
        media_name="photo2.jpg",
    )
    msg3 = Message(
        timestamp="1.1.2022 12:02",
        sender="User1",
        content="Photo 1 again",
        year=2022,
        input_file_id=chat_file.id,
        media_name="photo1.jpg",  # Duplicate reference
    )

    chat.messages.extend([msg1, msg2, msg3])

    # Process media dependencies
    process_media_dependencies(chat_data, vfs)

    # Verify output file dependencies
    assert 2022 in chat.output_files
    media_deps = chat.output_files[2022].media_dependencies
    assert len(media_deps) == 2  # Should only have two unique media files
    assert media_deps["photo1.jpg"] == media1.id
    assert media_deps["photo2.jpg"] == media2.id
