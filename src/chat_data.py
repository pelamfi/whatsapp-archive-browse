from dataclasses import dataclass, field
from typing import List, Optional, Dict, TypedDict, NotRequired
import json

class ChatFileDict(TypedDict):
    path: str
    parent_zip: NotRequired[Optional[str]]
    modification_timestamp: NotRequired[Optional[float]]
    size: NotRequired[Optional[int]]

@dataclass
class ChatFile:
    path: str  # Relative path to the file
    parent_zip: Optional[str] = None  # Path to the parent zip file, if any
    modification_timestamp: Optional[float] = None  # Timestamp of last modification
    size: Optional[int] = None  # Size of the file in bytes

    def to_dict(self) -> ChatFileDict:
        return {
            "path": self.path,
            "parent_zip": self.parent_zip,
            "modification_timestamp": self.modification_timestamp,
            "size": self.size,
        }

    @staticmethod
    def from_dict(data: ChatFileDict) -> "ChatFile":
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChatName):
            return self.name == other.name
        return False

class OutputFileDict(TypedDict):
    year: int
    generate: NotRequired[bool]

@dataclass
class OutputFile:
    """
    Represents a YYYY.html file in the output directory.
    Used to track which files need to be regenerated on each run.
    """
    year: int  # The year this file contains messages for
    generate: bool = False  # Whether this file needs to be regenerated this run
    
    def to_dict(self) -> OutputFileDict:
        return {
            "year": self.year,
            "generate": self.generate
        }
    
    @staticmethod
    def from_dict(data: OutputFileDict) -> "OutputFile":
        return OutputFile(
            year=data["year"],
            generate=data.get("generate", False)
        )

from typing import Any, Dict, List, Optional, Union

def messages_factory() -> List[Message]:
    return []

def output_files_factory() -> Dict[int, OutputFile]:
    return {}

def chats_factory() -> Dict[ChatName, "Chat"]:
    return {}

@dataclass
class Chat:
    chat_name: ChatName
    messages: List[Message] = field(default_factory=messages_factory)
    output_files: Dict[int, OutputFile] = field(default_factory=output_files_factory)  # year -> OutputFile

class ChatDict(TypedDict):
    messages: List[dict[str, Any]]
    output_files: Dict[str, OutputFileDict]

@dataclass
class ChatData:
    chats: Dict[ChatName, Chat] = field(default_factory=chats_factory)
    timestamp: str = "1970-01-01T00:00:00"  # Default timestamp, can be updated later

    def to_json(self) -> str:
        def encode_key(key: ChatName) -> str:
            return key.name

        def encode_chat(chat: Chat) -> ChatDict:
            chat_dict = chat.__dict__.copy()
            del chat_dict['chat_name']
            chat_dict['output_files'] = {str(year): file.to_dict() for year, file in chat.output_files.items()}
            return ChatDict(
                messages=chat_dict['messages'],
                output_files=chat_dict['output_files']
            )

        def default_serializer(obj: Union[Message, MediaReference, ChatFile]) -> dict[str, Any]:
            return obj.__dict__

        return json.dumps(
            {"chats": {encode_key(k): encode_chat(v) for k, v in self.chats.items()}},
            indent=4,
            sort_keys=True,
            default=default_serializer
        )

    @staticmethod
    def from_json(data: str) -> 'ChatData':
        def decode_key(key: str) -> ChatName:
            return ChatName(name=key)

        def decode_message_list(messages: List[dict[str, Any]]) -> List[Message]:
            def decode_message(msg: dict[str, Any]) -> Message:
                # Convert input_file to ChatFile if present
                if 'input_file' in msg and msg['input_file'] is not None:
                    if isinstance(msg['input_file'], str):  # Handle legacy format
                        msg['input_file'] = ChatFile(path=str(msg['input_file']))
                    else:
                        input_file_data = dict(msg['input_file'])
                        msg['input_file'] = ChatFile(**input_file_data)
                
                # Handle media reference
                if 'media' in msg and msg['media'] is not None:
                    media: dict[str, Any] = dict(msg['media'])  # Make a copy to modify
                    
                    # Handle input_path
                    if 'input_path' in media and media['input_path'] is not None:
                        if isinstance(media['input_path'], str):  # Handle legacy format
                            size = media.pop('size', None)  # Extract size if present
                            media['input_path'] = ChatFile(path=str(media['input_path']), size=size)
                        else:
                            input_path_data = dict(media['input_path'])
                            media['input_path'] = ChatFile(**input_path_data)
                            
                    # Remove size if present (it's now in ChatFile)
                    media.pop('size', None)
                    
                    msg['media'] = MediaReference(**media)
                return Message(**msg)

            return [decode_message(msg) for msg in messages]

        def decode_output_files(files_dict: dict[str, Any]) -> Dict[int, OutputFile]:
            if not files_dict:
                return {}
            return {int(year): OutputFile.from_dict(OutputFileDict(
                        year=int(file_data.get('year', 0)),
                        generate=bool(file_data.get('generate', False))
                    ))
                   for year, file_data in files_dict.items()}

        obj = json.loads(data)
        obj['chats'] = {
            decode_key(k): Chat(
                chat_name=decode_key(k),
                messages=decode_message_list(v.get('messages', [])),
                output_files=decode_output_files(v.get('output_files', {}))
            ) for k, v in obj['chats'].items()
        }
        return ChatData(chats=obj['chats'])
