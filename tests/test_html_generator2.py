"""
Unit tests for HTML generation helper functions with ChatData2.
"""

from pathlib import Path

from src.chat_data2 import Chat2, ChatData2, ChatFile2, ChatName2, Message2
from src.html_generator2 import (create_chat_index_html2, create_main_index_html2,
                               create_year_html2, format_message_html2, load_css_content2)


def test_format_message_html2(tmp_path: Path) -> None:
    """Test message HTML formatting with and without media"""
    chat_data = ChatData2()
    # Add chat data with media
    media_file = ChatFile2(
        path="test.jpg",
        size=100,
        modification_timestamp=1234567890.0,
    )
    chat_data.input_files[media_file.id] = media_file

    # Message without media
    message = Message2(timestamp="12:00", sender="Alice", content="Hello!", year=2025)
    html = format_message_html2(message, chat_data)
    assert "12:00" in html
    assert "Alice" in html
    assert "Hello!" in html
    assert "media" not in html

    # Message with media
    message = Message2(
        timestamp="12:00",
        sender="Alice",
        content="",
        year=2025,
        media_file_id=media_file.id,
    )
    html = format_message_html2(message, chat_data)
    assert 'img src="media/test.jpg"' in html


def test_create_year_html2(tmp_path: Path) -> None:
    """Test year page HTML generation"""
    chat = Chat2(chat_name=ChatName2("Test Chat"))
    messages = [
        Message2(timestamp="12:00", sender="Alice", content="Hi", year=2025),
        Message2(timestamp="12:01", sender="Bob", content="Hello", year=2025),
    ]
    chat_data = ChatData2()
    css_content = "body { color: black; }"

    html = create_year_html2(chat, 2025, messages, chat_data, css_content)
    assert "Test Chat" in html
    assert "2025" in html
    assert "Hi" in html
    assert "Hello" in html
    assert 'class="message"' in html
    assert css_content in html


def test_create_chat_index_html2(tmp_path: Path) -> None:
    """Test chat index page generation"""
    chat = Chat2(chat_name=ChatName2("Test Chat"))
    years = {2023, 2024, 2025}
    css_content = "body { color: black; }"

    html = create_chat_index_html2(chat, years, css_content)
    assert "Test Chat" in html
    assert "2023.html" in html
    assert "2024.html" in html
    assert "2025.html" in html
    assert "Back to chats" in html
    assert css_content in html


def test_create_main_index_html2(tmp_path: Path) -> None:
    """Test main index page generation"""
    chats = {"Chat One": {2023, 2024}, "Chat Two": {2024, 2025}}
    css_content = "body { color: black; }"

    html = create_main_index_html2(chats, "2025-08-03 14:28:38", css_content)
    assert "Chat One" in html
    assert "Chat Two" in html
    assert "Generated on" in html
    assert 'href="Chat One/index.html"' in html
    assert css_content in html


def test_load_css_content2(tmp_path: Path) -> None:
    """Test loading CSS content and ChatFile2 creation"""
    css_content, css_file = load_css_content2()
    assert "body {" in css_content
    assert css_file.path == "browseability-generator.css"
    assert css_file.size > 0
    assert css_file.modification_timestamp > 0
