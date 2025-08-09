#!/usr/bin/env bash

# Exit on error. Append "|| true" if you expect an error.
set -e

# Exit on error in any nested command
set -o pipefail

# Exit on unset variable
set -u

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Set initial flags
refresh_test_resources=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --refresh-test-resources)
            refresh_test_resources=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Create build directory if it doesn't exist
BUILD_DIR="build"
mkdir -p "$BUILD_DIR"

# Ensure virtual environment exists and is activated
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment (works even if already activated)
source .venv/bin/activate

# Set Python path to use virtualenv version
PYTHON=".venv/bin/python"

# Install dependencies if needed
$PYTHON -m pip install -q -e ".[dev]"

# Function to run a command silently but show output on error
run_quietly() {
    local name=$1
    shift
    echo "Running $name..."
    local output
    output=$("$@" 2>&1) || {
        echo "❌ $name failed:"
        echo "$output"
        return 1
    }
    echo "✓ $name passed"
}

# Black formatting
run_quietly "black code formatter" $PYTHON -m black --check src tests || {
    echo "Running black to fix formatting..."
    $PYTHON -m black src tests
}

# Import sorting
run_quietly "isort import sorter" $PYTHON -m isort --check-only src tests || {
    echo "Running isort to fix imports..."
    $PYTHON -m isort src tests
}

# Type checking
run_quietly "mypy type checker" $PYTHON -m mypy src tests

# Run tests first without coverage to get fast feedback
echo "Running pytest test suite..."

if [ "$refresh_test_resources" = true ]; then
    echo "Refreshing test reference files. Removing existing resources..."
    rm -rf tests/resources/*
    # First run will generate reference files - capture output to detect creation warnings
    test_output=$($PYTHON -m pytest 2>&1) || true
    if echo "$test_output" | grep -q "Reference file created:"; then
        echo "✓ Reference files created"
    else 
        echo "❌ No reference files created. Check test setup."
    fi
fi

# Normal test run - fail on any error
if ! test_output=$($PYTHON -m pytest 2>&1); then
    echo "❌ Tests failed:"
    echo "$test_output"
    echo "$test_output" > "$BUILD_DIR"/test_output.txt
    exit 1
fi

echo "✓ All tests passed"
echo "$test_output" > "$BUILD_DIR"/test_output.txt

# Only run coverage if tests pass
echo "Generating coverage report..."
if ! $PYTHON -m pytest --quiet --cov=src --cov-report=html:"$BUILD_DIR"/coverage --cov-report=term-missing > "$BUILD_DIR"/coverage_output.txt; then
    echo "❌ Coverage measurement failed"
    exit 1
fi
echo "✓ Coverage report generated in build/coverage/"

# Linting
run_quietly "flake8 linter" $PYTHON -m flake8 src tests
