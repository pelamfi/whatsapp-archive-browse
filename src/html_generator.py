"""
HTML Generation Module

This module handles the generation of HTML files for WhatsApp chat archives.
The generation is driven by OutputFile objects in the ChatData structure, which
indicate which files need to be (re)generated.

Design decisions:
1. Simple static HTML
   - No JavaScript or complex CSS
   - Maximum compatibility and longevity
   - Easy to archive and move around

2. Incremental Generation
   - Only regenerate YYYY.html files marked with generate=True
   - Always regenerate index.html files as they're small and simple
   - CSS is now embedded directly in HTML files for maximum compatibility

3. File Structure
   - Top level index.html with links to all chats
   - Per-chat directories with:
     - chat_name/index.html listing years
     - chat_name/YYYY.html for each year
     - chat_name/media/ for media files
   - Each HTML file is now self-contained with embedded CSS

4. Testing Strategy
   - Unit tests for HTML generation helper functions
   - Integration tests for full generation
   - CSS is now embedded directly in HTML files for maximum compatibility
"""

import html
import logging
import os
import shutil
from typing import Dict, Set, Tuple

from src.chat_data import Chat, ChatData, ChatFile, ChatName, Message


def load_css_content() -> Tuple[str, ChatFile]:
    """Load CSS content and return with its ChatFile."""
    css_path: str = os.path.join(os.path.dirname(__file__), "browseability-generator.css")
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    css_file = ChatFile(
        path="browseability-generator.css",
        size=os.path.getsize(css_path),
        modification_timestamp=os.path.getmtime(css_path),
    )

    return content, css_file


def copy_media_file(input_dir: str, chat_dir: str, media_file: ChatFile) -> bool:
    """Copy a media file from input to output directory."""
    src_path = os.path.join(input_dir, media_file.path)
    if not os.path.exists(src_path):
        logging.warning(f"Media file not found: {src_path}")
        return False

    dst_path = os.path.join(chat_dir, "media", os.path.basename(media_file.path))

    try:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy(src_path, dst_path)
        return True
    except (IOError, OSError) as e:
        logging.error(f"Failed to copy media file {src_path}: {e}")
        return False


def format_content_html(text: str) -> str:
    """Format message content for HTML, escaping HTML and converting newlines to <br> tags."""
    # First escape HTML special characters
    escaped = html.escape(text)
    # Then convert newlines to HTML line breaks with newlines for readable source
    # Don't add <br> for final new line.
    return escaped.rstrip("\n").replace("\n", "<br>\n")


def format_message_html(message: Message, chat_data: ChatData) -> str:
    """Format a single message as HTML."""
    media_html = ""
    if message.media_name:
        # Media file name will be used directly in the HTML
        media_html = f'<div class="media"><img src="media/{html.escape(message.media_name)}" alt="Media"></div>'

    return f"""
    <div class="message">
        <div class="metadata">
            <span class="timestamp">{html.escape(message.timestamp)}</span>
            <span class="sender">{html.escape(message.sender)}</span>
        </div>
        <div class="content">{format_content_html(message.content)}</div>
        {media_html}
    </div>
    """


def create_year_html(chat: Chat, year: int, messages: list[Message], chat_data: ChatData, css_content: str) -> str:
    """Generate HTML for a specific year of chat messages."""
    messages_html = "\n".join(format_message_html(msg, chat_data) for msg in messages if msg.year == year)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{html.escape(chat.chat_name.name)} - {year}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <h1>{html.escape(chat.chat_name.name)}</h1>
    <h2>Messages from {year}</h2>
    <nav><a href="index.html" class="nav-link">← Back to years</a></nav>
    <div class="messages">
        {messages_html}
    </div>
</body>
</html>"""


def create_chat_index_html(chat: Chat, years: Set[int], css_content: str) -> str:
    """Generate index.html for a specific chat directory."""
    years_html = "\n".join(f'<li><a href="{year}.html">{year}</a></li>' for year in sorted(years))

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{html.escape(chat.chat_name.name)}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <h1>{html.escape(chat.chat_name.name)}</h1>
    <nav><a href="../index.html" class="nav-link">← Back to chats</a></nav>
    <h2>Messages by Year</h2>
    <ul class="year-list">
        {years_html}
    </ul>
</body>
</html>"""


def create_main_index_html(chats: Dict[ChatName, Set[int]], timestamp: str, css_content: str) -> str:
    """Generate main index.html listing all chats."""

    chat_names: list[str] = sorted(name.name for name in chats.keys())
    chats_html = "\n".join(
        f'<li><a href="{html.escape(name)}/index.html">{html.escape(name)}</a></li>' for name in chat_names
    )

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WhatsApp Chats</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <h1>WhatsApp Chats</h1>
    <ul class="chat-list">
        {chats_html}
    </ul>
    <p><small>Generated on {timestamp}</small></p>
</body>
</html>"""


def generate_html(chat_data: ChatData, input_dir: str, output_dir: str) -> None:
    """Generate HTML files for chats using ChatData."""
    # Prepare output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load CSS content and add to input files
    css_content, css_file = load_css_content()
    chat_data.input_files[css_file.id] = css_file

    # Track which chats have which years
    chat_years: Dict[ChatName, Set[int]] = {}

    # Process each chat
    for chat_name, chat in chat_data.chats.items():
        chat_dir = os.path.join(output_dir, chat_name.name)
        os.makedirs(chat_dir, exist_ok=True)
        os.makedirs(os.path.join(chat_dir, "media"), exist_ok=True)

        for year, output_file in chat.output_files.items():
            if not output_file.generate:
                continue

            # copy media files for files that need updating
            # TODO: Avoid copying media files that exist in old data too. Need additional flag for that.
            for media_file_id in output_file.media_dependencies.values():
                if media_file_id in chat_data.input_files:
                    media_file = chat_data.input_files[media_file_id]
                    copy_media_file(input_dir, chat_dir, media_file)

            # Generate year files that need updating
            year_html = create_year_html(chat, year, chat.messages, chat_data, css_content)
            with open(os.path.join(chat_dir, f"{year}.html"), "w", encoding="utf-8") as f:
                f.write(year_html)

        # Create chat index
        year_set: set[int] = set(chat.output_files.keys())
        chat_index = create_chat_index_html(chat, year_set, css_content)
        with open(os.path.join(chat_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(chat_index)

        chat_years[chat_name] = year_set

    # Create main index
    main_index = create_main_index_html(chat_years, chat_data.timestamp, css_content)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_index)
