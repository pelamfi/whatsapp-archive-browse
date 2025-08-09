# Implementation Plan for WhatsApp Archive Browse


This document outlines the next phase of development focusing on implementing incremental processing, efficient file handling, and ZIP support. For context, see:
- [technical-documentation.md](./technical-documentation.md) for current architecture
- [chat-format.md](./chat-format.md) for message parsing approach
- [testing-approach.md](./testing-approach.md) for testing strategy

## 1. Model Refactoring: ChatData2
Fundamental changes to support incremental processing and efficient file handling.

### 1.1 New Types and Properties
Core changes to [`chat_data.py`](../src/chat_data.py):
- Create `chat_data2.py` with suffixed type names (`ChatData2`, `ChatFile2`, etc.)
- Implement `ChatFileID` type for unique file identification
- Add file existence tracking and split path handling in `ChatFile2`
- Remove optional fields from `ChatFile2` where possible
- Convert file references to use `ChatFileID`

### 1.2 Message Structure Updates
- Remove embedded file data from `Message2`
- Keep core fields: timestamp, sender, content, year
- Convert file references to `ChatFileID`
- Remove HTML path (moving to `OutputFile2`)

### 1.3 Dependencies in OutputFile
Design new `OutputFile2` type for tracking dependencies:
```python
class OutputFile2:
    media_dependencies: Dict[str, Optional[ChatFileID]]  # basename -> ID
    chat_dependencies: List[ChatFileID]                  # _chat.txt files
    css_dependency: ChatFileID                          # CSS resource
```

### 1.4 Code Migration Strategy
- Keep old and new implementations parallel during development
- Use suffixed names to track progress
- Plan final rename operation to remove suffixes

## 2. Virtual File System (VFS)

### 2.1 File Information Cache
- Design efficient file lookup structure
- Implement ID generation (path + separator + size + separator + mtime)
- Create indices for quick file location

### 2.2 Multiple Access Patterns
Support multiple lookup methods:
- By relative path within input/zip
- By `ChatFileID`
- By filename (for media files)

### 2.3 ZIP File Integration
- Scan ZIP contents only when needed
- Cache ZIP file information
- Abstract file access for regular and ZIP files

## 3. Incremental Processing System
Updates required across multiple components:
- [`input_scanner.py`](../src/input_scanner.py): VFS integration
- [`data_comparator.py`](../src/data_comparator.py): Change detection
- [`metadata_updater.py`](../src/metadata_updater.py): State persistence
- [`html_generator.py`](../src/html_generator.py): Smart regeneration
- [`main.py`](../src/main.py): Flow coordination
- [`output_checker.py`](../src/output_checker.py): Metadata loading
- [`parser.py`](../src/parser.py): File abstraction

### 3.1 Change Detection
- Track file dependencies for each output file
- Detect changes through `ChatFileID` comparison
- Handle missing files gracefully

### 3.2 Smart Regeneration
- Only regenerate affected HTML files
- Copy only changed media files
- Preserve existing content when possible

### 3.3 State Management
- Merge old and new metadata
- Handle file relocation
- Track missing files

## 4. Testing and Verification

### 4.1 New Integration Tests
Focus on complex scenarios:
- Incremental updates with file changes
- ZIP file handling
- Missing file handling
- Multiple overlapping backups

### 4.2 Reference Output Updates
- Create new reference outputs for incremental cases
- Add ZIP file test cases
- Document expected behavior for each test case

## 5. Final Implementation Details

### 5.1 Clean-up Tasks
- Remove locale parameter (now using heuristics)
- Update error messages and logging
- Add HTML improvements (link detection)

### 5.2 Documentation Updates
- Update [technical-documentation.md](./technical-documentation.md) with VFS and incremental processing details
- Update [chat-format.md](./chat-format.md) if needed
- Add examples for incremental usage to README.md
- Document ZIP file support and new features
- Review and update [testing-approach.md](./testing-approach.md) if needed

### 5.3 Production Testing
- Test with large real-world data
- Measure and optimize performance
- Handle edge cases discovered in testing

## Notes on Implementation Approach

### Dependency Tracking
The core of incremental processing relies on careful dependency tracking:
- Each output file knows its exact dependencies
- Dependencies are tracked by `ChatFileID` to detect changes
- Missing files are tracked but don't trigger unnecessary regeneration

### Change Detection Strategy
To minimize unnecessary work:
- Compare file IDs instead of content
- Track only essential dependencies
- Handle relocated files without regeneration
- Preserve existing content when dependencies haven't changed

### Future Considerations
Potential enhancements after core implementation:
- Two-party chat detection and styling
- More sophisticated link handling
- Performance optimizations for large archives
