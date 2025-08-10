"""
Helper module to merge existing ChatData with VFS.
"""

from src.chat_data import ChatData, ChatFile
from src.vfs import VFS


def merge_chat_files_into_vfs(chat_data: ChatData, vfs: VFS) -> None:
    """
    Patch ChatFiles from ChatData into VFS, marking them as non-existing if they don't exist in VFS.

    Args:
        chat_data: Existing ChatData containing file history
        vfs: Current VFS to update with historical files
    """
    for file_id, chat_file in chat_data.input_files.items():
        # Only process if not already in VFS
        if vfs.get_by_id(file_id) is None:
            # Create new instance with exists=False since not found in current VFS
            vfs.add_file(
                ChatFile(
                    path=chat_file.path,
                    size=chat_file.size,
                    modification_timestamp=chat_file.modification_timestamp,
                    parent_zip=chat_file.parent_zip,
                    exists=False,
                )
            )
