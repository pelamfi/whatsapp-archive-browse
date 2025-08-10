"""
CSS resource handling for the WhatsApp archive browser.
"""

import os
from pathlib import Path
from typing import Tuple

from src.chat_data import ChatFile


def get_css_file() -> Tuple[str, ChatFile]:
    """
    Get the CSS content and corresponding ChatFile.
    Uses a fixed timestamp to ensure stability across runs.

    Returns:
        Tuple containing:
        - CSS content as string
        - ChatFile instance with stable metadata
    """
    # Use fixed timestamp for stability
    FIXED_TIMESTAMP = 1620000000.0  # 2021-05-02 15:46:40

    # Get CSS file path relative to workspace root
    css_path = Path("src/resources/browseability-generator.css")

    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create ChatFile with stable timestamp
    css_file = ChatFile(
        path=str(css_path),
        size=os.path.getsize(css_path),
        modification_timestamp=FIXED_TIMESTAMP,
    )

    return content, css_file
