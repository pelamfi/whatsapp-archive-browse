from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json

@dataclass
class ChatFile:
    path: str  # Relative path to the file
    parent_zip: str = None  # Path to the parent zip file, if any
    modification_timestamp: str = None  # Timestamp of last modification
    size: int = None  # Size of the file in bytes

    def to_dict(self):
        return {
            "path": self.path,
            "parent_zip": self.parent_zip,
            "modification_timestamp": self.modification_timestamp,
            "size": self.size,
        }

    @staticmethod
    def from_dict(data):
        return ChatFile(
            path=data["path"],
            parent_zip=data.get("parent_zip"),
            modification_timestamp=data.get("modification_timestamp"),
            size=data.get("size"),
        )

@dataclass
class MediaReference:
    # The raw file name extracted from the content.
    raw_file_name: str
    # The input path of the media file, if known. Input file can be lost to time, so it is optional.
    input_path: Optional[ChatFile] = None
    # The output path of the media file, if known.
    output_path: Optional[str] = None

@dataclass
class Message:
    # The timestamp of the message, stored verbatim without square brackets.
    timestamp: str
    # The sender of the message.
    sender: str
    # The content of the message.
    content: str
    # The year extracted from the timestamp, used to determine the output HTML file.
    year: int
    # Optional media reference associated with the message.
    media: Optional[MediaReference] = None
    # The input file where the message was found. Input file can be lost to time, so it is optional.
    input_file: Optional[ChatFile] = None
    # Relative path to the possible per year HTML file where the message is placed.
    html_file: Optional[str] = None

@dataclass
class ChatName:
    name: str

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, ChatName):
            return self.name == other.name
        return False

@dataclass
class Chat:
    chat_name: ChatName
    messages: List[Message] = field(default_factory=list)

@dataclass
class ChatData:
    chats: Dict[ChatName, Chat] = field(default_factory=dict)

    def to_json(self) -> str:
        def encode_key(key):
            return key.name

        def encode_chat(chat):
            chat_dict = chat.__dict__.copy()
            del chat_dict['chat_name']
            return chat_dict

        def default_serializer(obj):
            if isinstance(obj, (Message, MediaReference, ChatFile)):
                return obj.__dict__
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        return json.dumps(
            {"chats": {encode_key(k): encode_chat(v) for k, v in self.chats.items()}},
            indent=4,
            sort_keys=True,
            default=default_serializer
        )

    @staticmethod
    def from_json(data: str) -> 'ChatData':
        def decode_key(key):
            return ChatName(name=key)

        def decode_message_list(messages):
            def decode_message(msg):
                # Convert input_file to ChatFile if present
                if 'input_file' in msg and msg['input_file'] is not None:
                    if isinstance(msg['input_file'], str):  # Handle legacy format
                        msg['input_file'] = ChatFile(path=msg['input_file'])
                    else:
                        msg['input_file'] = ChatFile(**msg['input_file'])
                
                # Handle media reference
                if 'media' in msg and msg['media'] is not None:
                    media = msg['media'].copy()  # Make a copy to modify
                    
                    # Handle input_path
                    if 'input_path' in media and media['input_path'] is not None:
                        if isinstance(media['input_path'], str):  # Handle legacy format
                            size = media.pop('size', None)  # Extract size if present
                            media['input_path'] = ChatFile(path=media['input_path'], size=size)
                        else:
                            media['input_path'] = ChatFile(**media['input_path'])
                            
                    # Remove size if present (it's now in ChatFile)
                    media.pop('size', None)
                    
                    msg['media'] = MediaReference(**media)
                return Message(**msg)

            return [decode_message(msg) for msg in messages]

        obj = json.loads(data)
        obj['chats'] = {decode_key(k): Chat(chat_name=decode_key(k), messages=decode_message_list(v['messages'])) for k, v in obj['chats'].items()}
        return ChatData(chats=obj['chats'])
