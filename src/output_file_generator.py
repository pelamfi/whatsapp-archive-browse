"""
Generate OutputFile records for each chat based on message years and dependencies.
"""

from src.chat_data import ChatData, OutputFile


def generate_output_files(chat_data: ChatData) -> None:
    """
    Generate OutputFile records for each chat in ChatData.
    Each year that has messages gets an OutputFile with appropriate dependencies.

    Args:
        chat_data: ChatData to generate output files for
    """
    # First clear any existing output files
    for chat in chat_data.chats.values():
        chat.output_files.clear()

        # Group messages by year and collect chat dependencies
        message_years = set()
        chat_dependencies = set()

        for msg in chat.messages:
            message_years.add(msg.year)
            if msg.input_file_id.value:
                chat_dependencies.add(msg.input_file_id)

        # Create output file for each year with messages
        for year in message_years:
            output_file = OutputFile(year=year)
            output_file.chat_dependencies.update(chat_dependencies)
            chat.output_files[year] = output_file
