"""
Entry point for the whatsapp-archive-browse tool using ChatData.
"""

import argparse
import os
from pathlib import Path
from typing import Sequence

from src.chat_data import ChatData
from src.chat_vfs_merge import merge_chat_files_into_vfs
from src.html_generator import generate_html
from src.media_locator import process_media_dependencies
from src.message_processor import process_messages
from src.metadata_updater import update_metadata
from src.output_checker import check_output_directory
from src.output_dependency_checker import check_output_dependencies
from src.vfs_scanner import scan_directory_to_vfs


def get_current_time() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main(argv: Sequence[str] | None = None, *, timestamp: str | None = None) -> None:
    if timestamp is None:
        timestamp = get_current_time()

    parser = argparse.ArgumentParser(
        description="Whatsapp Archive Browseability Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate HTML from a WhatsApp export folder
    %(prog)s --input path/to/whatsapp/export --output path/to/html/output

Notes:
    - Input folder should contain WhatsApp chat exports (_chat.txt files)
    - Can handle both expanded and .zip WhatsApp exports
    - Output directory will be created if it doesn't exist
    - Generates clean, static HTML with year-based organization
    - Detects and handles duplicate messages from multiple backups
    - Preserves and links media files referenced in chats
    """,
    )
    parser.add_argument(
        "--input",
        dest="input_folder",
        required=True,
        metavar="DIR",
        help="Input folder containing WhatsApp archives (either expanded or .zip)",
    )
    parser.add_argument(
        "--output",
        dest="output_folder",
        required=True,
        metavar="DIR",
        help="Output folder for generated browseable HTML files",
    )

    args = parser.parse_args(argv)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Step 1: Check output directory for existing data
    output_data = check_output_directory(args.output_folder) or ChatData()

    # Step 2: Build VFS from input directory
    vfs = scan_directory_to_vfs(Path(args.input_folder))

    # Step 3: Merge in historical files from output data
    merge_chat_files_into_vfs(output_data, vfs)

    # Step 4: Process messages and media
    chat_data = process_messages(vfs, output_data)
    process_media_dependencies(chat_data, vfs)

    # Set timestamp
    chat_data.timestamp = timestamp

    # Step 5: Check which files need regeneration
    check_output_dependencies(chat_data, output_data)

    # Step 6: Generate HTML
    generate_html(chat_data, args.input_folder, args.output_folder)

    # Step 7: Update metadata
    update_metadata(chat_data, args.output_folder)


if __name__ == "__main__":
    main()
