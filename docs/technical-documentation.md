# Technical Documentation for WhatsApp Archive Browse

## Architecture Overview

The system processes WhatsApp chat exports through five main stages:

1. **Output Directory Check** (`output_checker.py`)
   - Checks output directory for `browseability-generator-chat-data.json`
   - Constructs ChatData structure from existing JSON metadata

2. **Input Directory Scan** (`input_scanner.py`)
   - Detects different chats across input files
   - Uses Stage 1 output to identify changed/new `_chat.txt` files
   - Constructs new ChatData structure from input

3. **Data Comparison and Merge** (`data_comparator.py`)
   - Analyzes ChatData structures from stages 1 & 2
   - Identifies missing/changed chat data needing generation
   - Creates merged ChatData for metadata persistence

4. **HTML Generation** (`html_generator.py`)
   - Generates/regenerates HTML files based on Stage 3 output
   - Creates hierarchical structure of chat files

5. **Metadata Update** (`metadata_updater.py`)
   - Writes merged data to `browseability-generator-chat-data-NEW.json`
   - Safely renames to final `browseability-generator-chat-data.json`

## Chat Data Flow

The system uses a unified data structure (`ChatData` in `chat_data.py`) that
serves multiple critical purposes:

1. **State Transfer Between Stages**
   - Acts as the primary interface between processing stages
   - Carries both chat content and processing metadata
   - Enables clean separation between processing phases

2. **Persistence Layer**
   - Serializes to `browseability-generator-chat-data.json`
   - Preserves chat history even when source files are lost
   - Maintains references to media files and HTML outputs

3. **Incremental Processing Support**
   - Tracks which files have been processed
   - Records message sources for change detection
   - Maps messages to their generated HTML locations

The structure maintains a hierarchical organization (chats → years → messages)
that mirrors the final HTML output structure. This alignment simplifies both the
generation process and future updates.

Each chat message maintains links to both its input sources (for change
detection) and output locations (for incremental updates), allowing the system
to make smart decisions about what needs to be regenerated during subsequent
runs.

## Output Directory Structure

```
output_directory/
├── index.html                              # Main access point to all chats
├── browseability-generator-chat-data.json  # Metadata for incremental updates
└── Chat Name/                             # Per-chat directories
    ├── index.html                         # Links to year files
    └── YYYY.html                          # Per-year chat content
```

## Current Implementation Status

The current implementation provides basic chat processing functionality. For the
latest status and detailed development plan, see [PLAN.md](../PLAN.md).

### Implemented Features
- Basic chat text parsing and HTML generation
- Simple directory structure for output
- Foundation for metadata tracking via `browseability-generator-chat-data.json`

### Planned Features
These features are designed but not yet implemented:

1. **Incremental Processing**
   - Smart change detection using stored metadata
   - Selective regeneration of affected files
   - Preservation of data from lost input files
   - See [PLAN.md](../PLAN.md) for implementation timeline

2. **Media File Handling**
   - Detection across expanded exports
   - ZIP file support
   - Efficient media file organization
   - Currently in design phase

## Message Format Handling

The system uses a heuristic approach to parse WhatsApp chat exports:

1. **Timestamp Parsing**
   - Uses regex patterns to identify timestamps by structure (square brackets)
   - Only enforces year number validation (1900-2099)
   - Preserves original timestamp format for display
   - Extracts year for file organization

2. **Message Structure**
   - Identifies messages through structural patterns (timestamps, colons)
   - Handles special characters (U+200E, tildes) without locale dependency
   - Supports multi-line message content

3. **Media References**
   - Detects media through generic patterns (`<text: filename>`)
   - Uses loose word matching to support different localizations
   - Extracts filenames without relying on specific locale formats

This approach prioritizes robustness over strict format validation, allowing the
system to handle various WhatsApp export formats without maintaining
locale-specific rules.

## Deployment Requirements

1. **Dependencies**
   - Python 3.x environment
   - Minimal third-party dependencies
   - Virtual environment recommended

2. **Installation**
   See [README.md](../README.md)

3. **Runtime**
   - No external services required
   - Static file output
   - Standalone HTML browsing

## Development Tools

Project uses several quality assurance tools:

1. **Type Checking**
   - Strict mypy configuration
   - Full type annotation coverage
   - Runtime type validation

2. **Code Quality**
   - Black for formatting
   - isort for import organization
   - flake8 for style enforcement

3. **Testing**
   - Primarily end-to-end tests. See [testing-approach.md](./testing-approach.md)
   - Reference file comparison
   - Automated test data management

## Future Improvements

1. **Planned Features**
   - Performance optimizations (The "VFS")
   - More granular incremental updates

2. **Technical Enhancements**
   - UV package manager integration
   - Ruff linter adoption
   - Expanded test coverage
   - Enhanced documentation
