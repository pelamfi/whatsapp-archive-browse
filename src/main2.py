"""
Entry point for the whatsapp-archive-browse tool using ChatData2.
"""

import argparse
import os
from typing import Sequence

from src.data_comparator2 import merge_chat_data2
from src.html_generator2 import generate_html2
from src.input_scanner2 import scan_input_directory2
from src.metadata_updater2 import update_metadata2
from src.output_checker2 import check_output_directory2


def get_current_time() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main2(argv: Sequence[str] | None = None, *, timestamp: str | None = None) -> None:
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
    output_data = check_output_directory2(args.output_folder)

    # Step 2: Scan input directory
    input_data = scan_input_directory2(args.input_folder, output_data)

    # Step 3: Compare and merge data
    merged_data = merge_chat_data2(input_data, output_data)

    # Set timestamp
    merged_data.timestamp = timestamp

    # Step 4: Generate HTML
    generate_html2(merged_data, args.input_folder, args.output_folder)

    # Step 5: Update metadata
    update_metadata2(merged_data, args.output_folder)


if __name__ == "__main__":
    main2()
