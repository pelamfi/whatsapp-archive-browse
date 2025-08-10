import shutil
from pathlib import Path

from tests.utils.test_env import ChatTestEnvironment


def copy_css_to_workspace(test_env: ChatTestEnvironment, timestamp: float) -> None:
    """
    Copy the CSS file to src/resources in the test environment
    with a fixed timestamp.

    Args:
        timestamp: Unix timestamp to set for the CSS file
    """
    # Create src/resources in test environment
    resources_dir = test_env.base_dir / "src" / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Get source CSS file path
    source_css = Path(__file__).parent.parent.parent / "src" / "resources" / "browseability-generator.css"

    if not source_css.exists():
        raise FileNotFoundError(f"CSS file not found at {source_css}")

    # Copy to test environment
    dest_css = resources_dir / "browseability-generator.css"
    shutil.copy2(str(source_css), str(dest_css))

    # Set fixed timestamp
    test_env.set_file_timestamps(dest_css, timestamp)
