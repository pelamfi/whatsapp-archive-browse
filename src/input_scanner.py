"""
This module handles scanning WhatsApp chat export directories for _chat.txt files and their
associated media files. The scanning process is designed to be robust and handle real-world
complexities of WhatsApp chat backups:

1. Multiple backup copies: Users often have multiple backups of the same chat across
   different times, which may have overlapping content.

2. File modification timestamps: Since parsing exact timestamps from _chat.txt is complex
   due to localization, we use file modification timestamps to determine message order
   when merging multiple backups. While not perfect, this works reasonably well since
   WhatsApp creates new export files with current timestamps.

3. Incremental scanning: For efficiency in step 11, we'll add support for only rescanning
   files that have changed based on size and timestamps. For now, we scan everything.

4. Zip files: Handling of zipped exports is left for step 11 to keep the implementation
   focused first.
"""

import logging
import os
from typing import Dict, List, Optional, Set, Tuple

from src.chat_data import Chat, ChatData, ChatFile, Message

type MessageTuple = Tuple[str, str, str, int, Optional[str]]


def find_chat_files(input_dir: str) -> List[Tuple[str, float]]:
    """
    Find all _chat.txt files in the input directory and return them sorted by
    modification time. This ordering is used as a proxy for message chronology
    since exact timestamp parsing is complicated by localization.

    Args:
        input_dir: Root directory to search for _chat.txt files

    Returns:
        List of (file_path, mtime) tuples sorted by mtime
    """
    chat_files: list[tuple[str, float]] = []

    for root, _, _ in os.walk(input_dir):
        path = os.path.join(root, "_chat.txt")
        if os.path.isfile(path):
            mtime = os.path.getmtime(path)
            chat_files.append((path, mtime))

    # Sort by modification time to establish message chronology
    return sorted(chat_files, key=lambda x: x[1])


def remove_duplicate_messages(chat: Chat) -> None:
    """
    Remove duplicate messages from a chat by comparing message attributes.
    We call this after adding each new _chat.txt file to keep memory usage
    reasonable when processing many backup copies of the same chat.

    This is separated into its own function since duplicate elimination logic
    may need to evolve based on real-world usage patterns.

    Args:
        chat: Chat object to deduplicate messages in
    """
    # For now we use a simple exact match on all fields
    # Later we may need more sophisticated matching if we find
    # that timestamps or other fields vary between copies

    seen: Set[MessageTuple] = set()
    unique_messages: List[Message] = []

    for msg in chat.messages:
        msg_tuple: MessageTuple = (
            msg.timestamp,
            msg.sender,
            msg.content,
            msg.year,
            (media := msg.media) and media.raw_file_name,
        )

        if msg_tuple not in seen:
            seen.add(msg_tuple)
            unique_messages.append(msg)

    chat.messages = unique_messages


def scan_input_directory(input_dir: str, existing_data: Optional[ChatData] = None) -> ChatData:
    """
    Scan input directory for WhatsApp chat exports, merging with existing data if provided.

    The scanning process:
    1. Find all _chat.txt files sorted by modification time
    2. For each file:
       - Parse it using the parser module
       - Merge messages into the appropriate chat
       - Remove duplicates to keep memory usage reasonable
    3. Return updated ChatData

    Args:
        input_dir: Directory containing WhatsApp chat exports
        existing_data: Optional existing ChatData to merge with

    Returns:
        ChatData containing all messages from the input directory
    """
    chat_data = existing_data or ChatData()

    # Find and sort chat files by modification time
    chat_files = find_chat_files(input_dir)

    for file_path, mtime in chat_files:
        # Create ChatFile for tracking origin
        chat_file = ChatFile(
            path=os.path.relpath(file_path, input_dir),
            modification_timestamp=mtime,
            size=os.path.getsize(file_path),
        )

        # Parse file and merge messages - using parser module which we assume exists
        # Details of parsing and merging are handled by the parser module
        from .parser import parse_chat_file  # Import here to avoid circular imports

        new_messages = parse_chat_file(file_path, chat_file)

        for chat_name, messages in new_messages.items():
            # Get or create chat
            if chat_name not in chat_data.chats:
                chat_data.chats[chat_name] = Chat(chat_name=chat_name)

            # Add new messages
            chat = chat_data.chats[chat_name]
            chat.messages.extend(messages)

            # Remove duplicates after each file to keep memory usage reasonable
            remove_duplicate_messages(chat)

    # Try to locate any missing media files
    for chat in chat_data.chats.values():
        find_media_simple(chat, input_dir)
    find_missing_media(chat_data, input_dir)

    return chat_data


def find_media_simple(chat: Chat, input_dir: str) -> None:
    """
    Locate missing media files in the same directory as the _chat.txt file that referenced them.

    Args:
        chat: Chat object to process
        input_dir: Root input directory
    """
    for msg in chat.messages:
        if not msg.media or msg.media.input_path:
            continue

        # Get the directory of the _chat.txt file that referenced this media
        if not msg.input_file:
            continue

        chat_dir = os.path.dirname(os.path.join(input_dir, msg.input_file.path))
        media_path = os.path.join(chat_dir, msg.media.raw_file_name)

        if os.path.exists(media_path):
            msg.media.input_path = ChatFile(
                path=os.path.relpath(media_path, input_dir),
                modification_timestamp=os.path.getmtime(media_path),
                size=os.path.getsize(media_path),
            )


def find_missing_media(chat_data: ChatData, input_dir: str) -> None:
    """
    Scan chat data for missing media files and attempt to locate them.
    First tries same directory as _chat.txt, then searches entire input directory.
    Logs warning messages about missing media files.

    Args:
        chat_data: ChatData to process
        input_dir: Root input directory
    """
    # First pass: try to find media files in same directory as _chat.txt
    for chat in chat_data.chats.values():
        find_media_simple(chat, input_dir)

    # Second pass: collect messages with missing media
    missing_media_messages: List[Message] = []
    for chat in chat_data.chats.values():
        for msg in chat.messages:
            if msg.media and not msg.media.input_path:
                missing_media_messages.append(msg)

    if not missing_media_messages:
        return

    # Log the initial count of missing media files
    logging.warning(f"Found {len(missing_media_messages)} messages with missing media files")

    # Build a dictionary of all media files in input directory
    media_files: Dict[str, str] = {}
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file not in media_files:  # Only keep first occurrence if duplicate names exist
                media_files[file] = os.path.join(root, file)

    # Try to match missing media files
    still_missing: List[Tuple[str, str]] = []  # List of (filename, chat_txt_path) pairs
    for msg in missing_media_messages:
        if media := msg.media:
            filename = media.raw_file_name
            if filename in media_files:
                media_path = media_files[filename]
                msg.media.input_path = ChatFile(
                    path=os.path.relpath(media_path, input_dir),
                    modification_timestamp=os.path.getmtime(media_path),
                    size=os.path.getsize(media_path),
                )
            else:
                still_missing.append((filename, msg.input_file.path if msg.input_file else "unknown _chat.txt"))

    # Log details about still-missing files
    if still_missing:
        logging.warning("The following media files are still missing:")
        for filename, chat_txt in still_missing:
            logging.warning(f"  {filename} (referenced in {chat_txt})")
