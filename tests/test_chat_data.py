import os

from src.chat_data import Chat, ChatData, ChatFile, ChatFileDict, ChatName, Message, OutputFile


def test_deserialization_from_file() -> None:
    resource_path = os.path.join(os.path.dirname(__file__), "resources", "sample_chat_data.json")
    with open(resource_path, "r") as file:
        json_data = file.read()

    chat_data: ChatData = ChatData.from_json(json_data)

    # Assert a few fields
    assert ChatName(name="Space Rocket") in chat_data.chats
    chat: Chat = chat_data.chats[ChatName(name="Space Rocket")]
    assert len(chat.messages) == 1
    assert chat.messages[0].sender == "Matias Virtanen"


def test_serialization() -> None:
    # Create a zip file first to serve as parent
    zip_file = ChatFile(
        path="backup.zip",
        size=5000,
        modification_timestamp=1647093600.0,  # 2022-03-12 14:00:00 UTC
    )
    zip_file_id = zip_file.id

    # Create a chat file with known metadata
    chat_file = ChatFile(
        path="_chat.txt",
        size=100,
        modification_timestamp=1647093600.0,  # 2022-03-12 14:00:00 UTC
    )
    chat_file_id = chat_file.id

    # Create a media file with known metadata (inside the zip)
    media_file = ChatFile(
        path="inputfolder/input.jpg",
        size=12345,
        modification_timestamp=1647093600.0,  # 2022-03-12 14:00:00 UTC
        parent_zip=zip_file_id,  # This file is inside the zip
    )
    media_file_id = media_file.id

    # Create message with file IDs
    message = Message(
        timestamp="2022-03-12T14:08:18",
        sender="Matias Virtanen",
        content="Hello World",
        year=2022,
        input_file_id=chat_file_id,
        media_name="input.jpg",
    )

    # Create chat data with output file dependencies
    output_file = OutputFile(
        year=2022, generate=True, media_dependencies={"input.jpg": media_file_id}, chat_dependencies={chat_file_id}
    )

    chat_data = ChatData(
        chats={
            ChatName(name="Space Rocket"): Chat(
                chat_name=ChatName(name="Space Rocket"), messages=[message], output_files={2022: output_file}
            )
        },
        input_files={chat_file_id: chat_file, media_file_id: media_file, zip_file_id: zip_file},
    )

    json_data: str = chat_data.to_json()

    resource_path: str = os.path.join(os.path.dirname(__file__), "resources", "sample_chat_data.json")

    # check if the resource file exists
    if not os.path.exists(resource_path):
        # write the resource path and report
        with open(resource_path, "w", encoding="utf-8", newline="") as file:
            file.write(json_data)
        print("Updated resource file:", resource_path)
        # fail test to get attention
        assert False, "Resource file was updated, please rerun tests."

    deserialized: ChatData = ChatData.from_json(json_data)

    assert len(deserialized.chats) == 1
    assert ChatName(name="Space Rocket") in deserialized.chats
    chat: Chat = deserialized.chats[ChatName(name="Space Rocket")]
    assert len(chat.messages) == 1
    assert chat.messages[0].timestamp == "2022-03-12T14:08:18"
    assert chat.messages[0].input_file_id == chat_file_id
    assert chat.messages[0].media_name == "input.jpg"

    # Check output file dependencies were preserved
    output_file = chat.output_files[2022]
    assert output_file.media_dependencies["input.jpg"] == media_file_id
    assert output_file.chat_dependencies == {chat_file_id}


def test_serialization_round_trip() -> None:
    resource_path: str = os.path.join(os.path.dirname(__file__), "resources", "sample_chat_data.json")
    with open(resource_path, "r") as file:
        json_data: str = file.read()

    chat_data: ChatData = ChatData.from_json(json_data)
    serialized_data: str = chat_data.to_json()

    # Assert the serialized output matches the original JSON byte by byte
    assert json_data.strip() == serialized_data.strip()


def test_chat_file_serialization() -> None:
    # Create a zip file first to get its ID
    zip_file = ChatFile(
        path="archive.zip",
        size=2048,
        modification_timestamp=1754448000.0,
    )

    chat_file = ChatFile(
        path="example.txt",
        parent_zip=zip_file.id,
        modification_timestamp=1754448000.0,
        size=1024,
    )
    serialized: ChatFileDict = chat_file.to_dict()
    deserialized: ChatFile = ChatFile.from_dict(serialized)

    assert deserialized.path == chat_file.path
    assert deserialized.parent_zip == chat_file.parent_zip
    assert deserialized.modification_timestamp == chat_file.modification_timestamp
    assert deserialized.size == chat_file.size


def test_chat_file_id() -> None:
    # Create two identical files
    file1 = ChatFile(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448000.0,
    )
    file = ChatFile(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448000.0,
    )
    # IDs should be equal for identical files
    assert file1.id == file.id

    # Create a file with different metadata
    file3 = ChatFile(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448001.0,  # Different timestamp
    )
    # IDs should be different
    assert file1.id != file3.id
