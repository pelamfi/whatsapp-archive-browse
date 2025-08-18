import os
from pathlib import Path

import pytest

from src.main import main
from tests.utils.output_verification import verify_output_directory
from tests.utils.test_env import TIMESTAMPS, ChatTestEnvironment


def test_basic_run(test_env: ChatTestEnvironment) -> None:
    """
    Test complete HTML generation against reference files using demo chat data.
    If reference files don't exist, they will be created.
    """
    # Set up directories and copy files
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()
    test_env.copy_demo_chat(input_dir, TIMESTAMPS["BASE"])

    # Copy CSS file with fixed timestamp
    test_env.copy_css_to_workspace(TIMESTAMPS["BASE"])

    # Change to test environment directory so CSS is found
    original_cwd = os.getcwd()
    os.chdir(test_env.path)

    try:
        # Run the main function
        main_args = ["--input", str(input_dir), "--output", str(output_dir)]
        main(main_args, timestamp="2025-08-03 14:28:38")

        # Verify output against reference
        verify_output_directory(str(output_dir), "basic_test")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def test_duplicated_chat(test_env: ChatTestEnvironment) -> None:
    """
    Test HTML generation with the same chat backed up in two different locations.
    Should handle duplicates and produce identical output to single chat case.
    """
    # Set up test directories with two copies of the same chat
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()

    # Create first copy in input/chat1
    chat1_dir = input_dir / "chat1"
    test_env.copy_demo_chat(chat1_dir, TIMESTAMPS["BACKUP1"])

    # Create second copy in input/chat2
    chat2_dir = input_dir / "chat2"
    test_env.copy_demo_chat(chat2_dir, TIMESTAMPS["BACKUP2"])

    # Copy CSS file with fixed timestamp
    test_env.copy_css_to_workspace(TIMESTAMPS["BASE"])

    # Change to test environment directory so CSS is found
    original_cwd = os.getcwd()
    os.chdir(test_env.path)

    try:
        # Run the main function
        main_args = ["--input", str(input_dir), "--output", str(output_dir)]
        main(main_args, timestamp="2025-08-03 14:28:38")

        # Verify output against reference - should handle duplicates and produce clean output
        verify_output_directory(str(output_dir), "duplicated_chat_test")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def test_overlapping_chat_history(test_env: ChatTestEnvironment) -> None:
    """
    Test HTML generation with two backups of the same chat with partially overlapping history.
    One backup contains messages from lines 1 and 12-21.
    The other contains messages from lines 1 and 2-13.
    """
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()

    # Create second backup with lines 1 - 13
    backup1_dir = input_dir / "backup1"
    test_env.copy_demo_chat(backup1_dir, TIMESTAMPS["BACKUP1"])
    test_env.pick_chat_lines(backup1_dir, [(1, 13)], TIMESTAMPS["BACKUP1"])

    # Create first backup with lines 1 and 12-21
    backup2_dir = input_dir / "backup2"
    test_env.copy_demo_chat(backup2_dir, TIMESTAMPS["BACKUP2"])
    test_env.pick_chat_lines(backup2_dir, [(1, 2), (12, 21)], TIMESTAMPS["BACKUP2"])

    # Copy CSS file with fixed timestamp
    test_env.copy_css_to_workspace(TIMESTAMPS["BASE"])

    # Change to test environment directory so CSS is found
    original_cwd = os.getcwd()
    os.chdir(test_env.path)

    try:
        # Run the main function
        main_args = ["--input", str(input_dir), "--output", str(output_dir)]
        main(main_args, timestamp="2025-08-03 14:28:38")

        # Verify output against reference
        verify_output_directory(str(output_dir), "overlapping_chat_test")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def test_zip_input(test_env: ChatTestEnvironment) -> None:
    """
    Test HTML generation with input files in a ZIP archive.
    Should work identically to regular directory input.
    """
    # Create staging directory with demo chat
    staging_dir = test_env.create_input_dir("staging")
    test_env.copy_demo_chat(staging_dir, TIMESTAMPS["BASE"])

    # Create input directory for the ZIP file
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()

    # Create ZIP in input directory with fixed timestamp for consistent ChatFileIDs
    test_env.create_zip_archive(staging_dir, input_dir / "chat_backup.zip", timestamp=TIMESTAMPS["BASE"])

    # Copy CSS file with fixed timestamp
    test_env.copy_css_to_workspace(TIMESTAMPS["BASE"])

    # Change to test environment directory so CSS is found
    original_cwd = os.getcwd()
    os.chdir(test_env.path)

    try:
        # Run the main function
        main_args = ["--input", str(input_dir), "--output", str(output_dir)]
        main(main_args, timestamp="2025-08-03 14:28:38")

        # Should produce identical output to basic test
        verify_output_directory(str(output_dir), "zip_test")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def test_invalid_chat_syntax(test_env: ChatTestEnvironment) -> None:
    """
    Test HTML generation with invalid syntax in chat file.
    Should handle errors gracefully and continue processing.
    """
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()

    # Create chat with invalid syntax
    chat_dir = input_dir / "chat"
    test_env.copy_demo_chat(chat_dir, TIMESTAMPS["BASE"])

    invalid_lines = [
        "This line has no timestamp or sender\n",
        "[12.3.2022 klo ] Missing time\n",
        "[Invalid.Date klo 14:17:25] Sender: Message\n",
        "[12.3.2022 klo 14:17:25 Invalid timestamp format\n",
    ]
    test_env.insert_chat_lines(chat_dir, 5, invalid_lines, TIMESTAMPS["BASE"])

    # Copy CSS file with fixed timestamp
    test_env.copy_css_to_workspace(TIMESTAMPS["BASE"])

    # Change to test environment directory so CSS is found
    original_cwd = os.getcwd()
    os.chdir(test_env.path)

    try:
        # Run the main function
        main_args = ["--input", str(input_dir), "--output", str(output_dir)]
        main(main_args, timestamp="2025-08-03 14:28:38")

        # Verify output against reference
        verify_output_directory(str(output_dir), "invalid_chat_test")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


