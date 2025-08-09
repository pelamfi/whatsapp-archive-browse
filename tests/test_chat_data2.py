import os

from src.chat_data2 import Chat2, ChatData2, ChatFile2, ChatFile2Dict, ChatName2, Message2, OutputFile2


def test_deserialization_from_file() -> None:
    resource_path = os.path.join(os.path.dirname(__file__), "resources", "sample_chat_data2.json")
    with open(resource_path, "r") as file:
        json_data = file.read()

    chat_data: ChatData2 = ChatData2.from_json(json_data)

    # Assert a few fields
    assert ChatName2(name="Space Rocket") in chat_data.chats
    chat: Chat2 = chat_data.chats[ChatName2(name="Space Rocket")]
    assert len(chat.messages) == 1
    assert chat.messages[0].sender == "Matias Virtanen"


def test_serialization() -> None:
    # Create a chat file with known metadata
    chat_file = ChatFile2(
        path="_chat.txt",
        size=100,
        modification_timestamp=1647093600.0,  # 2022-03-12 14:00:00 UTC
    )
    chat_file_id = chat_file.id

    # Create a media file with known metadata
    media_file = ChatFile2(
        path="inputfolder/input.jpg",
        size=12345,
        modification_timestamp=1647093600.0,  # 2022-03-12 14:00:00 UTC
    )
    media_file_id = media_file.id

    # Create message with file IDs
    message = Message2(
        timestamp="2022-03-12T14:08:18",
        sender="Matias Virtanen",
        content="Hello World",
        year=2022,
        input_file_id=chat_file_id,
        media_file_id=media_file_id,
    )

    # Create chat data with output file dependencies
    output_file = OutputFile2(
        year=2022, generate=True, media_dependencies={"input.jpg": media_file_id}, chat_dependencies=[chat_file_id]
    )

    chat_data = ChatData2(
        chats={
            ChatName2(name="Space Rocket"): Chat2(
                chat_name=ChatName2(name="Space Rocket"), messages=[message], output_files={2022: output_file}
            )
        }
    )

    json_data: str = chat_data.to_json()
    deserialized: ChatData2 = ChatData2.from_json(json_data)

    assert len(deserialized.chats) == 1
    assert ChatName2(name="Space Rocket") in deserialized.chats
    chat: Chat2 = deserialized.chats[ChatName2(name="Space Rocket")]
    assert len(chat.messages) == 1
    assert chat.messages[0].timestamp == "2022-03-12T14:08:18"
    assert chat.messages[0].input_file_id == chat_file_id
    assert chat.messages[0].media_file_id == media_file_id

    # Check output file dependencies were preserved
    output_file = chat.output_files[2022]
    assert output_file.media_dependencies["input.jpg"] == media_file_id
    assert output_file.chat_dependencies == [chat_file_id]


def test_serialization_round_trip() -> None:
    resource_path: str = os.path.join(os.path.dirname(__file__), "resources", "sample_chat_data2.json")
    with open(resource_path, "r") as file:
        json_data: str = file.read()

    chat_data: ChatData2 = ChatData2.from_json(json_data)
    serialized_data: str = chat_data.to_json()

    # Log the produced JSON for easier resource file updates
    print("Produced JSON:")
    print(serialized_data)

    # Assert the serialized output matches the original JSON byte by byte
    assert json_data.strip() == serialized_data.strip()


def test_chat_file_serialization() -> None:
    chat_file = ChatFile2(
        path="example.txt",
        parent_zip="archive.zip",
        modification_timestamp=1754448000.0,
        size=1024,
    )
    serialized: ChatFile2Dict = chat_file.to_dict()
    deserialized: ChatFile2 = ChatFile2.from_dict(serialized)

    assert deserialized.path == chat_file.path
    assert deserialized.parent_zip == chat_file.parent_zip
    assert deserialized.modification_timestamp == chat_file.modification_timestamp
    assert deserialized.size == chat_file.size


def test_chat_file_id() -> None:
    # Create two identical files
    file1 = ChatFile2(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448000.0,
    )
    file2 = ChatFile2(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448000.0,
    )
    # IDs should be equal for identical files
    assert file1.id == file2.id

    # Create a file with different metadata
    file3 = ChatFile2(
        path="example.txt",
        size=1024,
        modification_timestamp=1754448001.0,  # Different timestamp
    )
    # IDs should be different
    assert file1.id != file3.id
