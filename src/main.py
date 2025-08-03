import argparse
import os
from parser import parse_chat_files
from chat_data import ChatData
from input_scanner import scan_input_directory
from output_checker import check_output_directory
from data_comparator import compare_and_merge_data
from html_generator import generate_html
from metadata_updater import update_metadata

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Whatsapp Archive Browseability Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate HTML from a WhatsApp export folder
    %(prog)s --input path/to/whatsapp/export --output path/to/html/output

    # Use a specific locale (default: FI)
    %(prog)s --input path/to/whatsapp/export --output path/to/html/output --locale FI

Notes:
    - Input folder should contain WhatsApp chat exports (_chat.txt files)
    - Can handle both expanded and .zip WhatsApp exports
    - Output directory will be created if it doesn't exist
    - Generates clean, static HTML with year-based organization
    - Detects and handles duplicate messages from multiple backups
    - Preserves and links media files referenced in chats
    """
    )
    parser.add_argument("--input", dest="input_folder", required=True, metavar="DIR",
                       help="Input folder containing WhatsApp archives (either expanded or .zip)")
    parser.add_argument("--output", dest="output_folder", required=True, metavar="DIR",
                       help="Output folder for generated browseable HTML files")
    parser.add_argument("--locale", default="FI", metavar="LOCALE",
                       help="Locale for parsing timestamps (currently only FI supported)")

    args = parser.parse_args(argv)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Step 1: Check output directory
    # This step loads existing metadata from the output directory.
    # In the future, this data will be passed to the input scanner to enable incremental parsing.
    output_data = check_output_directory(args.output_folder)

    # Step 2: Scan input directory
    # The input scanner will eventually use the output_data to detect unchanged input files
    # and reuse data from the output directory instead of re-parsing or unzipping files.
    input_data = scan_input_directory(args.input_folder, output_data=output_data)

    # Step 3: Compare and merge data: Detects which YYYY.html files need to be (re)generated, this information is embeded in ChatData for simplicity.
    merged_data = compare_and_merge_data(input_data, output_data)

    # Step 4: Generate HTML: Generate per chat folders, copy media files, and create per chat and top level index.htmls.
    generate_html(merged_data, args.output_folder)

    # Step 5: Update metadata: safely rewrites browseability-generator-chat-data.json, old JSON becomes backup.
    update_metadata(merged_data, args.output_folder)

if __name__ == "__main__":
    main()
