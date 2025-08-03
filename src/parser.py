import os
import re
from src.chat_data import ChatData, Chat, ChatName, Message, MediaReference, ChatFile

def parse_chat_txt(file_path, base_dir):
    chat_data = ChatData()

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    timestamp_regex = re.compile(r'\[(.*?)\]')
    year_regex = re.compile(r'\D(\d{4})\D')
    sender_regex = re.compile(r'(?<=\] ).*?(?=: )')
    content_regex = re.compile(r'(?<=: ).*')
    media_regex = re.compile(r'<liite: (.*?)>')

    for line in lines:
        line = line.replace('\u200e', '')  # Remove U+200E characters

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

            chat_name = ChatName(name="Default Chat")
            if chat_name not in chat_data.chats:
                chat_data.chats[chat_name] = Chat(chat_name=chat_name)

            relative_file_path = os.path.relpath(file_path, base_dir)
            message = Message(timestamp=timestamp, sender=sender, content=content, year=year, media=media, input_file=relative_file_path)
            chat_data.chats[chat_name].messages.append(message)

    return chat_data

def parse_chat_files(file_paths, locale):
    chat_files = []
    for file_path in file_paths:
        chat_file = ChatFile(
            path=file_path,
            parent_zip=None,  # Update logic if file is inside a zip
            modification_timestamp=None,  # Replace with actual timestamp
            size=None,  # Replace with actual file size
        )
        # Example usage in Message and MediaReference
        message = Message(input_file=chat_file)
        media_reference = MediaReference(input_path=chat_file)
        chat_files.append(chat_file)
    return chat_files
