import re

from src.chat_data import ChatFile, ChatName, MediaReference, Message


def parse_chat_file(file_path: str, input_file: ChatFile) -> dict[ChatName, list[Message]]:
    """
    Parse a single WhatsApp _chat.txt file.

    Args:
        file_path: Path to the _chat.txt file
        input_file: ChatFile object representing the file

    Returns:
        Dict mapping ChatName to list of Messages from this file
    """
    messages_by_chat: dict[ChatName, list[Message]] = {}

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    timestamp_regex = re.compile(r"\[(.*?)\]")
    year_regex = re.compile(r"\D(\d{4})\D")
    sender_regex = re.compile(r"(?<=\] ).*?(?=: )")
    content_regex = re.compile(r"(?<=: ).*")
    media_regex = re.compile(r"<liite: (.*?)>")

    # Try to determine chat name from first few system messages
    chat_name = None
    for line in lines[:10]:  # Look at first 10 lines
        if "muutti ryhmän nimeksi" in line:
            match = re.search(r"muutti ryhmän nimeksi (.*)", line)
            if match:
                chat_name = match.group(1)
                break

    if not chat_name:
        chat_name = "Unknown Chat"

    chat_name = ChatName(name=chat_name)
    messages: list[Message] = []

    for line in lines:
        line = line.replace("\u200e", "")  # Remove U+200E characters

        timestamp_match = timestamp_regex.search(line)
        year_match = year_regex.search(line)
        sender_match = sender_regex.search(line)
        content_match = content_regex.search(line)
        media_match = media_regex.search(line)

        if timestamp_match and year_match and sender_match:
            timestamp = timestamp_match.group(1)
            year = int(year_match.group(1))
            sender = sender_match.group(0)

            content = content_match.group(0) if content_match else ""
            if media_match:
                raw_file_name = media_match.group(1)
                content = content.replace(f"<liite: {raw_file_name}>", "").strip()
                media = MediaReference(raw_file_name=raw_file_name)
            else:
                media = None

            message = Message(
                timestamp=timestamp,
                sender=sender,
                content=content,
                year=year,
                media=media,
                input_file=input_file,
            )
            messages.append(message)
        else:
            print(
                f"WARNING! Skipping line in file {file_path} due to unknown syntax: {line.strip()}"
            )

    messages_by_chat[chat_name] = messages
    return messages_by_chat


def parse_chat_files(file_paths: list[str], locale: str) -> list[ChatFile]:
    chat_files: list[ChatFile] = []
    for file_path in file_paths:
        chat_file = ChatFile(
            path=file_path,
            parent_zip=None,  # Update logic if file is inside a zip
            modification_timestamp=None,  # Replace with actual timestamp
            size=None,  # Replace with actual file size
        )
        chat_files.append(chat_file)
    return chat_files
