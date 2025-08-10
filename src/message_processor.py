"""
Process WhatsApp chat files from VFS into ChatData.
"""

import os
from typing import Dict, List, Set, Tuple
from venv import logger

from src.chat_data import Chat, ChatData, ChatFile, ChatName
from src.logging_util import TRACE_LEVEL
from src.parser import parse_chat_file
from src.vfs import VFS


def process_messages(vfs: VFS, old_chat_data: ChatData) -> ChatData:
    """
    Process chat files from VFS into ChatData, merging with old data and
    ordering by file modification time. Files for the same chat are processed
    sequentially to maintain message order.

    Old chat data is merged and deduped in this same step.
    """
    chat_data = ChatData()

    # Group chat files by chat name
    chat_files_by_name: Dict[ChatName, List[Tuple[float, ChatFile, Chat]]] = {}
    seen_message_hashes: Dict[ChatName, Set[str]] = {}

    total_chat_file_count: int = 0
    parsed_file_count: int = 0
    message_count: int = 0
    duplicate_message_count: int = 0
    old_parsed_count: int = 0
    parse_failure_count: int = 0
    old_chat_count: int = 0

    # Process old chat data first
    for chat_name, old_chat in old_chat_data.chats.items():
        for msg in old_chat.messages:
            file_id = msg.input_file_id
            if file_id.value and (vfs.exists(file_id) or not vfs.get_by_id(file_id)):
                if chat_name not in chat_files_by_name:
                    chat_files_by_name[chat_name] = []
                # Use file from VFS if exists, otherwise create dummy for ordering
                file = vfs.get_by_id(file_id) or ChatFile(path="", size=0, modification_timestamp=0, exists=False)
                existing_chats = [c for _, _, c in chat_files_by_name[chat_name] if c.chat_name == chat_name]
                if not existing_chats:
                    chat_files_by_name[chat_name].append((file.modification_timestamp, file, old_chat))
                    old_chat_count += 1

    # Process new chat files that weren't in old data
    for file in vfs.files_by_path.values():
        if os.path.basename(file.path) == "_chat.txt" and file.exists:
            # Skip if we already have a file with this exact ID from old data
            file_id = file.id
            if any(old_file.id == file_id for chats in chat_files_by_name.values() for _, old_file, _ in chats):
                old_parsed_count += 1
                continue

            logger.log(TRACE_LEVEL, f"Parsing chat file: {file.path}")
            chat: Chat | None = parse_chat_file(vfs, file)
            parsed_file_count += 1
            if chat:
                if chat.chat_name not in chat_files_by_name:
                    chat_files_by_name[chat.chat_name] = []
                chat_files_by_name[chat.chat_name].append((file.modification_timestamp, file, chat))
            else:
                parse_failure_count += 1

    # Process each chat's files in order of modification time
    for chat_name, tuples in chat_files_by_name.items():
        # sort tuples by modification timestamp oldest first
        tuples.sort(key=lambda x: x[0])

        seen_message_hashes[chat_name] = set()
        combined_chat = Chat(chat_name=chat_name)
        chat_data.chats[chat_name] = combined_chat

        # Sort files by modification time (oldest first)
        for _, file, chat in tuples:
            total_chat_file_count += 1

            # Ensure chat files appear in input_files.
            chat_data.input_files[file.id] = file

            # Add only non-duplicate messages. As we go through export files
            # oldest first, we should get correct time order for messages
            # without having to parse the localized timestamps.
            for msg in chat.messages:
                msg_hash = f"{msg.timestamp}|{msg.sender}|{msg.content}"
                if msg_hash in seen_message_hashes[chat_name]:
                    duplicate_message_count += 1
                else:
                    message_count += 1
                    seen_message_hashes[chat_name].add(msg_hash)
                    combined_chat.messages.append(msg)

    logger.info(f"Total chat files processed: {total_chat_file_count}")
    logger.info(f"Parsed chat files: {parsed_file_count}")
    logger.info(f"Messages found: {message_count}")
    logger.info(f"Duplicate messages found: {duplicate_message_count}")
    logger.info(f"Old chat files processed: {old_chat_count}")
    logger.info(f"Old parsed chat files: {old_parsed_count}")
    logger.info(f"Parse failures: {parse_failure_count}")

    return chat_data
