#!/usr/bin/env bash

# Exit on error. Append "|| true" if you expect an error.
set -e

# Exit on error in any nested command
set -o pipefail

# Exit on unset variable
set -u

# Set Python path to use local version
PYTHON="python3"

# Ensure we're in the project root directory
cd "$(dirname "$0")"

echo "==> Checking code format with black..."
$PYTHON -m black --check src tests || {
    echo "Code format check failed. Running black to fix..."
    $PYTHON -m black src tests
}

echo "==> Sorting imports with isort..."
$PYTHON -m isort --check-only src tests || {
    echo "Import sort check failed. Running isort to fix..."
    $PYTHON -m isort src tests
}

echo "==> Running mypy type checker..."
$PYTHON -m mypy src tests

echo "==> Running tests with coverage..."
$PYTHON -m pytest --cov=src --cov-report=term-missing

echo "==> Running flake8 linter..."
$PYTHON -m flake8 src tests

echo "==> All checks passed! 🎉"
