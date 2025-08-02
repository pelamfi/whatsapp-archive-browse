# WhatsApp Chat Export Format Documentation

This document describes the structure and quirks of the `_chat.txt` format
exported from WhatsApp on an iPhone with a Finnish locale. It includes examples
and regex patterns to aid in parsing.

## General Structure
Each message in the chat follows this structure:

```
[DD.MM.YYYY klo HH.MM.SS] Sender: Message Content
```

### Components:
1. **Timestamp**:
   - Format: `[DD.MM.YYYY klo HH.MM.SS]`
   - Example: `[12.3.2022 klo 14.08.18]`
   - Regex: `\[\d{1,2}\.\d{1,2}\.\d{4} klo \d{1,2}\.\d{2}\.\d{2}\]`

2. **Sender**:
   - The name of the person or group sending the message.
   - Example: `Matias Virtanen`
   - Regex: `(?<=\] ).*?(?=: )`

3. **Message Content**:
   - The actual text of the message.
   - Example: `Blah blah`
   - Regex: `(?<=: ).*`

## Special Cases

### Media Attachments
- Media messages include a reference to the attached file.
- Format: `<liite: filename>`
- Example: `<liite: 00000074-PHOTO-2022-03-13-14-17-25.jpg>`
- Regex: `<liite: .*?>`

### System Messages
- Messages from the chat name (e.g., "Space Rocket") often indicate system actions.
- Examples:
  - `‎Viestit ja puhelut ovat täysin salattuja.` (Encryption status)
  - `Olet nyt ylläpitäjä` (Admin change)
- Regex: Match sender as the chat name.

### Special Characters
1. **U+200E (Left-to-Right Mark)**:
   - Appears before some names or text.
   - Likely enforces left-to-right text direction.
   - Can be considered noise for parsing.

2. **~ (Tilde)**:
   - Appears before some names.
   - Likely indicates system-generated messages or special roles (e.g., admin actions).

### Multi-line Messages
- Messages can span multiple lines, especially for links or long text.
- Example:
  ```
  Seli seli imaginary link
  https://example.com/linky
  ```

## Examples

### Regular Message
```
[12.3.2022 klo 14.08.18] Matias Virtanen: Blah blah
```

### Media Message
```
[13.3.2022 klo 14.17.25] Sami Ström: ‎<liite: 00000074-PHOTO-2022-03-13-14-17-25.jpg>
```

### System Message
```
[12.3.2022 klo 14.08.18] Space Rocket: ‎Viestit ja puhelut ovat täysin salattuja.
```

## Notes
- The chat name can be extracted from the first system message declaring encryption status.
- Localized elements (e.g., `klo`, `liite`) depend on the system locale.
- Timestamps do not include timezone information.
