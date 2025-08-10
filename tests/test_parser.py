"""
Tests for the parser module using ChatData structures.
"""

from pathlib import Path

from src.chat_data import ChatFile, ChatName
from src.parser import parse_chat_file
from src.vfs import VFS


def test_parse_chat_file_smoke_test(tmp_path: Path) -> None:
    """Basic smoke test with simple chat messages."""
    # Create test chat file
    chat_path = tmp_path / "test_chat.txt"
    with open(chat_path, "w", encoding="utf-8") as f:
        f.write("[12.3.2022 klo 14.08.18] Space Rocket: Test chat\n")
        f.write("[12.3.2022 klo 14.09.09] Matias Virtanen: Hello world\n")

    # Set up VFS
    input_file = ChatFile(
        path="test_chat.txt",
        size=chat_path.stat().st_size,
        modification_timestamp=chat_path.stat().st_mtime,
    )
    vfs = VFS(tmp_path)
    vfs.add_file(input_file)

    chat = parse_chat_file(vfs, input_file)
    assert chat is not None

    assert chat.chat_name == ChatName(name="Space Rocket")
    assert len(chat.messages) == 2
    assert chat.messages[0].content == "Test chat\n"
    assert chat.messages[0].year == 2022
    assert chat.messages[1].sender == "Matias Virtanen"
    assert chat.messages[1].content == "Hello world\n"


def test_parse_chat_file_u00e_and_tilde_handling(tmp_path: Path) -> None:
    """Test U+200E character removal and tilde wrapping as per regex design."""
    # Create test chat file
    chat_path = tmp_path / "test_chat.txt"
    with open(chat_path, "w", encoding="utf-8") as f:
        # U+200E at start of line and after colon - should be removed
        f.write("‎[12.3.2022 klo 14.08.18] Space Rocket: ‎Messages are encrypted\n")
        # Tilde wrapping with U+200E - tilde should be stripped from sender, U+200E removed
        f.write("[12.3.2022 klo 14.10.56] ~ Juuso Kivi: ‎~ Juuso Kivi lisättiin\n")
        # U+200E in content should be preserved (not at special locations)
        f.write("[12.3.2022 klo 14.15.00] User: Content with ‎U+200E in middle\n")

    input_file = ChatFile(
        path="test_chat.txt",
        size=chat_path.stat().st_size,
        modification_timestamp=chat_path.stat().st_mtime,
    )
    vfs = VFS(tmp_path)
    vfs.add_file(input_file)

    chat = parse_chat_file(vfs, input_file)
    assert chat is not None
    assert len(chat.messages) == 3

    # First message: U+200E removed from start and after colon, content preserved
    assert chat.messages[0].content == "Messages are encrypted\n"

    # Second message: tilde stripped from sender, U+200E after colon removed
    assert chat.messages[1].sender == "Juuso Kivi"  # Tilde stripped
    assert chat.messages[1].content == "Juuso Kivi lisättiin\n"  # Content preserved

    # Third message: U+200E in middle of content should be preserved
    assert chat.messages[2].content == "Content with ‎U+200E in middle\n"


def test_parse_chat_file_complex_scenarios(tmp_path: Path) -> None:
    """Test multiline content, media references, year extraction, and edge cases."""
    # Create test chat file
    chat_path = tmp_path / "test_chat.txt"
    with open(chat_path, "w", encoding="utf-8") as f:
        f.write("[12.3.2022 klo 14.08.18] Space Rocket: ‎Test chat\n")
        # Multiline message
        f.write("[12.3.2022 klo 14.20.39] Sami Ström: First line\n")
        f.write("Second line with link\n")
        f.write("https://example.com/test\n")
        f.write("Third line\n")
        # Media reference
        f.write("[13.3.2022 klo 14.17.25] Sami Ström: ‎<attached: photo.jpg>foobar\n")
        # Different year
        f.write("[31.1.2024 klo 8.56.58] Matias Virtanen: Message from 2024\n")

    input_file = ChatFile(
        path="test_chat.txt",
        size=chat_path.stat().st_size,
        modification_timestamp=chat_path.stat().st_mtime,
    )
    vfs = VFS(tmp_path)
    vfs.add_file(input_file)

    chat = parse_chat_file(vfs, input_file)
    assert chat is not None
    assert len(chat.messages) == 4

    # Check multiline content is properly joined
    expected_multiline = "First line\nSecond line with link\nhttps://example.com/test\nThird line\n"
    assert chat.messages[1].content == expected_multiline

    # Check media reference
    assert chat.messages[2].media_name == "photo.jpg"  # Media filename extracted
    assert chat.messages[2].content == "foobar\n"  # U+200E removed from the beginning of message, linefeed preserved

    # Check year extraction from different years
    assert chat.messages[0].year == 2022
    assert chat.messages[3].year == 2024
