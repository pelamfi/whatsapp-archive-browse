import re
from src.chat_data import ChatData, Chat, ChatName, Message

def parse_chat_txt(file_path):
    chat_data = ChatData()

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    timestamp_regex = re.compile(r'\[\d{1,2}\.\d{1,2}\.\d{4} klo \d{1,2}\.\d{2}\.\d{2}\]')
    sender_regex = re.compile(r'(?<=\] ).*?(?=: )')
    content_regex = re.compile(r'(?<=: ).*')

    for line in lines:
        timestamp_match = timestamp_regex.search(line)
        sender_match = sender_regex.search(line)
        content_match = content_regex.search(line)

        if timestamp_match and sender_match and content_match:
            timestamp = timestamp_match.group(0)
            sender = sender_match.group(0)
            content = content_match.group(0)

            # For simplicity, assume all messages belong to one chat named "Default Chat"
            chat_name = ChatName(name="Default Chat")
            if chat_name not in chat_data.chats:
                chat_data.chats[chat_name] = Chat(chat_name=chat_name)

            message = Message(timestamp=timestamp, sender=sender, content=content)
            chat_data.chats[chat_name].messages.append(message)

    return chat_data
