#!/bin/bash

# Exit on any error
set -e

# Function to replace content while preserving file timestamps
replace_content() {
    local src=$1
    local dst=$2
    local tmp="${dst}.tmp"
    
    # Get original timestamps
    local atime=$(stat -c %X "$dst")
    local mtime=$(stat -c %Y "$dst")
    
    # Replace content
    cp "$src" "$tmp"
    mv "$tmp" "$dst"
    
    # Restore timestamps
    touch -a -d @"$atime" "$dst"
    touch -m -d @"$mtime" "$dst"
}

# Source files to migrate
FILES=(
    "src/chat_data.py"
    "src/data_comparator.py"
    "src/html_generator.py"
    "src/input_scanner.py"
    "src/main.py"
    "src/metadata_updater.py"
    "src/output_checker.py"
    "src/parser.py"
    "tests/test_chat_data.py"
    "tests/test_data_comparator.py"
    "tests/test_html_generator.py"
    "tests/test_input_scanner.py"
    "tests/test_metadata_updater.py"
    "tests/test_parser.py"
)

# Backup original files
echo "Creating backup directory..."
BACKUP_DIR="backup_pre_2_suffix_$(date +%Y%m%d_%H%M%S)"
mkdir "$BACKUP_DIR"
for file in "${FILES[@]}"; do
    mkdir -p "$BACKUP_DIR/$(dirname "$file")"
    cp "$file" "$BACKUP_DIR/$file"
done

# Replace files
echo "Replacing files..."
for file in "${FILES[@]}"; do
    suffix2_file="${file%.*}2.py"
    if [ -f "$suffix2_file" ]; then
        echo "Migrating $suffix2_file to $file"
        # Preserve timestamps when replacing
        replace_content "$suffix2_file" "$file"
        # Remove the suffix2 file
        rm "$suffix2_file"
    else
        echo "Warning: $suffix2_file not found"
    fi
done

echo "Migration complete. Original files backed up in $BACKUP_DIR/"
echo "You can now use 'git diff' to review the changes."
