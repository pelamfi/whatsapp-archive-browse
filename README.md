## Whatsapp Archive Browseability Generator

This tool scans a directory for exported Whatsapp archives, zipped or otherwise
and generates a clean static HTML folder where backed up Whatsapp chats can be
viewed.

This project is partially generated with the help of Claude Sonnet 3.5 /
GPT-4o / Copilot.

## IMPORTANT DISCLAIMER!

**⚠️THIS IS EXPERIMENTAL SOFTWARE!!⚠️**

This software is very quickly put together and not tested very much!

**⚠️This software can contain serious bugs! Usage may result in loss of Whatsapp
archives and other files. ⚠️**

**⚠️USE AT YOUR OWN RISK!!⚠️**

## License

This software is licensed under the [MIT license.](LICENSE.txt)

## Usage and Setup

This tool converts WhatsApp chat exports into browseable HTML files, preserving the chat history and media files.

### Basic Usage:

NOTE: Unfortunately this tool has not yet been packaged into a stand alone tool.
This project uses Python virtual environments for development. So far this tool
can only be installed by cloning from git.

To set up:
```bash
# Create the virtual environment (first time only)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the package in development mode with all development dependencies
pip install -e ".[dev]"
```

And then to use:
```bash
# help
python -m src.main --help

# Run the tool, scan input for whatsapp exports (zipped or expanded), and generate HTML in output
python -m src.main --input ~/Downloads/WhatsAppExports --output ~/Documents/chat-archive
```

### Input Requirements:
- A folder containing WhatsApp chat exports
- Can contain multiple folders with `_chat.txt` files from different exports
- Can handle both expanded exports and .zip files
- Media files can be in the same folder or subfolder structure

### Output Structure:
- Clean, static HTML files
- Year-based organization
- Preserved media files
- Index files listing all chats and years per chat
- No external dependencies needed for viewing

The output from the tool will be roughly structured as follows:

- Top level folder, the folder given with `--output` parameter contains:
  - `index.html` - allows access to known chats
  - `browseability-generator-chat-data.json` - metadata for incremental processing and maintaining chats for which archives no longer exists
  - `Chat Name` - Subdirectories for each known chat with the name of the chat as directory name
    - `index.html` - showing the chat name and links to per year `YYYY.html` files
    - `YYYY.html` - a per year HTML file for years for which chat messages exist for this chat

## Development

### Technical Overview for Developers

This tool provides a robust solution for managing and viewing WhatsApp chat
exports. It handles multiple exports intelligently, merging overlapping backups
into clean timelines while preserving all chat history. For comprehensive
technical details, see our [technical documentation](./docs/technical-documentation.md).

Other key technical documents:
- [plan.md](./docs/plan.md): Current development status and roadmap
- [chat-format.md](./docs/chat-format.md): WhatsApp chat export format details
- [Testing Approach](./docs/testing-approach.md): Our end-to-end testing strategy

### Setting Up Development Environment

This project uses Python virtual environments and strict type checking.

The project is configured with several development tools in `pyproject.toml`:

To set up:
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run checks and tests
./build.sh
```

### Testing Approach

This project uses a pragmatic testing approach focused on end-to-end tests. See
our detailed [testing approach documentation](./docs/testing-approach.md).

Key points:
- Primary testing is done through end-to-end tests in
  [`test_integration.py`](./tests/test_integration.py)
- Tests use a reference file system for easy verification and updates
- To update reference files after making changes:
  ```bash
  ./build.sh --refresh-test-resources
  ```
- Don't try to fix reference files manually - let the automation handle it
  - Inspect the diffs to the previous data stored in git to understand and
    verify your changes.
- The system makes it easy to understand what changed through git diffs

### Code Quality Tools

The project uses several tools to maintain code quality:

### Type Checking (mypy)

Static type checking with strict settings:

```bash
mypy src tests
```

### Code Formatting (black)

Consistent code formatting:

```bash
# Check formatting
black --check src tests

# Auto-format code
black src tests
```

### Import Sorting (isort)

Consistent import ordering:

```bash
# Check import ordering
isort --check-only src tests

# Fix import ordering
isort src tests
```

### Code Linting (flake8)

Style guide enforcement:

```bash
flake8 src tests
```

### Running Tests

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

### Running All Checks

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

See above for how to run individual checks.

### Continuous Integration

The project's `pyproject.toml` configuration supports common CI practices, but a
CI has not been set up. All tools are configured through `pyproject.toml`,
making it in theory easy to run the same checks locally that will run in CI.

# TODOs / Issues

- Test and debug the incremental conversion
- Update the technical documents (stages in `main.py` have changed)
- Issue with senders / chats with colon `:` in the name
- Avoid copying media files that already exist in the output folder
- Identifying 2 party chats and rendering the speakers differently
  - IDEA: Command line option to give the name of "our user"
- Use a pattern to turn link looking things into a href links in the HTML output
- Identifying different media types
- Use uv
- Use ruff
- Packaging as a stand alone tool