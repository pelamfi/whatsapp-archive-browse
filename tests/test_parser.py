import os

import pytest

from src.chat_data import Chat, ChatData, ChatFile
from src.parser import parse_chat_file, parse_chat_files


def test_parse_chat_file():
    """Test parsing chat.txt and comparing with reference JSON"""
    resource_dir = os.path.join(os.path.dirname(__file__), "resources")
    input_file_path = os.path.join(resource_dir, "_chat.txt")
    output_file = os.path.join(resource_dir, "chat.json")

    # Create a ChatFile object
    input_file = ChatFile(
        path=input_file_path,
        parent_zip=None,
        modification_timestamp=os.path.getmtime(input_file_path),
        size=os.path.getsize(input_file_path),
    )

    # Parse the _chat.txt file
    chat_dict = parse_chat_file(input_file_path, input_file)

    # Create ChatData from the parsed chat
    first_chat_name = next(iter(chat_dict.keys()))  # Get the first (and only) chat's name
    messages = chat_dict[first_chat_name]  # Get the messages list
    chat = Chat(chat_name=first_chat_name, messages=messages)  # Create a Chat object
    chat_data = ChatData()
    chat_data.chats[first_chat_name] = chat  # Store the chat in ChatData

    # Serialize to JSON
    serialized_data = chat_data.to_json()

    # If chat.json is empty, update it with the serialized data
    if os.path.getsize(output_file) == 0:
        with open(output_file, "w") as file:
            file.write(serialized_data)
        pytest.fail("chat.json was empty. It has been updated. Please verify its contents and re-run the test.")

    # Compare with the existing chat.json
    with open(output_file, "r") as file:
        expected_data = file.read()

    assert serialized_data.strip() == expected_data.strip()


def test_parse_chat_files():
    """Test basic chat file parsing"""
    file_paths = ["example1.txt", "example2.txt"]
    locale = "FI"

    chat_files = parse_chat_files(file_paths, locale)

    assert len(chat_files) == len(file_paths)
    for i, chat_file in enumerate(chat_files):
        assert chat_file.path == file_paths[i]
        assert chat_file.parent_zip is None  # Update test if zip logic is added
        assert chat_file.modification_timestamp is None  # Placeholder
        assert chat_file.size is None  # Placeholder


def test_parse_chat_files_with_chatfile():
    """Test chat file parsing returns proper ChatFile objects"""
    file_paths = ["example1.txt", "example2.txt"]
    locale = "FI"

    chat_files = parse_chat_files(file_paths, locale)

    assert len(chat_files) == len(file_paths)
    for i, chat_file in enumerate(chat_files):
        assert isinstance(chat_file, ChatFile)
        assert chat_file.path == file_paths[i]
        assert chat_file.parent_zip is None  # Update test if zip logic is added
        assert chat_file.modification_timestamp is None  # Placeholder
        assert chat_file.size is None  # Placeholder
