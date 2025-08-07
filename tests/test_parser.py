from src.chat_data import ChatFile, ChatName
from src.parser import parse_chat_lines


def test_parse_chat_lines_smoke_test() -> None:
    """Basic smoke test with simple chat messages."""
    lines = [
        "[12.3.2022 klo 14.08.18] Space Rocket: Test chat",
        "[12.3.2022 klo 14.09.09] Matias Virtanen: Hello world",
    ]
    input_file = ChatFile(path="test_chat.txt")

    chat = parse_chat_lines(lines, input_file)

    assert chat is not None
    assert chat.chat_name == ChatName(name="Space Rocket")
    assert len(chat.messages) == 2
    assert chat.messages[0].content == "Test chat"
    assert chat.messages[0].year == 2022
    assert chat.messages[1].sender == "Matias Virtanen"
    assert chat.messages[1].content == "Hello world"


def test_parse_chat_lines_u200e_and_tilde_handling() -> None:
    """Test U+200E character removal and tilde wrapping as per regex design."""
    lines = [
        # U+200E at start of line and after colon - should be removed
        "‎[12.3.2022 klo 14.08.18] Space Rocket: ‎Messages are encrypted",
        # Tilde wrapping with U+200E - tilde should be stripped from sender, U+200E removed
        "[12.3.2022 klo 14.10.56] ~ Juuso Kivi: ‎~ Juuso Kivi lisättiin",
        # U+200E in content should be preserved (not at special locations)
        "[12.3.2022 klo 14.15.00] User: Content with ‎U+200E in middle",
    ]
    input_file = ChatFile(path="test_chat.txt")

    chat = parse_chat_lines(lines, input_file)

    assert chat is not None
    assert len(chat.messages) == 3
    
    # First message: U+200E removed from start and after colon, content preserved
    assert chat.messages[0].content == "Messages are encrypted"
    
    # Second message: tilde stripped from sender, U+200E after colon removed
    assert chat.messages[1].sender == "Juuso Kivi"  # Tilde stripped
    assert chat.messages[1].content == "Juuso Kivi lisättiin"  # Content preserved
    
    # Third message: U+200E in middle of content should be preserved
    assert chat.messages[2].content == "Content with ‎U+200E in middle"


def test_parse_chat_lines_complex_scenarios() -> None:
    """Test multiline content, media references, year extraction, and edge cases."""
    lines = [
        "[12.3.2022 klo 14.08.18] Space Rocket: ‎Test chat",
        # Multiline message
        "[12.3.2022 klo 14.20.39] Sami Ström: First line",
        "Second line with link",
        "https://example.com/test",
        "Third line",
        # Media reference
        "[13.3.2022 klo 14.17.25] Sami Ström: ‎<liite: photo.jpg>",
        # Different year
        "[31.1.2024 klo 8.56.58] Matias Virtanen: Message from 2024",
    ]
    input_file = ChatFile(path="test_chat.txt")

    chat = parse_chat_lines(lines, input_file)

    assert chat is not None
    assert len(chat.messages) == 4
    
    # Check multiline content is properly joined
    expected_multiline = "First line\nSecond line with link\nhttps://example.com/test\nThird line"
    assert chat.messages[1].content == expected_multiline
    
    # Check media reference parsing
    assert chat.messages[2].media is not None
    assert chat.messages[2].media.raw_file_name == "photo.jpg"
    assert chat.messages[2].content == ""  # U+200E removed from the beginning of message
    
    # Check year extraction from different years
    assert chat.messages[0].year == 2022
    assert chat.messages[3].year == 2024
