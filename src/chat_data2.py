import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, NotRequired, Optional, TypedDict, Union


@dataclass(frozen=True)
class ChatFileID:
    """Unique identifier for a file based on its path, size, and modification time."""

    value: str

    @staticmethod
    def create(mtime: float, size: int, path: str) -> "ChatFileID":
        """Creates a ChatFileID by hashing the file's metadata."""
        key = f"{mtime}:{size}:{path}"
        hash_obj = hashlib.sha1(key.encode(), usedforsecurity=False)
        return ChatFileID(base64.b64encode(hash_obj.digest()).decode())


class ChatFile2Dict(TypedDict):
    path: str
    size: int
    modification_timestamp: float
    parent_zip: NotRequired[Optional[str]]
    exists: NotRequired[bool]


@dataclass
class ChatFile2:
    path: str  # Relative path to the file within the containing directory or zip
    size: int  # Size of the file in bytes
    modification_timestamp: float  # Timestamp of last modification
    parent_zip: Optional[str] = None  # Path to the parent zip file, if any
    exists: bool = True  # Whether the file currently exists

    @property
    def id(self) -> ChatFileID:
        """Returns a unique identifier for this file based on its metadata."""
        return ChatFileID.create(
            mtime=self.modification_timestamp,
            size=self.size,
            path=self.path,
        )

    def to_dict(self) -> ChatFile2Dict:
        return {
            "path": self.path,
            "size": self.size,
            "modification_timestamp": self.modification_timestamp,
            "parent_zip": self.parent_zip,
            "exists": self.exists,
        }

    @staticmethod
    def from_dict(data: ChatFile2Dict) -> "ChatFile2":
        return ChatFile2(
            path=data["path"],
            size=data["size"],
            modification_timestamp=data["modification_timestamp"],
            parent_zip=data.get("parent_zip"),
            exists=data.get("exists", True),
        )


@dataclass
class Message2:
    # The timestamp of the message, stored verbatim without square brackets.
    timestamp: str
    # The sender of the message.
    sender: str
    # The content of the message.
    content: str
    # The year extracted from the timestamp, used to determine the output HTML file.
    year: int
    # The input file ID where the message was found.
    input_file_id: Optional[ChatFileID] = None
    # The ID of the media file reference, if found.
    media_file_id: Optional[ChatFileID] = None


@dataclass
class ChatName2:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChatName2):
            return self.name == other.name
        return False


class OutputFile2Dict(TypedDict):
    year: int
    generate: NotRequired[bool]
    media_dependencies: NotRequired[Dict[str, Optional[str]]]  # basename -> ChatFileID value
    chat_dependencies: NotRequired[List[str]]  # List of ChatFileID values
    css_dependency: NotRequired[str]  # ChatFileID value


@dataclass
class OutputFile2:
    """
    Represents a YYYY.html file in the output directory and tracks its dependencies.
    Dependencies are used to determine if the file needs to be regenerated.
    """

    year: int  # The year this file contains messages for
    generate: bool = False  # Whether this file needs to be regenerated this run
    media_dependencies: Dict[str, Optional[ChatFileID]] = field(default_factory=dict)  # basename -> ID
    chat_dependencies: List[ChatFileID] = field(default_factory=list)  # _chat.txt files
    css_dependency: Optional[ChatFileID] = None  # CSS resource dependency

    def to_dict(self) -> OutputFile2Dict:
        result: OutputFile2Dict = {
            "year": self.year,
            "generate": self.generate,
        }
        # Only include dependency fields if they have values
        if self.media_dependencies:
            result["media_dependencies"] = {
                basename: id.value if id else None for basename, id in self.media_dependencies.items()
            }
        if self.chat_dependencies:
            result["chat_dependencies"] = [id.value for id in self.chat_dependencies]
        if self.css_dependency:
            result["css_dependency"] = self.css_dependency.value
        return result

    @staticmethod
    def from_dict(data: OutputFile2Dict) -> "OutputFile2":
        return OutputFile2(
            year=data["year"],
            generate=data.get("generate", False),
            media_dependencies={
                basename: ChatFileID(value=id_value) if id_value else None
                for basename, id_value in data.get("media_dependencies", {}).items()
            },
            chat_dependencies=[ChatFileID(value=id_value) for id_value in data.get("chat_dependencies", [])],
            css_dependency=ChatFileID(value=css_id) if (css_id := data.get("css_dependency")) else None,
        )


def messages2_factory() -> List[Message2]:
    return []


def output_files2_factory() -> Dict[int, OutputFile2]:
    return {}


def chats2_factory() -> Dict[ChatName2, "Chat2"]:
    return {}


