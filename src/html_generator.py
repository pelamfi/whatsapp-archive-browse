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
   - Always copy CSS files as they're small and might be updated

3. File Structure
   - Top level index.html with links to all chats
   - Per-chat directories with:
     - chat_name/index.html listing years
     - chat_name/YYYY.html for each year
     - chat_name/media/ for media files
   - CSS file copied to each chat directory to make them self-contained

4. Testing Strategy
   - Unit tests for HTML generation helper functions
   - Integration tests in step 11 for full generation
"""

import logging
import os
import shutil
from typing import Dict, List, Set

from src.chat_data import Chat, ChatData, MediaReference, Message


def copy_media_file(input_dir: str, chat_dir: str, media_ref: MediaReference) -> bool:
    """
    Copy a media file from input to output directory and update its output path.

    Args:
        input_dir: Root input directory
        chat_dir: Output directory for the chat
        media_ref: MediaReference to process

    Returns:
        bool: True if file was copied successfully, False if file is missing
    """
    if not media_ref.input_path:
        return False

    # Construct paths
    src_path = os.path.join(input_dir, media_ref.input_path.path)
    if not os.path.exists(src_path):
        logging.warning(f"Media file not found: {src_path}")
        return False

    # Use the original filename for the output
    dst_path = os.path.join(chat_dir, "media", media_ref.raw_file_name)

    try:
        # Create media directory if it doesn't exist
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # Copy the file and update the reference
        shutil.copy2(src_path, dst_path)
        media_ref.output_path = f"media/{media_ref.raw_file_name}"
        return True
    except (IOError, OSError) as e:
        logging.error(f"Failed to copy media file {src_path}: {e}")
        return False


def escape_html(text: str) -> str:
    """Escape special characters in text for HTML output."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def format_message_html(message: Message) -> str:
    """Format a single message as HTML."""
    media_html = ""
    if message.media:
        if message.media.output_path:
            media_html = f'<div class="media"><img src="{message.media.output_path}" alt="Media"></div>'
        else:
            media_html = '<div class="media">[Media file not available]</div>'

    return f"""
    <div class="message">
        <div class="metadata">
            <span class="timestamp">[{escape_html(message.timestamp)}]</span>
            <span class="sender">{escape_html(message.sender)}</span>
        </div>
        <div class="content">{escape_html(message.content)}</div>
        {media_html}
    </div>
    """


def create_year_html(chat: Chat, year: int, messages: List[Message]) -> str:
    """Generate HTML for a specific year of chat messages."""
    messages_html = "\n".join(format_message_html(msg) for msg in messages)
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{escape_html(chat.chat_name.name)} - {year}</title>
    <link rel="stylesheet" href="browseability-generator.css">
</head>
<body>
    <h1>{escape_html(chat.chat_name.name)}</h1>
    <h2>Messages from {year}</h2>
    <p><a href="index.html">Back to years</a></p>
    <div class="messages">
        {messages_html}
    </div>
</body>
</html>"""


def create_chat_index_html(chat: Chat, years: Set[int]) -> str:
    """Generate index.html for a specific chat directory."""
    years_html = "\n".join(f'<li><a href="{year}.html">{year}</a></li>' for year in sorted(years))
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{escape_html(chat.chat_name.name)}</title>
    <link rel="stylesheet" href="browseability-generator.css">
</head>
<body>
    <h1>{escape_html(chat.chat_name.name)}</h1>
    <p><a href="../index.html">Back to chats</a></p>
    <h2>Messages by Year</h2>
    <ul class="year-list">
        {years_html}
    </ul>
</body>
</html>"""


def create_main_index_html(chats: Dict[str, Set[int]], timestamp: str) -> str:
    """Generate main index.html listing all chats."""
    chats_html = "\n".join(
        f'<li><a href="{escape_html(name)}/index.html">{escape_html(name)}</a></li>' for name in sorted(chats.keys())
    )
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WhatsApp Chats</title>
    <link rel="stylesheet" href="browseability-generator.css">
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
    """
    Generate HTML files for chats based on OutputFile flags in chat_data.
    Always regenerates index.html files and copies CSS.
    """
    # Copy CSS to root and prepare directory
    os.makedirs(output_dir, exist_ok=True)
    css_path = os.path.join(os.path.dirname(__file__), "browseability-generator.css")
    shutil.copy(css_path, os.path.join(output_dir, "browseability-generator.css"))

    # Track which chats have which years for index generation
    chat_years: Dict[str, Set[int]] = {}

    # Process each chat
    for chat_name, chat in chat_data.chats.items():
        chat_dir = os.path.join(output_dir, chat_name.name)
        os.makedirs(chat_dir, exist_ok=True)
        os.makedirs(os.path.join(chat_dir, "media"), exist_ok=True)

        # Copy CSS to chat directory
        shutil.copy(css_path, os.path.join(chat_dir, "browseability-generator.css"))

        years: set[int] = set()
        for year, output_file in chat.output_files.items():
            years.add(year)
            if not output_file.generate:
                continue

            # Filter messages for this year
            year_messages = [msg for msg in chat.messages if msg.year == year]
            if not year_messages:
                continue

            # Generate YYYY.html
            year_html = create_year_html(chat, year, year_messages)
            with open(os.path.join(chat_dir, f"{year}.html"), "w", encoding="utf-8") as f:
                f.write(year_html)

        # Generate chat index.html
        chat_years[chat_name.name] = years
        chat_index = create_chat_index_html(chat, years)
        with open(os.path.join(chat_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(chat_index)

    # Generate main index.html
    main_index = create_main_index_html(chat_years, chat_data.timestamp)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_index)

    # Copy all referenced media files
    print("Copying media files...")
    for chat in chat_data.chats.values():
        chat_dir = os.path.join(output_dir, chat.chat_name.name)
        for msg in chat.messages:
            if msg.media:
                copy_media_file(input_dir, chat_dir, msg.media)
