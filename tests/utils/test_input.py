"""Utilities for test input data setup."""

import os
import shutil
import tempfile
import pytest
from typing import Dict, Optional

@pytest.fixture
def setup_test_input_dirs(request):
    """
    Create test input and output directories with optional test-specific input data.
    
    Usage:
        @pytest.mark.test_input("custom_test_data")  # Optional, defaults to demo-chat
        def test_something(setup_test_input_dirs):
            input_dir = setup_test_input_dirs["input_dir"]
            output_dir = setup_test_input_dirs["output_dir"]
    """
    # Create temporary directories for input and output
    test_dir = tempfile.mkdtemp()
    input_dir = os.path.join(test_dir, 'input')
    output_dir = os.path.join(test_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if test has custom input data
    marker = request.node.get_closest_marker("test_input")
    input_name = marker.args[0] if marker else "demo-chat"
    
    # Copy input data into input directory
    input_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'test_input', input_name)
    if not os.path.exists(input_data_path):
        input_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', input_name)
    
    if os.path.exists(input_data_path):
        shutil.copytree(input_data_path, input_dir, dirs_exist_ok=True)
    else:
        os.makedirs(input_dir)

    # Return the directories for test use
    dirs = {"test_dir": test_dir, "input_dir": input_dir, "output_dir": output_dir}
    yield dirs
    
    # Clean up after test
    shutil.rmtree(test_dir)