def input_files_factory() -> Dict[ChatFileID, ChatFile2]:
    return {}


@dataclass
class Chat2:
    chat_name: ChatName2
    messages: List[Message2] = field(default_factory=messages2_factory)
    output_files: Dict[int, OutputFile2] = field(default_factory=output_files2_factory)  # year -> OutputFile2


class Chat2Dict(TypedDict):
    messages: List[dict[str, Any]]
    output_files: Dict[str, OutputFile2Dict]


@dataclass
class ChatData2:
    chats: Dict[ChatName2, Chat2] = field(default_factory=chats2_factory)
    timestamp: str = "1970-01-01T00:00:00"  # Default timestamp, can be updated later
    input_files: Dict[ChatFileID, ChatFile2] = field(default_factory=input_files_factory)  # Repository of input files

    def to_json(self) -> str:
        def encode_key(key: ChatName2) -> str:
            return key.name

        def encode_chat(chat: Chat2) -> Chat2Dict:
            chat_dict: Dict[str, Any] = chat.__dict__.copy()
            del chat_dict["chat_name"]
            chat_dict["output_files"] = {str(year): file.to_dict() for year, file in chat.output_files.items()}
            return Chat2Dict(
                messages=chat_dict["messages"],
                output_files=chat_dict["output_files"],
            )

        def default_serializer(obj: Union[Message2, ChatFile2, ChatFileID]) -> Any:
            if isinstance(obj, ChatFileID):
                return obj.value
            return obj.__dict__

        return json.dumps(
            {
                "chats": {encode_key(k): encode_chat(v) for k, v in self.chats.items()},
                "input_files": {file_id.value: file.to_dict() for file_id, file in self.input_files.items()},
            },
            indent=4,
            sort_keys=True,
            default=default_serializer,
        )

    @staticmethod
    def from_json(data: str) -> "ChatData2":
        def decode_key(key: str) -> ChatName2:
            return ChatName2(name=key)

        def decode_message_list(messages: List[dict[str, Any]]) -> List[Message2]:
            def decode_message(msg: dict[str, Any]) -> Message2:
                # Create ID from legacy input_file data
                if "input_file" in msg and msg["input_file"] is not None:
                    file_data = msg.pop("input_file")
                    if isinstance(file_data, str):  # Handle legacy format
                        meta = ChatFile2(
                            path=str(file_data),
                            size=0,  # Legacy data doesn't have size info
                            modification_timestamp=0.0,  # Legacy data doesn't have timestamp
                            exists=False,  # Legacy file might not exist
                        )
                        msg["input_file_id"] = meta.id if meta.exists else None
                    else:
                        meta = ChatFile2(**dict(file_data))
                        msg["input_file_id"] = meta.id if meta.exists else None
                # Direct ID in new format
                elif isinstance(msg.get("input_file_id"), str):
                    msg["input_file_id"] = ChatFileID(value=msg["input_file_id"])

                # Handle media reference
                if "media" in msg and msg["media"] is not None:
                    media: dict[str, Any] = dict(msg["media"])  # Make a copy to modify

                    # Create ID from legacy media file data
                    if "input_path" in media and media["input_path"] is not None:
                        file_data = media["input_path"]
                        if isinstance(file_data, str):  # Handle legacy format
                            meta = ChatFile2(
                                path=str(file_data),
                                size=media.get("size", 0),  # Extract size if present
                                modification_timestamp=0.0,  # Legacy data doesn't have timestamp
                                exists=False,  # Legacy file might not exist
                            )
                        else:
                            meta = ChatFile2(**dict(file_data))
                        msg["media_file_id"] = meta.id if meta.exists else None
                # Direct ID in new format
                elif isinstance(msg.get("media_file_id"), str):
                    msg["media_file_id"] = ChatFileID(value=msg["media_file_id"])
                return Message2(**msg)

            return [decode_message(msg) for msg in messages]

        def decode_output_files(files_dict: dict[str, Any]) -> Dict[int, OutputFile2]:
            if not files_dict:
                return {}
            return {int(year): OutputFile2.from_dict(file_data) for year, file_data in files_dict.items()}

        obj: dict[str, Any] = json.loads(data)
        input_files = {
            ChatFileID(value=id_value): ChatFile2.from_dict(file_dict)
            for id_value, file_dict in obj.get("input_files", {}).items()
        }
        chats = {
            decode_key(k): Chat2(
                chat_name=decode_key(k),
                messages=decode_message_list(v.get("messages", [])),
                output_files=decode_output_files(v.get("output_files", {})),
            )
            for k, v in obj["chats"].items()
        }
        return ChatData2(chats=chats, input_files=input_files)