@pytest.mark.dependency(
    depends=[
        "test_basic_run",
        "test_duplicated_chat",
        "test_overlapping_chat_history",
        "test_zip_input",
        "test_invalid_chat_syntax",
    ]
)
def test_all_html_outputs_match() -> None:
    """
    Meta test that verifies all integration tests produce identical HTML output.
    This helps ensure that different input scenarios (duplicates, overlapping messages,
    zip files, etc.) all produce consistent output for files that should be the same.
    """
    # Get the reference output directory
    test_root = Path(__file__).parent
    reference_dir = test_root / "resources" / "reference_output"

    # List of test directories that should have identical "Space Rocket" chat outputs
    # Note: invalid_chat_test is excluded because it tests invalid chat handling
    test_dirs = ["basic_test", "duplicated_chat_test", "overlapping_chat_test", "zip_test"]

    # HTML files to compare across test directories
    html_files_to_compare = [
        "index.html",
        "Space Rocket/index.html",
        "Space Rocket/2022.html",
        "Space Rocket/2024.html",
    ]

    # Use first test directory as reference
    reference_test = test_dirs[0]

    # Compare each HTML file across all test directories
    for html_file in html_files_to_compare:
        reference_html = reference_dir / reference_test / html_file

        if not reference_html.exists():
            continue

        # Read reference content
        with open(reference_html, "r", encoding="utf-8") as f:
            reference_content = f.read().strip()

        # Compare with same file in other test directories
        for test_dir in test_dirs[1:]:
            test_html = reference_dir / test_dir / html_file

            if not test_html.exists():
                continue

            with open(test_html, "r", encoding="utf-8") as f:
                test_content = f.read().strip()

            assert (
                reference_content == test_content
            ), f"HTML file '{html_file}' in {test_dir} differs from {reference_test}"
