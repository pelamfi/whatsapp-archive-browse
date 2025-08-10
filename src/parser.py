"""
Module for parsing WhatsApp chat export files.
"""

import re
from dataclasses import dataclass
from typing import Optional

from src.chat_data import Chat, ChatFile, ChatName, Message

"""
Module for parsing WhatsApp chat export files using chat_data structures.
"""


@dataclass
class RawChatLine:
    """
    A raw temporary parsed chat line. A raw line can be followed by more content
    lines, which are identified by them not matching the chat line format.
    """

    # Raw timestamp, part that is inside square brackets at the beginning of the
    # line.
    timestamp: str
    # timestamp is only considered valid if it contains a 4 digit year
    year: int
    # The timestamp is followed by the sender name followed by a colon.
    sender: str
    # The actual message content.
    content: str


# A single complex chat line regex to match the expected format of a WhatsApp
# chat line. It strips the U+200E characters and allows for some extra spaces
# and tildes (~) after the timestamp. It enforces that the timestamp contains 4
# digits for year number between 1900 and 2099, but otherwise the timestamp is
# taken verbatim.
#
# We Use a single regular expression to match and break down a _chat.txt line.
# This way we either get a match and know all components are present or we assume
# the line is a continuation of content (or some kind of line we don't have
# support for ATM).
chat_line_raw_regex = r"""(?xs)
    (?# This regex matches a single line of WhatsApp chat data)    (?# Match the start of the line)
    ^

    (?# Sometimes there is the right to left mark U+200E at the start, remove it)
    \u200E?

    (?# Match the timestamp in square brackets, ensure using non-greedy matchin that)
    (?# there is a 4 digit year somewhere and capture it to a separate group.)
    (?# Otherwise we treat the timestamp verbatim in the rest of the progam.)
    \[ (?P<timestamp> [^]]*? (?P<year> (?: 19 | 20 )[0-9][0-9] ) [^]]*? ) \]

    (?# Match the sender name trimming out spaces, possible left to right mark U+200E)
    (?# and tilde '~' wrapping, last of which is optional. Otherwise assume the sender)
    (?# name contains any characters except colon ':'. Note the use of backreference to
    (?# the tilde wrap group to not remove tilde in the beginning of content.)

    \s (?P<tildewrap>~\s)? (?P<sender>[^:]+) : \s \u200E? (?P=tildewrap)?

    (?# Match the content, which is everything after the colon, allowing for any characters)
    (?P<content> .*)

    (?# \n is included in content)
    """

chat_line_regex: re.Pattern[str] = re.compile(chat_line_raw_regex)


def parse_chat_line(line: str) -> Optional[RawChatLine]:
    """
    Parse a single line of chat data.

    Args:
        line: A single line from the chat file.

    Returns:
        A RawChatLine object if the line matches the expected format, otherwise None.
    """
    match: re.Match[str] | None = chat_line_regex.match(line)
    if match:
        return RawChatLine(
            timestamp=match.group("timestamp"),
            year=int(match.group("year")),
            sender=match.group("sender"),
            content=match.group("content"),
        )
    else:
        return None


# Lets assume this relatively relaxed pattern signals a media, it is not perfect
# as someone might type something similar into the chat. The part before colon
# is localized, so making this stricter would probably involve building a
# database of all possible WhatsApp localizations. I'm guessing 3 words composed of
# 1-20 unicode letters is generic enough to catch most locales.
# https://stackoverflow.com/a/79724794/1148030
media_regex: re.Pattern[str] = re.compile(r"<(?:[^\W\d_]{1,20}\s?){1,3}: (.*?)>")


def raw_chat_line_to_message(raw_line: RawChatLine, input_file: ChatFile) -> Message:
    """Convert a RawChatLine to a Message object."""
    content: str = raw_line.content
    media_name: Optional[str] = None

    # Check if the content contains a media reference
    media_match: re.Match[str] | None = media_regex.search(content)
    if media_match:
        # Store media filename, clear content as it's just a media reference
        media_name = media_match.group(1)
        # Remove media reference from content. Do we actually want a place
        # holder? I think media is always first and any "attached" text follows
        # it.
        content = content.replace(media_match.group(0), "")

    return Message(
        timestamp=raw_line.timestamp,
        sender=raw_line.sender,
        content=content,
        year=raw_line.year,
        input_file_id=input_file.id,
        media_name=media_name,
    )


def parse_chat_lines(lines: list[str], input_file: ChatFile) -> Optional[Chat]:
    """Parse a list of chat lines into a Chat object."""
    if len(lines) == 0:
        return None

    # First line sender is the chat name. If first line does not look like a chat line,
    # log an error and return None.
    first_raw_line: RawChatLine | None = parse_chat_line(lines[0])
    if not first_raw_line:
        return None

    chat_name = ChatName(name=first_raw_line.sender)
    messages: list[Message] = []

    current_raw_line: RawChatLine = first_raw_line
    content_lines: list[str] = [current_raw_line.content]

    # If the line matches the chat line format it begins a new message,
    # If it does not match it is assumed to be another line in the content of the last message.
    for line in lines[1:]:
        next_raw_line = parse_chat_line(line)
        if next_raw_line:
            # Before starting new message, finalize the previous message
            current_raw_line.content = "".join(content_lines)  # \n is included in content
            messages.append(raw_chat_line_to_message(current_raw_line, input_file))

            # Start new message
            current_raw_line = next_raw_line
            content_lines = [current_raw_line.content]
        else:
            # Continue existing message
            content_lines.append(line)

    # Finalize the last message
    current_raw_line.content = "".join(content_lines)
    messages.append(raw_chat_line_to_message(current_raw_line, input_file))

    return Chat(chat_name=chat_name, messages=messages)


def parse_chat_file(file_path: str, input_file: ChatFile) -> Optional[Chat]:
    """
    Parse a single WhatsApp _chat.txt file.

    Args:
        file_path: Path to the _chat.txt file
        input_file: ChatFile object representing the file

    Returns:
        Tuple of (Chat object, dict of input files) if successful, None if parsing fails
    """
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            lines = file.readlines()
            return parse_chat_lines(lines, input_file)
    except Exception as e:
        print(f"Failed to read chat file {file_path}: {e}")
        return None
