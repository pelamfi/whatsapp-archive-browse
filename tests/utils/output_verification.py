"""Utilities for testing the WhatsApp archive browser."""

import os
import shutil
import pytest

def get_reference_dir(name: str) -> str:
    """Get the path to a reference directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'reference_output', name)

def compare_or_update_reference(output_path: str, reference_path: str):
    """
    Compare output file with reference, or create/update reference if it doesn't exist.
    """
    # Create reference directory if it doesn't exist
    os.makedirs(os.path.dirname(reference_path), exist_ok=True)

    if not os.path.exists(reference_path):
        # Reference doesn't exist - create it
        shutil.copy2(output_path, reference_path)
        pytest.fail(
            f"Reference file {reference_path} did not exist and has been created.\n"
            f"Please verify its contents and re-run the test."
        )
    
    # Compare files
    with open(output_path, 'r', encoding='utf-8') as f1, \
         open(reference_path, 'r', encoding='utf-8') as f2:
        assert f1.read().strip() == f2.read().strip(), \
            f"Output file {output_path} differs from reference {reference_path}"

def verify_output_directory(output_dir: str, reference_subdir: str):
    """
    Compare the output directory with a reference subdirectory.
    Structure based on README.md:
    - Top level folder:
        - index.html (compared)
        - browseability-generator.css (presence checked)
        - browseability-generator-chat-data.json (compared)
        - Chat Name/
            - index.html (compared)
            - browseability-generator.css (presence checked)
            - YYYY.html (compared)
            - media/ (presence checked)
    """
    reference_dir = get_reference_dir(reference_subdir)

    # Compare top-level files
    compare_or_update_reference(
        os.path.join(output_dir, 'browseability-generator-chat-data.json'),
        os.path.join(reference_dir, 'browseability-generator-chat-data.json')
    )
    
    compare_or_update_reference(
        os.path.join(output_dir, 'index.html'),
        os.path.join(reference_dir, 'index.html')
    )

    # Check CSS presence
    assert os.path.exists(os.path.join(output_dir, 'browseability-generator.css')), \
        "CSS file missing from output root"

    # Compare all chat directories
    for chat_dir in os.listdir(reference_dir):
        if not os.path.isdir(os.path.join(reference_dir, chat_dir)):
            continue

        output_chat_dir = os.path.join(output_dir, chat_dir)
        reference_chat_dir = os.path.join(reference_dir, chat_dir)

        # Compare chat index
        compare_or_update_reference(
            os.path.join(output_chat_dir, 'index.html'),
            os.path.join(reference_chat_dir, 'index.html')
        )

        # Check chat CSS and media directory presence
        assert os.path.exists(os.path.join(output_chat_dir, 'browseability-generator.css')), \
            f"CSS file missing from chat directory {chat_dir}"
        assert os.path.exists(os.path.join(output_chat_dir, 'media')), \
            f"Media directory missing from chat directory {chat_dir}"

        # Compare all year files
        for year_file in os.listdir(reference_chat_dir):
            if not year_file.endswith('.html') or year_file == 'index.html':
                continue

            compare_or_update_reference(
                os.path.join(output_chat_dir, year_file),
                os.path.join(reference_chat_dir, year_file)
            )
