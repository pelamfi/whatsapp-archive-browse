import pytest
from src.main import main
from tests.utils.output_verification import verify_output_directory
from tests.utils.test_env import test_env, TIMESTAMPS

def test_basic_run(test_env):
    """
    Test complete HTML generation against reference files using demo chat data.
    If reference files don't exist, they will be created.
    """
    # Set up test directories and copy demo data
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()
    test_env.copy_demo_chat(input_dir, TIMESTAMPS["BASE"])
    
    # Run the main function
    main_args = ['--input', str(input_dir), 
                '--output', str(output_dir), 
                '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    # Verify output against reference
    verify_output_directory(str(output_dir), 'basic_test')

def test_duplicated_chat(test_env):
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
    
    # Run the main function
    main_args = ['--input', str(input_dir), 
                '--output', str(output_dir), 
                '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    # Verify output against reference - should handle duplicates and produce clean output
    verify_output_directory(str(output_dir), 'duplicated_chat_test')

def test_overlapping_chat_history(test_env):
    """
    Test HTML generation with two backups of the same chat with partially overlapping history.
    One backup contains messages from lines 1 and 12-21.
    The other contains messages from lines 1 and 2-13.
    """
    input_dir = test_env.create_input_dir()
    output_dir = test_env.create_output_dir()
    
    # Create first backup with lines 1 - 2 and 12-21
    backup1_dir = input_dir / "backup1"
    test_env.copy_demo_chat(backup1_dir, TIMESTAMPS["BACKUP1"])
    test_env.filter_chat_lines(backup1_dir, 12, 21, TIMESTAMPS["BACKUP1"])
    
    # Create second backup with lines 1 - 2 and 3-13
    backup2_dir = input_dir / "backup2"
    test_env.copy_demo_chat(backup2_dir, TIMESTAMPS["BACKUP2"])
    test_env.filter_chat_lines(backup2_dir, 3, 13, TIMESTAMPS["BACKUP2"])
    
    # Run the main function
    main_args = ['--input', str(input_dir), 
                '--output', str(output_dir), 
                '--locale', 'FI']
    main(main_args, timestamp="2025-08-03 14:28:38")
    
    # Verify output against reference
    verify_output_directory(str(output_dir), 'overlapping_chat_test')
