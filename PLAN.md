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
4.3. Implement a basic integration test fixture helper functions that make it trivial to construct tests using the following:
  - Sets up temp input folder (Deep copy of `demo-chat`)
  - Sets up temp output folder
  - Run CLI 
  - Modify input folder
  - Check output folder
  - Clean up temp folders
4.4.
  - Implement a simple test matching current implementation (no HTML generated as steps 5-9 are not completed)
4.5. Implement help and usage instructions.

## 5. Basic input Directory Scanning
5.1. Implement a function to scan the input directory for:
  - WhatsApp chat files (`_chat.txt`).
  - Media files.
5.2. Parse `_chat.txt` files to identify:
  - Different chats.
  - Year numbers to place messages in correct output HTML files.
  - Time order for chat messages:
    - Since parsing timestamps is too hard due to wild localization:
      - We'll resort to parsing _chat.txt files in the file modification order
      - We append parsed messages to the array
      - Eliminate chat messages that are duplicates across the array using a dictionary
      - If timestamps on the export files are correct, the chat messages should be in correct order.
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

## 10. Testing and Validation, advanced features
10.1. Add more integration tests for each of the advanced features:
  - In the following assert output files against reference test resources stored in the project
  - Each test offers a feature for easy update of output reference test resource for when code is changed
10.1.1. Basic test for simple scenario with output folder compared against stored reference resources
10.1.2. 2 backups of the same chat in different directories
10.1.3. 2 backups of the same chat in different directories with partially overlapping history
10.1.4. Unknown _chat.txt syntax, log warnings and continue
10.1.5. Missing media files, log warnings and add note to output HTML and continue
10.1.6. Missing input files on 2nd run, Use output directory `browseability-generator-chat-data.json` and media files to keep output chat HTML intact
10.1.7. Incremental runs using input file timestamp + size checks, only modified input files are processed again and only necessary output HTML regenerated
10.1.8. Repeated runs on same input, no work done
10.1.9. Handling of Zipped WhatsApp export files

## 11. Documentation
11.1. Update the README.md with:
  - Detailed usage instructions.
  - Examples of input and output.
11.2. Add comments and docstrings to the code for maintainability.

# PLAN FOR THE NEXT STEPS
NOTE: Most of the above plan is completed now, but the program does not meet
expectations.


## 1: Update documentation
We should turn the plan above into a document about the function, design and
structure of the program at this stage.

Lets create a separate technical-documentation.md where we combine and update
the General Plan section from README.md and create an up to date documentation
combining with the information in the plan above.

This document will provide context for the final steps in this project towards 1.0.

After the last steps described below, the document will be updated and we will
have up to date documetation for this project

## 2: Implement the final refactoring, VFS, incrementality

Then we should focus on the chat_model.md upgrade, VFS and other changes flowing
from those, then adding the incrementality and finalizing and testing the zip
file handling support should be straightforward.

Then remains testing with large cache of "production data" and possibly changes
and fixes flowing from that.

## Remainig non completed steps from the original plan above

These steps, mostly very minor, were not completed so far. We can mostly
ignore them now and maybe
add them as final checks in the end of the new plan.

10.1.5. Missing media files, log warnings and add note to output HTML and continue
10.1.6. Missing input files on 2nd run, Use output directory `browseability-generator-chat-data.json` and media files to keep output chat HTML intact

## Major steps remaining:

These steps actually contain quite a bit of complexity, though they were minor verification steps
in the original plan. This was partly intentional as now we have been able to think about
these and have a more coherent detailed plan (VFS + ChatData2 refactoring)

10.1.7. Incremental runs using input file timestamp + size checks, only modified input files are processed again and only necessary output HTML regenerated
10.1.8. Repeated runs on same input, no work done
10.1.9. Handling of Zipped WhatsApp export files

We'll leave again adding the more complex tests for these to the
test_integration.py for later for a kind of verification pass in the end.

We are also taking into account the
[testing-approach.md](./testing-approach.md).

## chat_data.py model refactoring aka chat data 2

Lets create chat_data2.py ChatData2 with number 2 appended as suffix to all
types ChatData2, ChatFile2 etc.

Then we can incrementally modify code and identify which parts have been
modified. Note the text below does not contain these "2" suffixes, but they
should be there.

Then a bit later we can remove the original chat_data.py and do a few IDE rename
operations to remove the number "2" suffixes for code readablity.

### ChatFile changes
- Add ChatFileID data type
- ChatFile has id property
- ChatFile has "exists" property that is updated in input folder scanning
- ChatFile modification_timestamp and size should not need to be optional
- ChatFile should have 2 separate properties: relative path, file name
- ChatFile parent_zip should be a ChatFile ID reference

### use ChatFile IDs
- Don't repeat the full ChatFile struct in each chat message
  - Still useful to have a reference from where a chat message came from
  - See ChatFile id in next section
  - files stored in a separate by ID dict input_files
    - input_files no longer in input merged from old JSON and kept around

### MediaReference

This type should be replaced with the ChatFile. The location in the structure
identifies that it is a media file. This makes sense because Whatsapp media
file can be any type, though almost always some image.

### Message

The message shall no longer embed any file data, mostly they are replaced by ChatFileIDs.

The core fields timestamp, sender, content and year remain.

media gets type Optional[ChatFileID]

input_file gets type ChatFileID

html_file is removed. It's role will be replaced by the new OutputFile data type
and the more complex output_files property in Chat.

### OutputFile data type
The OutputFile is together with ChatFile forms the core of the incremental system.


- to be stored in the chat output_files structure
  - Contains a dictionary media_dependencies from media file base names to dependency ChatFileIDs / None if the file wasn't able to be located on previous run
  - Similarly contains a list chat_dependencies for _chat.txt dependencies
  - Similarly contains a field css_dependency for the ChatFileID for the resource .CSS file
  - OutputFile needs to be updated if the dicts of either dependencies ChatFileIDs differs
  - If media_dependencies differs between old JSON and model generated this run -> HTML is regenerated (media links)
    - Only the media base names that have different or ChatFileID or it was previously None are copied
  - If other_dependencies differs between old JSON and model generated this run -> HTML is regenerated
  - Important that dependencies are handled in a way that reduces churn, even if input folders change
  - The new model generated this run contains what was merged from old JSON

## Separate VFS (Virtual File System) scanning pass

- First read the old output.JSON and don't open / rescan .zips that have same ChatFileID
- ChatFiles have ID derived from file path, separator, size, separator, modification timestamp (sha1 + base64)
- Merge the output.JSON ChatFile's into the same VFS to have it serve as a single index
- Scan the input folder and produce a structure of ChatFile's for all files present
- Scan the .zip files in the input folder and add their contents as well to the VFS
  - Only if the .zip file contains _chat.txt at top level
- Used to find media files faster
- Multiple inidices for ChatFile entities / dicts in the VFS struct:
  - By relative input subfolder / zip file path (for quick lookup of media files in same location as _chat.txt) (1 to many)
  - by ChatFile ID (1 to 1)
  - by file base name (for quick lookup of media files)
- Generate all ChatFiles in one place in the first pass, refer to them later

## Handling of Zipped WhatsApp export files

- Use the VFS in other stages to abstract away that some files are inside zip files

## Incremental updates

- If _chat.txt is present in the output and CSS resource has not changed.

## Smaller Features / TODOs / Ideas

- Remove the locale parameter (the parsing ended up agnostic using "heuristics")
- Identifying 2 party chats and rendering the speakers differently
  - IDEA: Command line option to give the name of "our user"
- pattern to turn link looking things into a href links in HTML output

