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

def test_basic_run(test_dirs):
    """Test that the program runs without errors"""
    # At this point only checking that the program runs without errors
    # Later tests will verify output files when HTML generation is implemented
    main_args = ['--input', test_dirs['input_dir'], '--output', test_dirs['output_dir'], '--locale', 'FI']
    
    main(main_args)  # If this raises an exception, pytest will fail the test
    
    # Verify output directory exists
    assert os.path.exists(test_dirs['output_dir'])
