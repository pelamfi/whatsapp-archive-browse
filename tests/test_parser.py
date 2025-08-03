from src.chat_data import ChatFile
from src.parser import parse_chat_files


def test_parse_chat_files() -> None:
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
