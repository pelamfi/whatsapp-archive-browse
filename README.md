## Whatsapp Archive Browseability Generator

This tool scans a directory for exported Whatsapp archives, zipped or otherwise and
generates a clean static HTML folder where backed up Whatsapp chats can be
viewed.

This project is generated with the help of GPT-4o / Copilot.

NOTE: Work in progress! Only basic parsing code exists now.

## Testing Approach

This project uses a pragmatic testing approach focused on end-to-end tests. See
our detailed [testing approach documentation](./docs/testing-approach.md).

Key points:
- Primary testing is done through end-to-end tests in
  [`test_integration.py`](./tests/test_integration.py)
- Tests use a reference file system for easy verification and updates
- To update reference files after making changes:
  ```bash
  rm -rf tests/resources/reference_output/*
  pytest tests/test_integration.py
  ```
- Don't try to fix reference files manually - let the automation handle it
- The system makes it easy to understand what changed through git diffs

## Technical Overview

This tool provides a robust solution for managing and viewing WhatsApp chat
exports. It handles multiple exports intelligently, merging overlapping backups
into clean timelines while preserving all chat history. For comprehensive
technical details, see our [technical documentation](./docs/technical-documentation.md).

Key technical documents:
- [PLAN.md](./PLAN.md): Current development status and roadmap
- [chat-format.md](./docs/chat-format.md): WhatsApp chat export format details
- [Testing Approach](./docs/testing-approach.md): Our end-to-end testing strategy

## Development Setup

This project uses Python virtual environments for development. To set up:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package in development mode with all development dependencies
pip install -e ".[dev]"
```

## Usage

This tool converts WhatsApp chat exports into browseable HTML files, preserving the chat history and media files.

### Basic Usage:

```bash
# Create and activate virtual environment (first time only)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (first time only)
pip install -e ".[dev]"

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
  - `browseability-generator-chat-data.json` - metadata for incremental processing and maintaining chats for which archives no longer exists
  - `Chat Name` - Subdirectories for each known chat with the name of the chat as directory name
    - `index.html` - showing the chat name and links to per year `YYYY.html` files
    - `YYYY.html` - a per year HTML file for years for which chat messages exist for this chat


# Misc TODOs / Ideas

- Use uv
- Use ruff