"""
Tests for the message processor module.
"""

from pathlib import Path

from src.chat_data import ChatFile, ChatName
from src.message_processor import process_messages
from src.vfs import VFS


def test_process_messages_basic(tmp_path: Path) -> None:
    """Test basic message processing with two chat files for same chat."""
    vfs = VFS()
    vfs.base_path = tmp_path

    # Create 3 chat files with overlapping messages
    for file_index in range(1, 4):  # 1, 2, 3
        relative_path: Path = Path(f"export{file_index}/_chat.txt")
        export_folder = tmp_path / relative_path.parent
        export_folder.mkdir()
        chat_path = export_folder / "_chat.txt"
        with open(chat_path, "w", encoding="utf-8") as f:
            f.write("[12.3.2022 klo 14.08.18] Space Rocket: Test chat\n")
            for message_index in range(max(1, file_index - 1), file_index + 1):  # create duplicate overlapping messages
                f.write(f"[12.3.2022 klo 14.09.09] Tester: Message {message_index}\n")

        chat_file = ChatFile(
            path=str(relative_path),
            size=chat_path.stat().st_size,
            modification_timestamp=1000.0 + file_index,  # Ensure order
            exists=True,
        )
        vfs.add_file(chat_file)

    result = process_messages(vfs)
    assert len(result.chats) == 1
    chat = result.chats[ChatName(name="Space Rocket")]
    assert len(chat.messages) == 4  # Common message + unique message from each file

    def assertMessageContent(message_index: int, content: str, file: str) -> None:
        assert chat.messages[message_index].content == content, f"Message {message_index} content mismatch"
        message_file = vfs.get_by_id(chat.messages[message_index].input_file_id)
        assert message_file is not None, f"message_index={message_index} source file not found"
        assert message_file.path == file, f"message_index={message_index} source file path mismatch"

    assertMessageContent(0, "Test chat\n", "export1/_chat.txt")  # First message from oldest file
    assertMessageContent(1, "Message 1\n", "export1/_chat.txt")  # Second message from first file
    assertMessageContent(2, "Message 2\n", "export2/_chat.txt")  # Message from second file that is also in 3rd file
    assertMessageContent(3, "Message 3\n", "export3/_chat.txt")  # Unique message from third file
