import pytest
from src.main import main
from tests.utils.output_verification import verify_output_directory
from tests.utils.test_env import test_env

def test_basic_run(test_env):
    """
    Test complete HTML generation against reference files using demo chat data.
    If reference files don't exist, they will be created.
    """
    # Set up test directories and copy demo data
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()
    test_env.copy_demo_chat(input_dir)
    
    # Run the main function
    main_args = ['--input', str(input_dir), 
                '--output', str(output_dir), 
                '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    # Verify output against reference
    verify_output_directory(str(output_dir), 'basic_test')
