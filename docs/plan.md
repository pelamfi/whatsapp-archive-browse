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

Done. Details removed to save space.

## 2. Processing Pipeline Refactoring

### 2.1 New Stage Files
Create new implementations alongside existing ones:

- ['vfs.py']
  - Data structure and functions to support vfs_scanner and querying vfs.

- [`vfs_scanner.py`](../src/vfs_scanner.py): Stage 1 - VFS scanning
  - Takes over file discovery from `output_checker.py`
  - Merges new and old file information
  - Maintains file existence flags
  - Integrates with ZIP handling

- [`message_processor.py`](../src/message_processor.py): Stage 2 - Message processing
  - Focuses on chat text parsing and deduplication
  - Sorts messages by _chat.txt timestamps
  - Handles message deduplication per chat
  - Works with both new and preserved messages

- [`media_locator.py`](../src/media_locator.py): Stage 3 - Media handling
  - Dedicated to media file discovery
  - Uses VFS for efficient file lookup
  - Implements smart file matching logic
  - Handles both local and ZIP-based media

### 2.2 Migration Strategy
- Keep existing stages functional during development
- Gradually shift functionality to new stages
- Update `main.py` to coordinate new pipeline
- Remove old stages once migration is complete

## 3. Virtual File System (VFS)

### 3.1 File Information Cache
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

### Notes about the refacoring:

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

