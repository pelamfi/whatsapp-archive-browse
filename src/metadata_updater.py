"""
This module handles updating metadata JSON files in the output directory.
The update process is designed to be safe against interruptions by:
1. Writing new data to a separate file
2. Making backup of existing data
3. Only then replacing the main file
"""

import os
from src.chat_data import ChatData

def update_metadata(chat_data: ChatData, output_dir: str) -> None:
    """
    Safely update the metadata JSON in the output directory.
    
    The update process:
    1. Write new data to browseability-generator-chat-data-NEW.json
    2. If main JSON exists, rename it to BACKUP
    3. Rename NEW to be the main JSON
    """
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare paths
    main_json = os.path.join(output_dir, 'browseability-generator-chat-data.json')
    new_json = os.path.join(output_dir, 'browseability-generator-chat-data-NEW.json')
    backup_json = os.path.join(output_dir, 'browseability-generator-chat-data-BACKUP.json')
    
    # Write new data
    with open(new_json, 'w', encoding='utf-8') as f:
        f.write(chat_data.to_json())
    
    # If main exists, make backup (remove old backup first)
    if os.path.exists(main_json):
        if os.path.exists(backup_json):
            os.remove(backup_json)
        os.rename(main_json, backup_json)
    
    # Move new file to main
    os.rename(new_json, main_json)
    print("Updating metadata")
    # No-op implementation
    return None
