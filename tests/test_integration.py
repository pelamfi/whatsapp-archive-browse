import pytest
from src.main import main
from tests.utils.output_verification import verify_output_directory
from tests.utils.test_input import setup_test_input_dirs

def test_basic_run(setup_test_input_dirs):
    """
    Test complete HTML generation against reference files using demo chat data.
    If reference files don't exist, they will be created.
    """
    main_args = ['--input', setup_test_input_dirs['input_dir'], 
                '--output', setup_test_input_dirs['output_dir'], 
                '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    verify_output_directory(setup_test_input_dirs['output_dir'], 'basic_test')
