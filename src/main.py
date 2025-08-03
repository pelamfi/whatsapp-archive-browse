import argparse
from parser import parse_chat_files
from chat_data import ChatData
from input_scanner import scan_input_directory
from output_checker import check_output_directory
from data_comparator import compare_and_merge_data
from html_generator import generate_html
from metadata_updater import update_metadata

def main():
    parser = argparse.ArgumentParser(description="Whatsapp Archive Browseability Generator")
    parser.add_argument("input_folder", help="Input folder containing WhatsApp archives")
    parser.add_argument("output_folder", help="Output folder for generated HTML")
    parser.add_argument("--locale", default="FI", help="Locale specification (default: FI)")

    args = parser.parse_args()

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
