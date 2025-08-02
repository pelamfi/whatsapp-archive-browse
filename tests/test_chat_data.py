import unittest
import os
from src.chat_data import ChatData, Message, MediaReference, ChatName

class TestChatData(unittest.TestCase):
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

    def test_serialization_round_trip(self):
        resource_path = os.path.join(os.path.dirname(__file__), 'resources', 'sample_chat_data.json')
        with open(resource_path, 'r') as file:
            json_data = file.read()

        chat_data = ChatData.from_json(json_data)
        serialized_data = chat_data.to_json()

        # Assert the serialized output matches the original JSON byte by byte
        self.assertEqual(json_data.strip(), serialized_data.strip())

if __name__ == "__main__":
    unittest.main()
