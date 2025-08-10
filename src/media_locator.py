"""
Media file discovery and matching for WhatsApp chat archives.
"""

from pathlib import Path
from typing import Dict, Optional

from src.chat_data import ChatData, ChatFile, ChatFileID
from src.vfs import VFS


def find_media_file(vfs: VFS, media_name: str, chat_file_path: str) -> Optional[ChatFile]:
    """
    Find a media file by name using chat message's source file location as context.
    First tries to find the file in the same directory as the chat file.
    If not found, falls back to searching any file with the same name.

    Args:
        vfs: Virtual file system instance
        media_name: Name of the media file to find
        chat_file_path: Path of the chat file containing the media reference
    """
    chat_file = vfs.get_by_path(chat_file_path)
    if not chat_file:
        # If we can't find the chat file, just try finding the media by name
        if found_files := vfs.find_by_name(media_name):
            return next(iter(found_files))
        return None

    # Try to find in the same directory as the chat file
    chat_dir = str(Path(chat_file.path).parent)
    media_path = str(Path(chat_dir) / media_name)
    if media_file := vfs.get_by_path(media_path):
        return media_file

    # Fall back to any file with the same name
    if found_files := vfs.find_by_name(media_name):
        return next(iter(found_files))  # Return first found file

    return None


def process_media_dependencies(chat_data: ChatData, vfs: VFS) -> None:
    """
    Process media dependencies for all chats.
    Updates output file dependencies to track media file locations.
    """
    for chat in chat_data.chats.values():
        # Build a map of media references for each year
        media_by_year: Dict[int, Dict[str, Optional[ChatFileID]]] = {}

        # Process each message's media references
        for msg in chat.messages:
            if msg.media_name:
                year = msg.year
                if year not in media_by_year:
                    media_by_year[year] = {}

                # Only process each unique media file once per year
                if msg.media_name not in media_by_year[year]:
                    chat_file = vfs.get_by_id(msg.input_file_id)
                    if chat_file:
                        media_file = find_media_file(vfs, msg.media_name, chat_file.path)
                        media_by_year[year][msg.media_name] = media_file.id if media_file else None

                        # add found media file to chat_data.input_files
                        if media_file:
                            chat_data.input_files[media_file.id] = media_file

        # Update output file dependencies
        for year, media_deps in media_by_year.items():
            if output_file := chat.output_files.get(year):
                output_file.media_dependencies.update(media_deps)
