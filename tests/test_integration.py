import unittest
import os
import shutil
import tempfile
from pathlib import Path
from src.main import main

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for input and output
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.test_dir, 'input')
        self.output_dir = os.path.join(self.test_dir, 'output')
        
        # Copy demo-chat into input directory
        demo_chat_path = os.path.join(os.path.dirname(__file__), '..', 'demo-chat')
        if os.path.exists(demo_chat_path):
            shutil.copytree(demo_chat_path, self.input_dir, dirs_exist_ok=True)
        else:
            os.makedirs(self.input_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)

    def test_basic_run(self):
        # At this point only checking that the program runs without errors
        # Later tests will verify output files when HTML generation is implemented
        main_args = ['--input', self.input_dir, '--output', self.output_dir, '--locale', 'FI']
        try:
            main(main_args)
        except Exception as e:
            self.fail(f"Main execution failed: {str(e)}")

        # Verify output directory exists
        self.assertTrue(os.path.exists(self.output_dir))
