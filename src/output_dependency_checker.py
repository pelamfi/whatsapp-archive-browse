"""
Check output file dependencies to determine if HTML regeneration is needed.
"""

import logging

from src.chat_data import ChatData
from src.logging_util import TRACE_LEVEL

logger = logging.getLogger(__name__)


def check_output_dependencies(new_data: ChatData, old_data: ChatData) -> None:
    """
    Compare output files between old and new data and set generate flag if dependencies changed.

    Args:
        new_data: New ChatData with output files to check
        old_data: Previous ChatData containing old dependency information
    """
    generate_count: int = 0
    total_count: int = 0
    # For each chat in new data
    for chat_name, new_chat in new_data.chats.items():
        old_chat = old_data.chats.get(chat_name)

        # For each year's output file
        for year, new_file in new_chat.output_files.items():
            old_file = old_chat.output_files.get(year) if old_chat else None

            total_count += 1

            # Always generate if no old data exists
            if not old_file:
                new_file.generate = True
                continue

            # Check if any dependencies changed
            if (
                new_file.css_dependency != old_file.css_dependency
                or new_file.media_dependencies != old_file.media_dependencies
                or new_file.chat_dependencies != old_file.chat_dependencies
            ):
                generate_count += 1
                new_file.generate = True
            else:
                logger.log(TRACE_LEVEL, f"Output file {chat_name.name} / {new_file.year} is up to date")

    logger.info(f"Output file generation summary: {generate_count}/{total_count} files marked for regeneration")
