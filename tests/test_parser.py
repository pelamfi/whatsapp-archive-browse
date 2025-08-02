import unittest
import os
from src.chat_data import ChatData
from src.parser import parse_chat_txt

class TestParser(unittest.TestCase):

    def test_parse_chat_txt(self):
        resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
        input_file = os.path.join(resource_dir, '_chat.txt')
        output_file = os.path.join(resource_dir, 'chat.json')
        base_dir = os.path.dirname(resource_dir)  # Set base directory

        # Parse the _chat.txt file
        chat_data = parse_chat_txt(input_file, base_dir=base_dir)

        # Serialize to JSON
        serialized_data = chat_data.to_json()

        # If chat.json is empty, update it with the serialized data
        if os.path.getsize(output_file) == 0:
            with open(output_file, 'w') as file:
                file.write(serialized_data)
            self.fail("chat.json was empty. It has been updated. Please verify its contents and re-run the test.")

        # Compare with the existing chat.json
        with open(output_file, 'r') as file:
            expected_data = file.read()

        self.assertEqual(serialized_data.strip(), expected_data.strip())

if __name__ == "__main__":
    unittest.main()
