"""
Unit tests for HTML generation helper functions with ChatData.
"""

from pathlib import Path

from src.chat_data import Chat, ChatData, ChatFile, ChatName, Message
from src.html_generator import (
    create_chat_index_html,
    create_main_index_html,
    create_year_html,
    format_message_html,
    load_css_content,
)


def test_format_message_html(tmp_path: Path) -> None:
    """Test message HTML formatting with and without media"""
    chat_data = ChatData()
    # Add chat data with media
    media_file = ChatFile(
        path="test.jpg",
        size=100,
        modification_timestamp=1234567890.0,
    )
    chat_data.input_files[media_file.id] = media_file

    # Message without media
    message = Message(timestamp="12:00", sender="Alice", content="Hello!", year=2025)
    html = format_message_html(message, chat_data)
    assert "12:00" in html
    assert "Alice" in html
    assert "Hello!" in html
    assert "media" not in html

    # Message with media
    message = Message(
        timestamp="12:00",
        sender="Alice",
        content="",
        year=2025,
        media_name="test.jpg",
    )
    html = format_message_html(message, chat_data)
    assert 'img src="media/test.jpg"' in html


def test_create_year_html(tmp_path: Path) -> None:
    """Test year page HTML generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    messages = [
        Message(timestamp="12:00", sender="Alice", content="Hi", year=2025),
        Message(timestamp="12:01", sender="Bob", content="Hello", year=2025),
    ]
    chat_data = ChatData()
    css_content = "body { color: black; }"

    html = create_year_html(chat, 2025, messages, chat_data, css_content)
    assert "Test Chat" in html
    assert "2025" in html
    assert "Hi" in html
    assert "Hello" in html
    assert 'class="message"' in html
    assert css_content in html


def test_create_chat_index_html(tmp_path: Path) -> None:
    """Test chat index page generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    years = {2023, 2024, 2025}
    css_content = "body { color: black; }"

    html = create_chat_index_html(chat, years, css_content)
    assert "Test Chat" in html
    assert "2023.html" in html
    assert "2024.html" in html
    assert "2025.html" in html
    assert "Back to chats" in html
    assert css_content in html


def test_create_main_index_html(tmp_path: Path) -> None:
    """Test main index page generation"""
    chats: dict[ChatName, set[int]] = {ChatName("Chat One"): {2023, 2024}, ChatName("Chat Two"): {2024, 2025}}
    css_content = "body { color: black; }"

    html = create_main_index_html(chats, "2025-08-03 14:28:38", css_content)
    assert "Chat One" in html
    assert "Chat Two" in html
    assert "Generated on" in html
    assert 'href="Chat One/index.html"' in html
    assert css_content in html


def test_load_css_content(tmp_path: Path) -> None:
    """Test loading CSS content and ChatFile creation"""
    css_content, css_file = load_css_content()
    assert "body {" in css_content
    assert css_file.path == "src/resources/browseability-generator.css"
    assert css_file.size > 0
    assert css_file.modification_timestamp == 1620000000.0  # Check for fixed timestamp
    css_content, css_file = load_css_content()
    assert "body {" in css_content
    assert css_file.path == "src/resources/browseability-generator.css"
    assert css_file.size > 0
    assert css_file.modification_timestamp > 0
