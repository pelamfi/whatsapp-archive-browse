"""
Module for parsing WhatsApp chat export files.
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple

from src.chat_data2 import Chat2, ChatFile2, ChatFileID, ChatName2, Message2


def parse_chat_line(line: str) -> Optional[Tuple[str, str, str]]:
    """Parse a chat line into (timestamp, sender, content) or None if not a message line."""
    if not line.startswith("["):
        return None

    # Try to match timestamp inside square brackets
    timestamp_match = re.match(r"\[(.*?)\]", line)
    if not timestamp_match:
        return None

    timestamp = timestamp_match.group(1)
    rest = line[timestamp_match.end() :].strip()

    # Try to find sender and content split by first colon
    parts = rest.split(":", 1)
    if len(parts) != 2:
        return None

    sender = parts[0].strip()
    content = parts[1].strip()

    return timestamp, sender, content


def extract_year_from_timestamp(timestamp: str) -> int:
    """Extract year from timestamp string, using heuristic parsing."""
    try:
        # Try various common formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
            try:
                return datetime.strptime(timestamp, fmt).year
            except ValueError:
                continue

        # Fallback: try to find 4-digit year anywhere in string
        year_match = re.search(r"\b(20\d{2})\b", timestamp)
        if year_match:
            return int(year_match.group(1))

        raise ValueError(f"Could not extract year from timestamp: {timestamp}")
    except Exception as e:
        print(f"Warning: Failed to parse year from timestamp {timestamp}: {e}")
        # Default to current year as fallback
        return datetime.now().year


def detect_media_reference(content: str) -> Optional[str]:
    """Try to extract media filename from message content."""
    # Common patterns in WhatsApp exports
    patterns = [
        r"<attached: (.+?)>",
        r"\(file attached: (.+?)\)",
        r"\[file: (.+?)\]",
    ]

    for pattern in patterns:
        if match := re.search(pattern, content):
            return match.group(1)

    return None


def parse_chat_file(file_path: str, chat_file: ChatFile2) -> Optional[Tuple[Chat2, dict[ChatFileID, ChatFile2]]]:
    """
    Parse a WhatsApp chat export file.

    Args:
        file_path: Path to _chat.txt file to parse
        chat_file: ChatFile2 object representing the input file

    Returns:
        Tuple of (Chat2 object, dict of input files) if successful, None if parsing fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Failed to read chat file {file_path}: {e}")
        return None

    messages: list[Message2] = []
    input_files: dict[ChatFileID, ChatFile2] = {chat_file.id: chat_file}

    for line in lines:
        if parsed := parse_chat_line(line.strip()):
            timestamp, sender, content = parsed
            year = extract_year_from_timestamp(timestamp)

            # Check for media reference
            media_file_id: Optional[ChatFileID] = None
            if media_filename := detect_media_reference(content):
                # Note: We don't create the ChatFile2 here, that's done by input_scanner
                # during media file discovery. We just store the reference.
                content = content.replace(f"<attached: {media_filename}>", "").strip()

            messages.append(
                Message2(
                    timestamp=timestamp,
                    sender=sender,
                    content=content,
                    year=year,
                    input_file_id=chat_file.id,
                    media_file_id=media_file_id,
                )
            )

    if not messages:
        return None

    # Try to extract chat name from path
    chat_name = ChatName2(name=os.path.basename(os.path.dirname(file_path)))

    # Create chat object
    chat = Chat2(
        chat_name=chat_name,
        messages=messages,
    )

    return chat, input_files
