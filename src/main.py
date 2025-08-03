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

    # Step 1: Scan input directory
    input_data = scan_input_directory(args.input_folder)

    # Step 2: Check output directory
    output_data = check_output_directory(args.output_folder)

    # Step 3: Compare and merge data
    merged_data = compare_and_merge_data(input_data, output_data)

    # Step 4: Generate HTML
    generate_html(merged_data, args.output_folder)

    # Step 5: Update metadata
    update_metadata(merged_data, args.output_folder)

if __name__ == "__main__":
    main()
