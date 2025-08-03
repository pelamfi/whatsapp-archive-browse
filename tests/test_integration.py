import pytest
import os
import shutil
import tempfile
from pathlib import Path
from src.main import main

@pytest.fixture
def test_dirs():
    # Create temporary directories for input and output
    test_dir = tempfile.mkdtemp()
    input_dir = os.path.join(test_dir, 'input')
    output_dir = os.path.join(test_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy demo-chat into input directory
    demo_chat_path = os.path.join(os.path.dirname(__file__), '..', 'demo-chat')
    if os.path.exists(demo_chat_path):
        shutil.copytree(demo_chat_path, input_dir, dirs_exist_ok=True)
    else:
        os.makedirs(input_dir)

    # Return the directories for test use
    yield {"test_dir": test_dir, "input_dir": input_dir, "output_dir": output_dir}
    
    # Clean up after test
    shutil.rmtree(test_dir)

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

def test_basic_run(test_dirs):
    """
    Test complete HTML generation against reference files.
    If reference files don't exist, they will be created.
    """
    main_args = ['--input', test_dirs['input_dir'], '--output', test_dirs['output_dir'], '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    # Get reference directory path
    ref_dir = os.path.join(os.path.dirname(__file__), 'resources', 'reference_output')
    
    # Compare main metadata file
    compare_or_update_reference(
        os.path.join(test_dirs['output_dir'], 'browseability-generator-chat-data.json'),
        os.path.join(ref_dir, 'browseability-generator-chat-data.json')
    )
    
    # Compare main index
    compare_or_update_reference(
        os.path.join(test_dirs['output_dir'], 'index.html'),
        os.path.join(ref_dir, 'index.html')
    )

    # Compare all chat directories
    for chat_dir in os.listdir(test_dirs['output_dir']):
        if not os.path.isdir(os.path.join(test_dirs['output_dir'], chat_dir)):
            continue

        # Compare chat index
        compare_or_update_reference(
            os.path.join(test_dirs['output_dir'], chat_dir, 'index.html'),
            os.path.join(ref_dir, chat_dir, 'index.html')
        )

        # Compare all year files
        for year_file in os.listdir(os.path.join(test_dirs['output_dir'], chat_dir)):
            if not year_file.endswith('.html') or year_file == 'index.html':
                continue

            compare_or_update_reference(
                os.path.join(test_dirs['output_dir'], chat_dir, year_file),
                os.path.join(ref_dir, chat_dir, year_file)
            )
