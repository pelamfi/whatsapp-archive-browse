# WhatsApp Chat Export Format

This document describes how we parse WhatsApp `_chat.txt` exports, focusing on the structural patterns we rely on rather than exact formats.

## Core Message Structure

A basic message follows this pattern:
```
[timestamp] sender: content
```

Key characteristics we detect:
- Timestamps are always in square brackets `[...]`
- Must contain a 4-digit year (1900-2099) somewhere in the timestamp
- Sender name is followed by a colon and space
- Content continues until the next valid message line or EOF

## Special Formatting

Our parser handles these formatting variations:
1. **Right-to-Left Mark**: Optional U+200E character at line start
2. **Tilde Wrapping**: Some names are wrapped in `~` with spaces
3. **Multi-line Messages**: Lines without timestamp pattern are merged into previous message's content

## Chat Name Detection

We use a simple but effective approach:
- Chat name is extracted from the sender field of the first message
- This works because WhatsApp exports always start with system messages about the chat

## Media References

Media references are detected using loose pattern matching:
```
<word1 word2 word3: filename>
```

Key characteristics:
- Enclosed in angle brackets
- 1-3 words before the colon (to handle different localizations)
- Each word must be 1-20 letters (no numbers or symbols)
- Filename comes after the colon

## Example With Annotations

```
[12.3.2022 klo 14.08.18] Space Rocket: Messages are end-to-end encrypted...
└─ First message: "Space Rocket" becomes chat name

[12.3.2022 klo 14.10.56] ~ Juuso Kivi: ‎~ 
└─ Note the tilde wrapping and U+200E character

[13.3.2022 klo 14.17.25] Sami Ström: message with
continuation line
and another one
└─ Multiple lines combined into one message

‎[13.3.2022 klo 14.17.25] Sami Ström: ‎<liite: photo.jpg>
└─ Media reference detected and extracted
```

## Implementation Notes

1. **Year Extraction**
   - Only validate year exists (1900-2099)
   - Rest of timestamp kept as-is for display
   - Year used for file organization

2. **Message Continuation**
   - Any line not matching timestamp pattern
   - Added to previous message with newline
   - Preserves original formatting

3. **Error Handling**
   - Files without valid first line are rejected
   - Empty files are rejected
   - Invalid lines in middle of file become part of previous message

See `parser.py` for the implementation details, including the exact regular expressions used.
