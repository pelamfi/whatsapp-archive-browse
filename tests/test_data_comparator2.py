"""
Tests for data comparator2 module.
"""

from typing import Set

from src.chat_data2 import Chat2, ChatName2, Message2, OutputFile2
from src.data_comparator2 import find_years_needing_update2, get_message_years2


def test_get_message_years2() -> None:
    """Test extracting years from a list of messages"""
    messages = [
        Message2(timestamp="12:00", sender="Alice", content="Hi", year=2022),
        Message2(timestamp="13:00", sender="Bob", content="Hello", year=2022),
        Message2(timestamp="14:00", sender="Alice", content="Hey", year=2023),
    ]

    years: Set[int] = get_message_years2(messages)
    assert years == {2022, 2023}


def test_find_years_needing_update2_no_output() -> None:
    """Test when there's no existing output"""
    input_chat = Chat2(
        chat_name=ChatName2("test"),
        messages=[
            Message2(timestamp="12:00", sender="Alice", content="Hi", year=2022),
            Message2(timestamp="13:00", sender="Bob", content="Hello", year=2023),
        ],
    )

    needs_update: Set[int] = find_years_needing_update2(input_chat, None)
    assert needs_update == {2022, 2023}


def test_find_years_needing_update2_with_changes() -> None:
    """Test detecting years that need updates"""
    # Create input chat with messages from 2022 and 2023
    input_chat = Chat2(
        chat_name=ChatName2("test"),
        messages=[
            Message2(timestamp="12:00", sender="Alice", content="Hi", year=2022),
            Message2(timestamp="13:00", sender="Bob", content="Hello", year=2023),
        ],
    )

    # Create output chat with:
    # - 2022 messages matching input (no update needed)
    # - 2023 messages different from input (update needed)
    # - Output file exists for 2022 but not 2023
    output_chat = Chat2(
        chat_name=ChatName2("test"),
        messages=[
            Message2(timestamp="12:00", sender="Alice", content="Hi", year=2022),
            Message2(timestamp="13:00", sender="Bob", content="Different", year=2023),
        ],
        output_files={2022: OutputFile2(year=2022)},
    )

    needs_update: Set[int] = find_years_needing_update2(input_chat, output_chat)
    assert needs_update == {2023}  # Both different content and missing output file
