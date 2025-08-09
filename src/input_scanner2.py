"""
Scanner for WhatsApp chat exports using ChatData2 structures.
"""

import os
from typing import List, Optional

from src.chat_data2 import ChatData2, ChatFile2
from src.parser2 import parse_chat_file


def find_chat_files2(input_dir: str) -> List[ChatFile2]:
    """Find all _chat.txt files and return them as ChatFile2 objects."""
    chat_files: list[ChatFile2] = []

    for root, _, _ in os.walk(input_dir):
        path = os.path.join(root, "_chat.txt")
        if os.path.isfile(path):
            relative_path = os.path.relpath(path, input_dir)
            chat_files.append(
                ChatFile2(
                    path=relative_path,
                    size=os.path.getsize(path),
                    modification_timestamp=os.path.getmtime(path),
                )
            )

    return sorted(chat_files, key=lambda x: x.modification_timestamp)


def find_media_files2(input_dir: str, chat_file: ChatFile2, media_filename: str) -> Optional[ChatFile2]:
    """Try to find media file first in same directory as chat file, then anywhere in input."""
    chat_dir = os.path.dirname(os.path.join(input_dir, chat_file.path))
    media_path = os.path.join(chat_dir, media_filename)

    if os.path.exists(media_path):
        relative_path = os.path.relpath(media_path, input_dir)
        return ChatFile2(
            path=relative_path,
            size=os.path.getsize(media_path),
            modification_timestamp=os.path.getmtime(media_path),
        )

    # Try finding anywhere in input directory
    for root, _, files in os.walk(input_dir):
        if media_filename in files:
            media_path = os.path.join(root, media_filename)
            relative_path = os.path.relpath(media_path, input_dir)
            return ChatFile2(
                path=relative_path,
                size=os.path.getsize(media_path),
                modification_timestamp=os.path.getmtime(media_path),
            )

    return None


def scan_input_directory2(input_dir: str, existing_data: Optional[ChatData2] = None) -> ChatData2:
    """
    Scan input directory using ChatData2 structures.

    Args:
        input_dir: Directory containing WhatsApp chat exports
        existing_data: Optional existing ChatData2 to merge with

    Returns:
        ChatData2 containing all messages and files from input
    """
    chat_data = existing_data or ChatData2()

    # Find all chat files
    chat_files = find_chat_files2(input_dir)

    # Parse each chat file
    for chat_file in chat_files:
        full_path = os.path.join(input_dir, chat_file.path)
        result = parse_chat_file(full_path, chat_file)

        if not result:
            continue

        chat, input_files = result

        # Add input files to global repository
        chat_data.input_files.update(input_files)

        # Merge into existing chat or create new one
        if chat.chat_name in chat_data.chats:
            existing_chat = chat_data.chats[chat.chat_name]
            existing_chat.messages.extend(chat.messages)
        else:
            chat_data.chats[chat.chat_name] = chat

    # Look for media files
    for chat in chat_data.chats.values():
        for msg in chat.messages:
            if msg.media_file_id is not None and msg.input_file_id is not None:
                # Try to locate the media file
                if media_file := find_media_files2(input_dir, chat_data.input_files[msg.input_file_id], msg.content):
                    chat_data.input_files[media_file.id] = media_file
                    msg.media_file_id = media_file.id

    return chat_data
