#!/bin/bash

# Exit on any error
set -e

# Fix imports in all Python files
echo "Fixing imports..."
find src tests -name "*.py" -type f -exec sed -i \
    -e 's/from src\.\([^ ]*\)2 import/from src.\1 import/g' \
    -e 's/import src\.\([^ ]*\)2/import src.\1/g' \
    -e 's/\([A-Za-z][A-Za-z0-9_]*\)2/\1/g' {} +

echo "Import fixes complete. Please review with git diff."
