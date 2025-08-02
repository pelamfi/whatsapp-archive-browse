## Whatsapp Archive Browseability Generator

This tool scans a directory for whatsapp archives, zipped or otherwise and
generates a clean static HTML folder where backed up whatsapp chats can be
viewed.

Parameters:
  - Input folder containing whatsapp archives either still in .zip files or
    expanded by user

Features:
  - Detects duplicated chats (eg. from multiple backups done on same chat at
    different times)
  - Constructs a clean timeline even with duplicated messages
    - with years worth of chat in each file and a top level index files allowing
      to select a chat and a year
  - Links media files back to the chat
  - Scans for media files in the input directory in case they are not in the
    same location as the `_chat.txt` files
  - Can be run multiple times incrementally
    - The files used to construct each chat HTML are stored as metadata in the
      HTML
    - The metadata stored alongside the generated HTML files in
      browseablity-generator-chat-data.json
    - The metadata form JSON together with input data is used to detect whether
      the HTML files need to be regenerated
    - If input does not contain some data anymore, the old chat HTML is still
      kept and linked to the index files even if they are regenerated
      - In this case the new browseability-generator.json will be a merge of the
        new and old metadata
  - The Generated HTML is extremely plain and simple HTML with nice line feeds
  - A single static .css file is deployed to the output directory and referenced by the HTML files.
  - HTML files are placed in a nice hierarchy where at the top level there is
    single index.html
    - Chats are sorted in alpabetical order
    - Second level is folders with names of the chats
      - Contains YYYY.html files for per year chat files
      - Contains a media subfolder with all the media files referred to by the
        per year files

Technology:
  - Written in Python 3
  - Using minimal necessary 3rd party dependencies
  - Runnable directly from the git repository, instructions in README.md
  - Utilities are in their separate .py files in a subfolder

Difficulties:
  - Time formats and time zones are coded in _chat.txt files in localized
    format, timezone is unknown
    - Must provide a command line parameter to specify time locale
  - zipped Whatsapp export files are extracted to a temp folder for fast access

Overall Architeture:
  - A command line program with nice command line arguments and help
  - 5 main stages
    - 1. First scans the input directory to determine:
      - Different chats
      - Time ranges for which data is available
      - Locations of media files referred to by the chats
      - Constructs a ChatData data structure
    - 2. Check the status of the output directory
      - Checks the output directory for browseability-generator-chat-data.json
      - Constructs a second ChatData data structure from the JSON
    - 3. Looks at at ChatData data structures from stages 1. and 2.
      - Costructs a data structure of missing or changed chat data that should be generated from the input
      - Costructs a merged ChatData to be saved to browseability-generator-chat-data.json later
    - 4. Generate or regenerate missing HTML files based on output of previous step
    - 5. Update metadata JSON
      - Write merged data to `browseability-generator-chat-data-NEW.json`
      - rename `browseability-generator-chat-data.json` `browseability-generator-chat-data-BACKUP.json` (delete old backup if exists)
      - rename `browseability-generator-chat-data-NEW.json` to `browseability-generator-chat-data.json`

ChatData specification:
  - Contains all chat messages
    - If the message uses a media file:
      - contains a size of the media file as a number
      - contains a relative path to the location of the media file in the input
        folder (can be inside zip)
      - contains a relative path to the location of the media file in the output
        folder (possibly extracted)
        - (this is used in the HTML)
    - Timestamp without timezone information (whatsapp exports don't specify
      timezone, we can assume user knows it and is not confused)
    - The text content of the message (but not media)
      - We assume chat messages to be relatively small, only media files are
        large
    - The input file where the message was found in
    - Relative path to the possible per year HTML file where the message is
      placed in if the HTML file is already generated

## Running Tests

To run the tests for this project, use the following command:

```
python -m unittest discover -s tests -p "test_*.py"
```

This will automatically discover and run all test files in the `tests` directory that match the pattern `test_*.py`. Ensure you have Python 3 installed and are in the project root directory when running this command.


