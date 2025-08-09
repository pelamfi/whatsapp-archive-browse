"""
Unit tests for HTML generation helper functions.
Full HTML generation tests will be added in step 11.
"""

from src.chat_data import Chat, ChatName, MediaReference, Message
from src.html_generator import create_chat_index_html, create_main_index_html, create_year_html, format_message_html


def test_format_message_html() -> None:
    """Test message HTML formatting with and without media"""
    # Message without media
    message = Message(timestamp="12:00", sender="Alice", content="Hello!", year=2025)
    html = format_message_html(message)
    assert "12:00" in html
    assert "Alice" in html
    assert "Hello!" in html
    assert "media" not in html

    # Message with media
    message.media = MediaReference(raw_file_name="test.jpg", output_path="media/test.jpg")
    html = format_message_html(message)
    assert 'img src="media/test.jpg"' in html

    # Message with missing media
    message.media.output_path = None
    html = format_message_html(message)
    assert "[Media file not available]" in html


def test_create_year_html() -> None:
    """Test year page HTML generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    messages = [
        Message(timestamp="12:00", sender="Alice", content="Hi", year=2025),
        Message(timestamp="12:01", sender="Bob", content="Hello", year=2025),
    ]
    html = create_year_html(chat, 2025, messages)
    assert "Test Chat" in html
    assert "2025" in html
    assert "Hi" in html
    assert "Hello" in html
    assert 'class="message"' in html


def test_create_chat_index_html() -> None:
    """Test chat index page generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    years = {2023, 2024, 2025}
    html = create_chat_index_html(chat, years)
    assert "Test Chat" in html
    assert "2023.html" in html
    assert "2024.html" in html
    assert "2025.html" in html
    assert "Back to chats" in html


def test_create_main_index_html() -> None:
    """Test main index page generation"""
    chats = {"Chat One": {2023, 2024}, "Chat Two": {2024, 2025}}
    html = create_main_index_html(chats, "2025-08-03 14:28:38")
    assert "Chat One" in html
    assert "Chat Two" in html
    assert "Generated on" in html
    assert 'href="Chat One/index.html"' in html
