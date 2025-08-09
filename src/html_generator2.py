"""
HTML Generation Module for ChatData2 structures.
"""

import html
import logging
import os
import shutil
from typing import Dict, Set, Tuple

from src.chat_data2 import Chat2, ChatData2, ChatFile2, Message2, OutputFile2


def load_css_content2() -> Tuple[str, ChatFile2]:
    """Load CSS content and return with its ChatFile2."""
    css_path = os.path.join(os.path.dirname(__file__), "browseability-generator.css")
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    css_file = ChatFile2(
        path="browseability-generator.css",
        size=os.path.getsize(css_path),
        modification_timestamp=os.path.getmtime(css_path),
    )

    return content, css_file


def copy_media_file2(input_dir: str, chat_dir: str, media_file: ChatFile2) -> bool:
    """Copy a media file from input to output directory."""
    src_path = os.path.join(input_dir, media_file.path)
    if not os.path.exists(src_path):
        logging.warning(f"Media file not found: {src_path}")
        return False

    dst_path = os.path.join(chat_dir, "media", os.path.basename(media_file.path))

    try:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        return True
    except (IOError, OSError) as e:
        logging.error(f"Failed to copy media file {src_path}: {e}")
        return False


def format_message_html2(message: Message2, chat_data: ChatData2) -> str:
    """Format a single message as HTML."""
    media_html = ""
    if message.media_file_id is not None and message.media_file_id in chat_data.input_files:
        media_file = chat_data.input_files[message.media_file_id]
        media_filename = os.path.basename(media_file.path)
        media_html = f'<div class="media"><img src="media/{html.escape(media_filename)}"></div>'

    return f"""
    <div class="message">
        <div class="metadata">
            <span class="timestamp">{html.escape(message.timestamp)}</span>
            <span class="sender">{html.escape(message.sender)}</span>
        </div>
        <div class="content">{html.escape(message.content)}</div>
        {media_html}
    </div>
    """


def create_year_html2(chat: Chat2, year: int, messages: list[Message2], chat_data: ChatData2, css_content: str) -> str:
    """Generate HTML for a specific year of chat messages."""
    messages_html = "\n".join(format_message_html2(msg, chat_data) for msg in messages if msg.year == year)

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


def create_chat_index_html2(chat: Chat2, years: Set[int], css_content: str) -> str:
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


def create_main_index_html2(chats: Dict[str, Set[int]], timestamp: str, css_content: str) -> str:
    """Generate main index.html listing all chats."""
    chats_html = "\n".join(
        f'<li><a href="{html.escape(name)}/index.html">{html.escape(name)}</a></li>' for name in sorted(chats.keys())
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


def generate_html2(chat_data: ChatData2, input_dir: str, output_dir: str) -> None:
    """Generate HTML files for chats using ChatData2."""
    # Prepare output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load CSS content and add to input files
    css_content, css_file = load_css_content2()
    chat_data.input_files[css_file.id] = css_file

    # Track which chats have which years
    chat_years: Dict[str, Set[int]] = {}

    # Process each chat
    for chat_name, chat in chat_data.chats.items():
        chat_dir = os.path.join(output_dir, chat_name.name)
        os.makedirs(chat_dir, exist_ok=True)
        os.makedirs(os.path.join(chat_dir, "media"), exist_ok=True)

        # Track years and copy media for this chat
        years: set[int] = set()

        # Copy media files for each message
        for msg in chat.messages:
            if msg.media_file_id is not None and msg.media_file_id in chat_data.input_files:
                media_file = chat_data.input_files[msg.media_file_id]
                if copy_media_file2(input_dir, chat_dir, media_file):
                    # Update output file dependencies
                    year = msg.year
                    if year not in chat.output_files:
                        chat.output_files[year] = OutputFile2(year=year)
                    output_file = chat.output_files[year]
                    output_file.media_dependencies[os.path.basename(media_file.path)] = msg.media_file_id

            years.add(msg.year)

        # Generate year files that need updating
        for year in years:
            if year not in chat.output_files:
                chat.output_files[year] = OutputFile2(year=year)

            output_file = chat.output_files[year]
            if output_file.generate:
                year_content = create_year_html2(chat, year, chat.messages, chat_data, css_content)
                with open(os.path.join(chat_dir, f"{year}.html"), "w", encoding="utf-8") as f:
                    f.write(year_content)

                # Update dependencies
                # Add chat_dependencies for every message
                for msg in chat.messages:
                    if msg.input_file_id and msg.year == year:
                        output_file.chat_dependencies.append(msg.input_file_id)
                output_file.css_dependency = css_file.id

        # Create chat index
        chat_index = create_chat_index_html2(chat, years, css_content)
        with open(os.path.join(chat_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(chat_index)

        chat_years[chat_name.name] = years

    # Create main index
    main_index = create_main_index_html2(chat_years, chat_data.timestamp, css_content)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_index)
