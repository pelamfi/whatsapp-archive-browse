import os
from typing import Optional
from .chat_data import ChatData

def check_output_directory(output_dir: str) -> Optional[ChatData]:
    """
    Check if browseability-generator-chat-data.json exists in output directory
    and load it if found.
    
    Args:
        output_dir: Directory to check for existing chat data
        
    Returns:
        ChatData if json file exists and can be parsed, None otherwise
    """
    json_path = os.path.join(output_dir, "browseability-generator-chat-data.json")
    
    if not os.path.exists(json_path):
        return None
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return ChatData.from_json(f.read())
    except Exception as e:
        # Log error but continue - this allows regenerating from input if output is corrupted
        print(f"Error reading {json_path}: {e}")
        return None
