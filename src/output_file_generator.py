"""
Generate OutputFile records for each chat based on message years and dependencies.
"""

from src.chat_data import ChatData, ChatFileID, OutputFile


def generate_output_files(chat_data: ChatData) -> None:
    """
    Generate OutputFile records for each chat in ChatData.
    Each year that has messages gets an OutputFile with appropriate dependencies.

    Args:
        chat_data: ChatData to generate output files for
    """

    from src.css import get_css_file

    _, css_file = get_css_file()
    chat_data.input_files[css_file.id] = css_file

    # First clear any existing output files
    for chat in chat_data.chats.values():
        chat.output_files.clear()

        # Group messages by year and collect chat dependencies
        message_years: set[int] = set()
        chat_dependencies: dict[int, set[ChatFileID]] = {}

        for msg in chat.messages:
            message_years.add(msg.year)
            if msg.input_file_id.value:
                chat_dependencies[msg.year] = chat_dependencies.get(msg.year, set())
                chat_dependencies[msg.year].add(msg.input_file_id)

        # Create output file for each year with messages
        for year in message_years:
            output_file = OutputFile(year=year)
            output_file.chat_dependencies = chat_dependencies.get(year, set())
            output_file.css_dependency = css_file.id
            chat.output_files[year] = output_file
            chat.output_files[year] = output_file
