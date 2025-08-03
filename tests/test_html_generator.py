"""
Unit tests for HTML generation helper functions.
Full HTML generation tests will be added in step 11.
"""

import pytest
from src.html_generator import (
    escape_html,
    format_message_html,
    create_year_html,
    create_chat_index_html,
    create_main_index_html
)
from src.chat_data import Message, Chat, ChatName, MediaReference

def test_escape_html():
    """Test HTML escaping of special characters"""
    input_text = 'Test with <tags> & "quotes" and \'apostrophes\''
    expected = 'Test with &lt;tags&gt; &amp; &quot;quotes&quot; and &#39;apostrophes&#39;'
    assert escape_html(input_text) == expected

def test_format_message_html():
    """Test message HTML formatting with and without media"""
    # Message without media
    message = Message(
        timestamp="12:00",
        sender="Alice",
        content="Hello!",
        year=2025
    )
    html = format_message_html(message)
    assert "[12:00]" in html
    assert "Alice" in html
    assert "Hello!" in html
    assert "media" not in html

    # Message with media
    message.media = MediaReference(
        raw_file_name="test.jpg",
        output_path="media/test.jpg"
    )
    html = format_message_html(message)
    assert 'img src="media/test.jpg"' in html

    # Message with missing media
    message.media.output_path = None
    html = format_message_html(message)
    assert "[Media file not available]" in html

def test_create_year_html():
    """Test year page HTML generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    messages = [
        Message(timestamp="12:00", sender="Alice", content="Hi", year=2025),
        Message(timestamp="12:01", sender="Bob", content="Hello", year=2025)
    ]
    html = create_year_html(chat, 2025, messages)
    assert "Test Chat" in html
    assert "2025" in html
    assert "Hi" in html
    assert "Hello" in html
    assert 'class="message"' in html

def test_create_chat_index_html():
    """Test chat index page generation"""
    chat = Chat(chat_name=ChatName("Test Chat"))
    years = {2023, 2024, 2025}
    html = create_chat_index_html(chat, years)
    assert "Test Chat" in html
    assert "2023.html" in html
    assert "2024.html" in html
    assert "2025.html" in html
    assert "Back to chats" in html

def test_create_main_index_html():
    """Test main index page generation"""
    chats = {
        "Chat One": {2023, 2024},
        "Chat Two": {2024, 2025}
    }
    html = create_main_index_html(chats)
    assert "Chat One" in html
    assert "Chat Two" in html
    assert "Generated on" in html
    assert 'href="Chat One/index.html"' in html
