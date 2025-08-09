import re
from dataclasses import dataclass

from src.chat_data import Chat, ChatFile, ChatName, MediaReference, Message


# A raw temporary parsed chat line. A raw line can be followed by more content
# lines, which are identified by them not matching the chat line format.
@dataclass
class RawChatLine:
    # Raw timestamp, part that is inside square brackets at the beginning of the
    # line.
    timestamp: str
    # timestamp is only considered valid if it contains a 4 digit year
    year: int
    # The timestamp is followed by the sender name followed by a colon. This
    # part can also contain extra spaces, tilde (~) and sometimes U+200E
    # characters, which are filtered out.
    sender: str
    # the content, the part that comes after the colon.
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
chat_line_raw_regex = r"""(?x)
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

    (?# Match end of line)
    $
    """

chat_line_regex: re.Pattern[str] = re.compile(chat_line_raw_regex)


def parse_chat_line(line: str) -> RawChatLine | None:
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
    media: MediaReference | None = None
    content: str = raw_line.content

    # Check if the content contains a media reference
    media_match: re.Match[str] | None = media_regex.search(content)
    if media_match:
        raw_file_name: str = media_match.group(1)
        content = content.replace(media_match.group(0), "")
        media = MediaReference(raw_file_name=raw_file_name)

    return Message(
        timestamp=raw_line.timestamp,
        sender=raw_line.sender,
        content=content,
        year=raw_line.year,
        media=media,
        input_file=input_file,
    )


def parse_chat_lines(lines: list[str], input_file: ChatFile) -> Chat | None:

    if len(lines) == 0:
        print(f"WARNING! Empty chat file {input_file.path}, skipping.")
        return None

    # First line sender is the chat name. If fist line does not look like a chat line,
    # log an error and return empty None.
    first_raw_line: RawChatLine | None = parse_chat_line(lines[0])

    if not first_raw_line:
        print(f"WARNING! First line in file {input_file.path} does not match expected chat line format: {lines[0]}")
        return None

    chat_name_typed = ChatName(name=first_raw_line.sender)

    prev_raw_line: RawChatLine = first_raw_line

    messages: list[Message] = []

    # If the line matches the chat line format it begins a new message,
    # If it does not match it is assumed to be another line in the content of the last message.
    for line in lines[1:]:
        raw_line: RawChatLine | None = parse_chat_line(line)
        if raw_line:
            # If the line is a new chat line, create a message from the previous raw line
            if prev_raw_line:
                messages.append(raw_chat_line_to_message(prev_raw_line, input_file))
            prev_raw_line = raw_line
        else:
            # If the line does not match the chat line format, append it to the content of the last message
            if prev_raw_line:
                prev_raw_line.content += "\n" + line.strip()

    # At this point we at least have the first line because we would have returned None if there were no lines.
    messages.append(raw_chat_line_to_message(prev_raw_line, input_file))

    return Chat(
        chat_name=chat_name_typed,
        messages=messages,
    )


def parse_chat_file(file_path: str, input_file: ChatFile) -> Chat | None:
    """
    Parse a single WhatsApp _chat.txt file.

    Args:
        file_path: Path to the _chat.txt file
        input_file: ChatFile object representing the file
    """

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        lines: list[str] = file.readlines()

    return parse_chat_lines(lines, input_file)
