import pytest
import os
import shutil
import tempfile
from pathlib import Path
from src.main import main
from tests.utils.output_verification import verify_output_directory

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

def test_basic_run(test_dirs):
    """
    Test complete HTML generation against reference files.
    If reference files don't exist, they will be created.
    """
    main_args = ['--input', test_dirs['input_dir'], '--output', test_dirs['output_dir'], '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    verify_output_directory(test_dirs['output_dir'], 'basic_test')
