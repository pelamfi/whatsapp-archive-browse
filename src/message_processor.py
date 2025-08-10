"""
Process WhatsApp chat files from VFS into ChatData.
"""

import os
from typing import Dict, List, Set, Tuple

from src.chat_data import Chat, ChatData, ChatFile, ChatName
from src.parser import parse_chat_file
from src.vfs import VFS


def process_messages(vfs: VFS) -> ChatData:
    """
    Process chat files from VFS into ChatData, ordered by file modification time.
    Files for the same chat are processed sequentially to maintain message order.
    """
    chat_data = ChatData()

    # Group chat files by chat name
    chat_files_by_name: Dict[ChatName, List[Tuple[float, ChatFile, Chat]]] = {}
    seen_message_hashes: Dict[ChatName, Set[str]] = {}

    # Parse all chat files into individual data strucures, duplicates are handled later.
    for file in vfs.files_by_path.values():
        if os.path.basename(file.path) == "_chat.txt" and file.exists:
            chat: Chat | None = parse_chat_file(vfs.abs_path(file), file)
            if chat:
                if chat.chat_name not in chat_files_by_name:
                    chat_files_by_name[chat.chat_name] = []
                chat_files_by_name[chat.chat_name].append((file.modification_timestamp, file, chat))

    # TODO: Take old messages from JSON from output folder and collect them into individual chats
    # based on file ID in each message. Then feed into this same mechanism to get deduping.

    # Process each chat's files in order of modification time
    for chat_name, tuples in chat_files_by_name.items():
        # sort tuples by modification timestamp oldest first
        tuples.sort(key=lambda x: x[0])

        seen_message_hashes[chat_name] = set()
        combined_chat = Chat(chat_name=chat_name)
        chat_data.chats[chat_name] = combined_chat

        # Sort files by modification time (oldest first)
        for _, file, chat in tuples:
            chat_data.input_files[file.id] = file

            # Add only non-duplicate messages. As we go through export files
            # oldest first, we should get correct time order for messages
            # without having to parse the localized timestamps.
            for msg in chat.messages:
                msg_hash = f"{msg.timestamp}|{msg.sender}|{msg.content}"
                if msg_hash not in seen_message_hashes[chat_name]:
                    seen_message_hashes[chat_name].add(msg_hash)
                    combined_chat.messages.append(msg)

    return chat_data
