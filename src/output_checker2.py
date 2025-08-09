"""
This module handles checking and converting output JSON files for ChatData2.
"""

import json
import os
from typing import Optional

from src.chat_data import ChatData
from src.chat_data2 import (
    Chat2,
    ChatData2,
    ChatFile2,
    ChatName2,
    Message2,
    OutputFile2,
)


def convert_to_chat_data2(old_data: ChatData) -> ChatData2:
    """Convert ChatData to ChatData2 format."""
    new_data = ChatData2()
    new_data.timestamp = old_data.timestamp

    # First pass: create ChatFile2 objects for all files
    for chat in old_data.chats.values():
        for msg in chat.messages:
            # Convert input file
            if msg.input_file:
                chat_file = ChatFile2(
                    path=msg.input_file.path,
                    size=msg.input_file.size or 0,
                    modification_timestamp=msg.input_file.modification_timestamp or 0.0,
                    parent_zip=msg.input_file.parent_zip,
                )
                new_data.input_files[chat_file.id] = chat_file

            # Convert media file
            if msg.media and msg.media.input_path:
                media_file = ChatFile2(
                    path=msg.media.input_path.path,
                    size=msg.media.input_path.size or 0,
                    modification_timestamp=msg.media.input_path.modification_timestamp or 0.0,
                    parent_zip=msg.media.input_path.parent_zip,
                )
                new_data.input_files[media_file.id] = media_file

    # Second pass: create messages referencing files
    for chat_name, chat in old_data.chats.items():
        messages: list[Message2] = []

        for msg in chat.messages:
            # Find file IDs
            input_file_id = None
            if msg.input_file:
                temp_file = ChatFile2(
                    path=msg.input_file.path,
                    size=msg.input_file.size or 0,
                    modification_timestamp=msg.input_file.modification_timestamp or 0.0,
                )
                input_file_id = temp_file.id

            media_file_id = None
            if msg.media and msg.media.input_path:
                temp_file = ChatFile2(
                    path=msg.media.input_path.path,
                    size=msg.media.input_path.size or 0,
                    modification_timestamp=msg.media.input_path.modification_timestamp or 0.0,
                )
                media_file_id = temp_file.id

            # Create new message
            new_msg = Message2(
                timestamp=msg.timestamp,
                sender=msg.sender,
                content=msg.content,
                year=msg.year,
                input_file_id=input_file_id,
                media_file_id=media_file_id,
            )
            messages.append(new_msg)

        # Create new chat
        new_chat = Chat2(chat_name=ChatName2(name=chat_name.name), messages=messages)
        new_data.chats[ChatName2(name=chat_name.name)] = new_chat

        # Convert output files
        for year, out_file in chat.output_files.items():
            new_data.chats[ChatName2(name=chat_name.name)].output_files[year] = OutputFile2(
                year=year,
                generate=out_file.generate,
            )

    return new_data


def check_output_directory2(output_dir: str) -> Optional[ChatData2]:
    """
    Check for existing chat data JSON and convert if needed.
    """
    json_path = os.path.join(output_dir, "browseability-generator-chat-data.json")

    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Try loading as ChatData2 first
        try:
            return ChatData2.from_json(json.dumps(data))
        except Exception:
            # If that fails, try converting from old format
            old_data = ChatData.from_json(json.dumps(data))
            return convert_to_chat_data2(old_data)

    except Exception as e:
        print(
            f"Error reading {json_path}: {e}, will regenerate from input.\n"
            "  NOTE: IF INPUT FILES ARE MISSING SOME MESSAGES MAY BE LOST!\n"
            "  Check the output backup JSON: browseability-generator-chat-data-BACKUP.json"
        )
        return None
