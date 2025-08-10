"""
Entry point for the whatsapp-archive-browse tool using ChatData.

This module provides the main entry point for the WhatsApp archive browser tool.
It supports various verbosity levels for logging:

- Level 0 (--quiet): Only errors
- Level 1 (-v): Info - Major steps and results (default)
- Level 2 (-vv): Debug - Detailed progress info
- Level 3 (-vvv): Trace - Very detailed debugging info
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Sequence

from src.chat_data import ChatData
from src.chat_vfs_merge import merge_chat_files_into_vfs
from src.html_generator import generate_html
from src.logging_util import setup_logging
from src.media_locator import process_media_dependencies
from src.message_processor import process_messages
from src.metadata_updater import update_metadata
from src.output_checker import check_output_directory
from src.output_dependency_checker import check_output_dependencies
from src.output_file_generator import generate_output_files
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
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity level (0-3). -v for INFO, -vv for DEBUG, -vvv for TRACE. Default: 1 (INFO)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode, no output except errors (sets verbosity to 0)",
    )

    args = parser.parse_args(argv)

    verbose = args.verbose
    if args.quiet:
        verbose = 0

    setup_logging(verbose)

    logger = logging.getLogger(__name__)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Step 1: Check output directory for existing data
    logger.info("Checking output directory for existing data...")
    output_data = check_output_directory(args.output_folder) or ChatData()

    # Step 2: Build VFS from input directory
    logger.info("Building VFS from input directory...")
    vfs = scan_directory_to_vfs(Path(args.input_folder))

    # Step 3: Merge in historical files from output data
    logger.info("Merging historical files...")
    merge_chat_files_into_vfs(output_data, vfs)

    # Step 4: Process messages and media and merge old message data
    logger.info("Processing messages and merging with old data...")
    chat_data = process_messages(vfs, output_data)

    # Set timestamp
    chat_data.timestamp = timestamp

    # Step 5: Generate output file records
    logger.info("Generating output file records...")
    generate_output_files(chat_data)

    # Step 6: Locate media and update output_files with media_dependencies
    logger.info("Processing media dependencies...")
    process_media_dependencies(chat_data, vfs)

    # Step 7: Check which files need regeneration
    logger.info("Checking which files need regeneration...")
    check_output_dependencies(chat_data, output_data)

    # Step 8: Generate HTML
    logger.info("Generating HTML files...")
    generate_html(chat_data, vfs, args.output_folder)

    # Step 9: Update metadata
    logger.info("Updating metadata...")
    update_metadata(chat_data, args.output_folder)

    logger.info("Done!")


if __name__ == "__main__":
    main()
