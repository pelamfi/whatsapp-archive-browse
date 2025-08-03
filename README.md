## Whatsapp Archive Browseability Generator

This tool scans a directory for exported Whatsapp archives, zipped or otherwise and
generates a clean static HTML folder where backed up Whatsapp chats can be
viewed.

This project is generated with the help of GPT-4o / Copilot.

NOTE: Work in progress! Only basic parsing code exists now.


## General Plan

Following plan is pure human output. I wrote it to get started with
the project and organize my own thoughts.

Then after 2 iterations with GPT-4o / Copilot we have [PLAN.md](./PLAN.md) 
for a more detailed step wise plan that makes it easy to ask AI agent to
work on a certain part of the plan.

Also see [FORMAT.md](./FORMAT.md) for the description of the Whatsapp `_chat.txt`
format.

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
    - 1. Check the status of the output directory
      - Checks the output directory for browseability-generator-chat-data.json
      - Constructs a second ChatData data structure from the JSON
    - 2. First scans the input directory to:
      - Detect different chats
      - Uses output of Stage 1 to detect changed / new _chat.txt files to do incremental scanning
      - Construct a coherent sequence of messages (Eliminate repeats etc)
      - Find and record locations of media files referred to by the chats
      - Constructs a ChatData data structure
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

## Development Setup

This project uses Python virtual environments for development. To set up:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

## Usage

This tool converts WhatsApp chat exports into browseable HTML files, preserving the chat history and media files.

### Basic Usage:

```bash
# Create and activate virtual environment (first time only)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements-dev.txt
pip install -e .

# Run the tool
python -m src.main --input path/to/whatsapp/export --output path/to/html/output
```

### Input Requirements:
- A folder containing WhatsApp chat exports
- Can contain multiple `_chat.txt` files from different exports
- Can handle both expanded exports and .zip files
- Media files can be in the same folder or subfolder structure

### Output Structure:
- Clean, static HTML files
- Year-based organization
- Preserved media files
- Index file listing all chats
- No external dependencies needed for viewing

### Example:
```bash
# Convert an expanded WhatsApp export
python -m src.main --input ~/Downloads/WhatsApp --output ~/Documents/chat-archive

# Specify a different locale (currently only FI supported)
python -m src.main --input ~/Downloads/WhatsApp --output ~/Documents/chat-archive --locale FI
```

## Development

### Setting Up Development Environment

This project uses Python virtual environments and strict type checking. To set up:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Development Tools

The project is configured with several development tools in `pyproject.toml`:

#### Code Quality Tools

The project uses several tools to maintain code quality:

##### Type Checking (mypy)

Static type checking with strict settings:

```bash
mypy src tests
```

##### Code Formatting (black)

Consistent code formatting:

```bash
# Check formatting
black --check src tests

# Auto-format code
black src tests
```

##### Import Sorting (isort)

Consistent import ordering:

```bash
# Check import ordering
isort --check-only src tests

# Fix import ordering
isort src tests
```

##### Code Linting (flake8)

Style guide enforcement:

```bash
flake8 src tests
```

#### Running Tests

Tests are written using pytest. Run:

```bash
# Run all tests
pytest

# Run with coverage report and generate HTML report
pytest --cov=src --cov-report=html

# View coverage report in browser (Linux)
xdg-open htmlcov/index.html

# Run specific test file
pytest tests/test_specific.py
```

#### Running All Checks

The project includes a build script that runs all quality checks:

```bash
./build.sh
```

This script:
1. Formats code with black
2. Sorts imports with isort
3. Runs flake8 linter
4. Runs mypy type checker
5. Runs tests with coverage report

The script uses bash strict mode (`set -euo pipefail`) and will stop on the first error. For code formatting issues (black and isort), it will automatically fix the problems.

You can also run individual checks as needed:

```bash
# Just format code
black src tests
isort src tests

# Just run tests
pytest

# Just check types
mypy src tests
```

#### IDE Integration

The project is configured to work well with modern IDEs through `pyproject.toml`:

- **VS Code**: Will automatically pick up:
  - Python version requirements
  - Type checking settings
  - Test configuration
  - Development dependencies

- **PyCharm**: Will recognize:
  - Project structure
  - Test configuration
  - Type checking settings

### Building and Distribution

The project uses standard Python packaging tools:

```bash
# Build distribution packages
python -m build

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Continuous Integration

The project's `pyproject.toml` configuration supports common CI practices:

- Type checking with mypy
- Test running with pytest
- Package building
- Development dependency management

All tools are configured through `pyproject.toml`, making it easy to run the same checks locally that will run in CI.

# Output directory structure

- Top level folder, the folder given with `--output` parameter contains:
  - `index.html` - allows access to known chats
  - `browseability-generator.css` - the common .css resource used by index.html files
  - `browseability-generator-chat-data.json` - metadata for incremental processing and maintaining chats for which archives no longer exists
  - `Chat Name` - Subdirectories for each known chat with the name of the chat as directory name
    - `index.html` - showing the chat name and links to per year `.html` files
    - `browseability-generator.css` - a copy of the .css to make the directory stand alone
    - `YYYY.html` - a per year HTML file for years for which chat messages exist for this chat