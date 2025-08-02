# Implementation Plan for Whatsapp Archive Browseability Generator

## 1. Command Line Interface (CLI)
1.1. Design a CLI using Python's `argparse` module.
1.2. Add parameters for:
  - Input folder containing WhatsApp archives.
  - Time locale specification.
  - Output directory for generated HTML.
1.3. Implement help and usage instructions.

## 2. Input Directory Scanning
2.1. Implement a function to scan the input directory for:
  - WhatsApp chat files (`_chat.txt`).
  - Media files.
  - Zipped WhatsApp export files.
2.2. Extract zipped files to a temporary folder for processing.
2.3. Parse `_chat.txt` files to identify:
  - Different chats.
  - Time ranges for chat data.
  - Media file references.
2.4. Construct a `ChatData` data structure to store parsed information.

## 3. Output Directory Status Check
3.1. Check if `browseability-generator-chat-data.json` exists in the output directory.
3.2. If it exists, load and parse it into a `ChatData` data structure.

## 4. Data Comparison and Merging
4.1. Compare the `ChatData` structures from the input and output directories.
4.2. Identify missing or changed chat data that needs to be regenerated.
4.3. Merge the input and output `ChatData` structures into a new `ChatData` structure.

## 5. HTML Generation
5.1. Generate or regenerate missing HTML files based on the merged `ChatData` structure.
5.2. Ensure the following structure:
  - A top-level `index.html` file listing all chats alphabetically.
  - Subfolders for each chat containing:
    - `YYYY.html` files for yearly chat data.
    - A `media` subfolder for media files.
5.3. Deploy a single static `.css` file to the output directory and reference it in the HTML files.

## 6. Metadata Update
6.1. Write the merged `ChatData` structure to `browseability-generator-chat-data-NEW.json`.
6.2. Rename the existing `browseability-generator-chat-data.json` to `browseability-generator-chat-data-BACKUP.json` (delete old backup if it exists).
6.3. Rename `browseability-generator-chat-data-NEW.json` to `browseability-generator-chat-data.json`.

## 7. Utilities and Helper Functions
7.1. Create utility functions for:
  - Parsing `_chat.txt` files.
  - Extracting zipped files.
  - Linking media files to chat messages.
  - Generating clean and simple HTML.
7.2. Organize utilities into separate `.py` files in a subfolder.

## 8. Testing and Validation
8.1. Test the program with various input scenarios:
  - Multiple backups of the same chat.
  - Missing media files.
  - Different time locales.
8.2. Validate the generated HTML structure and metadata.

## 9. Documentation
9.1. Update the README.md with:
  - Detailed usage instructions.
  - Examples of input and output.
9.2. Add comments and docstrings to the code for maintainability.
