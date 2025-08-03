"""Utilities for testing the WhatsApp archive browser."""

import os
import shutil
import pytest

def get_reference_dir(name: str) -> str:
    """Get the path to a reference directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'reference_output', name)

import warnings

def compare_or_update_reference(output_path: str, reference_path: str) -> bool:
    """
    Compare output file with reference, or create/update reference if it doesn't exist.
    Returns True if comparison was made, False if reference was created.
    """
    # Create reference directory if it doesn't exist
    os.makedirs(os.path.dirname(reference_path), exist_ok=True)

    if not os.path.exists(reference_path):
        # Reference doesn't exist - create it
        shutil.copy2(output_path, reference_path)
        warnings.warn(
            f"\nReference file created: {reference_path}\n"
            f"Please verify its contents before committing.",
            RuntimeWarning
        )
        return False
    
    # Compare files
    with open(output_path, 'r', encoding='utf-8') as f1, \
         open(reference_path, 'r', encoding='utf-8') as f2:
        assert f1.read().strip() == f2.read().strip(), \
            f"Output file {output_path} differs from reference {reference_path}"
    return True

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
    files_compared = []
    files_created = []

    def safe_compare(output_path: str, reference_path: str):
        """Helper to track which files were compared vs created"""
        if compare_or_update_reference(output_path, reference_path):
            files_compared.append(os.path.relpath(reference_path, reference_dir))
        else:
            files_created.append(os.path.relpath(reference_path, reference_dir))

    # Compare top-level files
    safe_compare(
        os.path.join(output_dir, 'browseability-generator-chat-data.json'),
        os.path.join(reference_dir, 'browseability-generator-chat-data.json')
    )
    
    safe_compare(
        os.path.join(output_dir, 'index.html'),
        os.path.join(reference_dir, 'index.html')
    )

    # Process all chat directories in output
    for chat_dir in os.listdir(output_dir):
        if not os.path.isdir(os.path.join(output_dir, chat_dir)) or chat_dir == 'media':
            continue

        output_chat_dir = os.path.join(output_dir, chat_dir)
        reference_chat_dir = os.path.join(reference_dir, chat_dir)

        # Compare chat index
        safe_compare(
            os.path.join(output_chat_dir, 'index.html'),
            os.path.join(reference_chat_dir, 'index.html')
        )

        # Compare all year files
        for year_file in os.listdir(output_chat_dir):
            if not year_file.endswith('.html') or year_file == 'index.html':
                continue

            safe_compare(
                os.path.join(output_chat_dir, year_file),
                os.path.join(reference_chat_dir, year_file)
            )

    # Report reference file status
    if files_created:
        warnings.warn(
            f"\nReference files created in {reference_subdir}:\n"
            f"  " + "\n  ".join(files_created) + "\n"
            f"Please verify the contents of these files before committing.",
            RuntimeWarning
        )
    if files_compared:
        print(f"Verified {len(files_compared)} reference files in {reference_subdir}")

    # Now verify structure matches
    # Check CSS presence
    assert os.path.exists(os.path.join(output_dir, 'browseability-generator.css')), \
        "CSS file missing from output root"

    # Verify final structure
    output_chat_dirs = {d for d in os.listdir(output_dir) 
                       if os.path.isdir(os.path.join(output_dir, d)) and d != 'media'}
    reference_chat_dirs = {d for d in os.listdir(reference_dir) 
                          if os.path.isdir(os.path.join(reference_dir, d)) and d != 'media'}
    
    # Verify output has exactly the same chat directories as reference
    assert output_chat_dirs == reference_chat_dirs, \
        f"Chat directories don't match. Output has {output_chat_dirs}, reference has {reference_chat_dirs}"

    # Check CSS and media for each chat directory
    for chat_dir in output_chat_dirs:

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
