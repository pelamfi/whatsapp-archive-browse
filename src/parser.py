import re
from src.chat_data import ChatData, Chat, ChatName, Message

def parse_chat_txt(file_path):
    chat_data = ChatData()

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    timestamp_regex = re.compile(r'\[(.*?)\]')
    year_regex = re.compile(r'\D(\d{4})\D')
    sender_regex = re.compile(r'(?<=\] ).*?(?=: )')
    content_regex = re.compile(r'(?<=: ).*')

    for line in lines:
        timestamp_match = timestamp_regex.search(line)
        year_match = year_regex.search(line)
        sender_match = sender_regex.search(line)
        content_match = content_regex.search(line)

        if timestamp_match and year_match and sender_match and content_match:
            timestamp = timestamp_match.group(1)
            year = int(year_match.group(1))
            sender = sender_match.group(0)
            content = content_match.group(0)

            chat_name = ChatName(name="Default Chat")
            if chat_name not in chat_data.chats:
                chat_data.chats[chat_name] = Chat(chat_name=chat_name)

            message = Message(timestamp=timestamp, sender=sender, content=content, year=year)
            chat_data.chats[chat_name].messages.append(message)

    return chat_data
