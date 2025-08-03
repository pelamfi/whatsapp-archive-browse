import unittest
import os
from src.chat_data import ChatData, Message, MediaReference, ChatName, Chat, ChatFile

class TestChatData(unittest.TestCase):
    maxDiff = None

    def test_deserialization_from_file(self):
        resource_path = os.path.join(os.path.dirname(__file__), 'resources', 'sample_chat_data.json')
        with open(resource_path, 'r') as file:
            json_data = file.read()

        chat_data = ChatData.from_json(json_data)

        # Assert a few fields
        self.assertIn(ChatName(name="Space Rocket"), chat_data.chats)
        chat = chat_data.chats[ChatName(name="Space Rocket")]
        self.assertEqual(len(chat.messages), 1)
        self.assertEqual(chat.messages[0].sender, "Matias Virtanen")
        self.assertEqual(chat.messages[0].media.size, 12345)

    def test_serialization(self):
        media = MediaReference(
            raw_file_name="input.jpg",
            size=12345,
            input_path="inputfolder/input.jpg",
            output_path="outputfolder/input.jpg"
        )
        message = Message(
            timestamp="2022-03-12T14:08:18",
            sender="Matias Virtanen",
            content="Hello World",
            year=2022,
            media=media,
            input_file="_chat.txt",
            html_file="2022.html"
        )
        chat_data = ChatData(chats={ChatName(name="Space Rocket"): Chat(chat_name=ChatName(name="Space Rocket"), messages=[message])})

        json_data = chat_data.to_json()
        deserialized = ChatData.from_json(json_data)

        self.assertEqual(len(deserialized.chats), 1)
        self.assertIn(ChatName(name="Space Rocket"), deserialized.chats)
        chat = deserialized.chats[ChatName(name="Space Rocket")]
        self.assertEqual(len(chat.messages), 1)
        self.assertEqual(chat.messages[0].timestamp, "2022-03-12T14:08:18")
        self.assertEqual(chat.messages[0].media.raw_file_name, "input.jpg")
        self.assertEqual(chat.messages[0].media.size, 12345)
        self.assertEqual(chat.messages[0].media.input_path, "inputfolder/input.jpg")
        self.assertEqual(chat.messages[0].media.output_path, "outputfolder/input.jpg")
        self.assertEqual(chat.messages[0].input_file, "_chat.txt")
        self.assertEqual(chat.messages[0].html_file, "2022.html")

    def test_serialization_round_trip(self):
        resource_path = os.path.join(os.path.dirname(__file__), 'resources', 'sample_chat_data.json')
        with open(resource_path, 'r') as file:
            json_data = file.read()

        chat_data = ChatData.from_json(json_data)
        serialized_data = chat_data.to_json()

        # Log the produced JSON for easier resource file updates
        # print("Produced JSON:")
        # print(serialized_data)

        # Assert the serialized output matches the original JSON byte by byte
        self.assertEqual(json_data.strip(), serialized_data.strip())

    def test_chat_file_serialization(self):
        chat_file = ChatFile(
            path="example.txt",
            parent_zip="archive.zip",
            modification_timestamp="2025-08-03T12:00:00",
            size=1024,
        )
        serialized = chat_file.to_dict()
        deserialized = ChatFile.from_dict(serialized)

        self.assertEqual(deserialized.path, chat_file.path)
        self.assertEqual(deserialized.parent_zip, chat_file.parent_zip)
        self.assertEqual(deserialized.modification_timestamp, chat_file.modification_timestamp)
        self.assertEqual(deserialized.size, chat_file.size)

    def test_message_with_chatfile(self):
        chat_file = ChatFile(
            path="example.txt",
            parent_zip="archive.zip",
            modification_timestamp="2025-08-03T12:00:00",
            size=1024,
        )
        message = Message(
            timestamp="2022-03-12T14:08:18",
            sender="Matias Virtanen",
            content="Hello World",
            year=2022,
            input_file=chat_file,
            html_file="2022.html"
        )

        self.assertEqual(message.input_file, chat_file)

    def test_media_reference_with_chatfile(self):
        chat_file = ChatFile(
            path="media.jpg",
            parent_zip=None,
            modification_timestamp="2025-08-03T12:00:00",
            size=2048,
        )
        media_reference = MediaReference(
            raw_file_name="media.jpg",
            size=2048,
            input_path=chat_file,
            output_path="outputfolder/media.jpg"
        )

        self.assertEqual(media_reference.input_path, chat_file)

if __name__ == "__main__":
    unittest.main()
