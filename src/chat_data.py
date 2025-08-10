import base64
import hashlib
import json
import os
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


class ChatFileDict(TypedDict):
    path: str
    size: int
    modification_timestamp: float
    parent_zip: NotRequired[Optional[str]]  # ChatFileID value as string when serialized
    exists: NotRequired[bool]


@dataclass(frozen=True)
class ChatFile:
    path: str  # Relative path to the file within the containing directory or zip
    size: int  # Size of the file in bytes
    modification_timestamp: float  # Timestamp of last modification
    parent_zip: Optional[ChatFileID] = None  # ChatFileID of the parent zip file, if any
    exists: bool = True  # Whether the file currently exists

    def __hash__(self) -> int:
        """Use the ID as hash key since the dataclass is frozen."""
        return hash(self.id)

    @property
    def id(self) -> ChatFileID:
        """Returns a unique identifier for this file based on its metadata."""
        return ChatFileID.create(
            mtime=self.modification_timestamp,
            size=self.size,
            path=self.path,
        )

    def to_dict(self) -> ChatFileDict:
        return {
            "path": self.path,
            "size": self.size,
            "modification_timestamp": self.modification_timestamp,
            "parent_zip": self.parent_zip.value if self.parent_zip else None,
            "exists": self.exists,
        }

    @staticmethod
    def from_dict(data: ChatFileDict) -> "ChatFile":
        parent_zip_value = data.get("parent_zip")
        return ChatFile(
            path=data["path"],
            size=data["size"],
            modification_timestamp=data["modification_timestamp"],
            parent_zip=ChatFileID(value=parent_zip_value) if parent_zip_value else None,
            exists=data.get("exists", True),
        )


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
    # The input file ID where the message was found.
    input_file_id: ChatFileID = ChatFileID(value="")
    # The name of the media file referenced in this message, if any.
    media_name: Optional[str] = None


@dataclass
class ChatName:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChatName):
            return self.name == other.name
        return False


class OutputFileDict(TypedDict):
    year: int
    generate: NotRequired[bool]
    media_dependencies: NotRequired[Dict[str, Optional[str]]]  # basename -> ChatFileID value as string
    chat_dependencies: NotRequired[List[str]]  # Set of ChatFileID values serialized as list of strings
    css_dependency: NotRequired[str]  # ChatFileID value as string


@dataclass
class OutputFile:
    """
    Represents a YYYY.html file in the output directory and tracks its dependencies.
    Dependencies are used to determine if the file needs to be regenerated.
    """

    year: int  # The year this file contains messages for
    generate: bool = False  # Whether this file needs to be regenerated this run
    media_dependencies: Dict[str, Optional[ChatFileID]] = field(default_factory=dict)  # basename -> ID
    chat_dependencies: set[ChatFileID] = field(default_factory=set)  # _chat.txt files
    css_dependency: Optional[ChatFileID] = None  # CSS resource dependency

    def to_dict(self) -> OutputFileDict:
        result: OutputFileDict = {
            "year": self.year,
            "generate": self.generate,
        }
        # Always include dependency fields even if empty
        result["media_dependencies"] = {
            basename: id.value if id else None for basename, id in self.media_dependencies.items()
        }
        if self.chat_dependencies:  # Only add if not empty since it's a set
            result["chat_dependencies"] = sorted(id.value for id in self.chat_dependencies)
        if self.css_dependency:  # Only add if exists since it's optional
            result["css_dependency"] = self.css_dependency.value
        return result

    @staticmethod
    def from_dict(data: OutputFileDict) -> "OutputFile":
        return OutputFile(
            year=data["year"],
            generate=data.get("generate", False),
            media_dependencies={
                basename: ChatFileID(value=id_value) if id_value else None
                for basename, id_value in data.get("media_dependencies", {}).items()
            },
            chat_dependencies={ChatFileID(value=id_value) for id_value in data.get("chat_dependencies", [])},
            css_dependency=ChatFileID(value=css_id) if (css_id := data.get("css_dependency")) else None,
        )


def messages_factory() -> List[Message]:
    return []


def output_files_factory() -> Dict[int, OutputFile]:
    return {}


def chats_factory() -> Dict[ChatName, "Chat"]:
    return {}


def input_files_factory() -> Dict[ChatFileID, ChatFile]:
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
    input_files: Dict[ChatFileID, ChatFile] = field(default_factory=input_files_factory)  # Repository of input files

    def to_json(self) -> str:
        def encode_key(key: ChatName) -> str:
            return key.name

        def encode_chat(chat: Chat) -> ChatDict:
            chat_dict: Dict[str, Any] = chat.__dict__.copy()
            del chat_dict["chat_name"]
            chat_dict["output_files"] = {str(year): file.to_dict() for year, file in chat.output_files.items()}
            return ChatDict(
                messages=chat_dict["messages"],
                output_files=chat_dict["output_files"],
            )

        def default_serializer(obj: Union[Message, ChatFile, ChatFileID]) -> Any:
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
    def from_json(data: str) -> "ChatData":
        def decode_key(key: str) -> ChatName:
            return ChatName(name=key)

        def decode_message_list(messages: List[dict[str, Any]]) -> List[Message]:
            def decode_message(msg: dict[str, Any]) -> Message:
                # Create ID from legacy input_file data
                if "input_file" in msg and msg["input_file"] is not None:
                    file_data = msg.pop("input_file")
                    if isinstance(file_data, str):  # Handle legacy format
                        meta = ChatFile(
                            path=str(file_data),
                            size=0,  # Legacy data doesn't have size info
                            modification_timestamp=0.0,  # Legacy data doesn't have timestamp
                            exists=False,  # Legacy file might not exist
                        )
                        msg["input_file_id"] = meta.id if meta.exists else None
                    else:
                        meta = ChatFile(**dict(file_data))
                        msg["input_file_id"] = meta.id if meta.exists else None
                # Direct ID in new format
                elif isinstance(msg.get("input_file_id"), str):
                    msg["input_file_id"] = ChatFileID(value=msg["input_file_id"])

                # Handle media reference
                if "media" in msg and msg["media"] is not None:
                    media: dict[str, Any] = dict(msg["media"])  # Make a copy to modify
                    # Convert legacy media format to just the filename
                    if "input_path" in media and media["input_path"] is not None:
                        if isinstance(media["input_path"], str):
                            msg["media_name"] = os.path.basename(media["input_path"])
                        else:
                            msg["media_name"] = os.path.basename(media["input_path"]["path"])
                # Handle new format
                elif "media_name" in msg:
                    msg["media_name"] = msg["media_name"]
                # Handle old media_file_id format by converting to media_name
                elif isinstance(msg.get("media_file_id"), str):
                    msg["media_name"] = msg.get("content", "")
                return Message(**msg)

            return [decode_message(msg) for msg in messages]

        def decode_output_files(files_dict: dict[str, Any]) -> Dict[int, OutputFile]:
            if not files_dict:
                return {}
            return {int(year): OutputFile.from_dict(file_data) for year, file_data in files_dict.items()}

        obj: dict[str, Any] = json.loads(data)
        input_files = {
            ChatFileID(value=id_value): ChatFile.from_dict(file_dict)
            for id_value, file_dict in obj.get("input_files", {}).items()
        }
        chats = {
            decode_key(k): Chat(
                chat_name=decode_key(k),
                messages=decode_message_list(v.get("messages", [])),
                output_files=decode_output_files(v.get("output_files", {})),
            )
            for k, v in obj["chats"].items()
        }
        return ChatData(chats=chats, input_files=input_files)
