# Implementation Plan for Whatsapp Archive Browseability Generator

## 1. Study and Document the _chat.txt Format
1.1. Analyze the provided demo archive files to understand the syntax and quirks of the `demo-chat/_chat.txt` format.
1.2. Document the findings in a `FORMAT.md` file, including:
  - Message structure.
  - Timestamp formats.
  - Media file references.
  - Any peculiarities or edge cases (e.g., character codes).

## 2. Define the Core ChatData Data Structure
2.1. Create the first iteration of the `ChatData` data structure based on:
  - The specification in the README.md.
  - Discoveries made during the `_chat.txt` format analysis.
2.2. Ensure the data structure can handle:
  - Messages with and without media references.
  - Timestamps without timezone information.
  - Metadata for input and output file paths.
  - Define JSON serialization / deserialization for ChatData
  - Create a basic tests for JSON serialization against reference file stored in repo

## 3. Develop the _chat.txt Parser
3.1. Implement a parser that:
  - Accepts a list of paths to `_chat.txt` files and a locale identifier
    - for now we only support "FI", but leave room for adding more
  - Produces a `ChatData` data structure.
  - Handles duplicated messages and media file references.
3.2. Write unit tests to validate the parser:
  - Use the demo archive files as input.
  - Compare the JSON representation of `ChatData` to stored reference files.

## 4. Command Line Interface (CLI) and integration test scaffolding
4.1. Design a CLI using Python's `argparse` module.
4.2. Add parameters for:
  - Input folder containing WhatsApp archives.
  - locale specification. (Only `FI` supported now)
  - Output directory for generated HTML.
4.3. Implement help and usage instructions.
4.4. Implement a basic integration test fixture helper functions that make it trivial to construct tests using the following:
  - Sets up temp input folder (Deep copy of `demo-chat`)
  - Sets up temp output folder
  - Run CLI 
  - Modify input folder
  - Check output folder
  - Clean up temp folders
4.5.
  - Implement a simple test matching current implementation (no HTML generated as steps 5-9 are not completed)

## 5. Basic input Directory Scanning
5.1. Implement a function to scan the input directory for:
  - WhatsApp chat files (`_chat.txt`).
  - Media files.
5.2. Parse `_chat.txt` files to identify:
  - Different chats.
  - Time ranges for chat data.
  - Media file references.
5.3. Construct a `ChatData` data structure to store parsed information.

## 6. Basic output Directory Status Check
6.1. Check if `browseability-generator-chat-data.json` exists in the output directory.
6.2. If it exists, load and parse it into a `ChatData` data structure.

## 7. Basic data Comparison and Merging
7.1. Compare the `ChatData` structures from the input and output directories.
7.2. Identify missing or changed chat data that needs to be regenerated.
7.3. Merge the input and output `ChatData` structures into a new `ChatData` structure.

## 8. Basic HTML Generation
8.1. Generate or regenerate missing HTML files based on the merged `ChatData` structure.
8.2. Ensure the following structure:
  - A top-level `index.html` file listing all chats alphabetically.
  - Subfolders for each chat containing:
    - `YYYY.html` files for yearly chat data.
    - A `media` subfolder for media files.
8.3. Deploy a single static `.css` file to the output directory and reference it in the HTML files.

## 9. Basic Metadata Update
9.1. Write the merged `ChatData` structure to `browseability-generator-chat-data-NEW.json`.
9.2. Rename the existing `browseability-generator-chat-data.json` to `browseability-generator-chat-data-BACKUP.json` (delete old backup if it exists).
9.3. Rename `browseability-generator-chat-data-NEW.json` to `browseability-generator-chat-data.json`.

## 11. Testing and Validation, advanced features
11.1. Add more integration tests for each of the advanced features:
  - In the following assert output files against reference test resources stored in the project
  - Each test offers a feature for easy update of output reference test resource for when code is changed
11.1.2. 2 backups of the same chat in different directories
11.1.3. 2 backups of the same chat in different directories with partially overlapping history
11.1.4. Unknown _chat.txt syntax, log warnings and continue
11.1.5. Missing media files, log warnings and add note to output HTML and continue
11.1.6. Missing input files on 2nd run, Use output directory `browseability-generator-chat-data.json` and media files to keep output chat HTML intact
11.1.7. Incremental runs using input file timestamp + size checks, only modified input files are processed again and only necessary output HTML regenerated
11.1.8. Repeated runs on same input, no work done
11.1.9. Handling of Zipped WhatsApp export files

## 12. Documentation
12.1. Update the README.md with:
  - Detailed usage instructions.
  - Examples of input and output.
12.2. Add comments and docstrings to the code for maintainability.
