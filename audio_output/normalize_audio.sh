#!/bin/bash
# This script recursively finds all WAV files in the current directory
# and processes each one with SoX using gain normalization to -12 dBFS.
# The output file will be saved in the same directory with a "n-" prefix.

find . -type f -iname "*.wav" | while read -r file; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    output="$dir/n-$base"
    echo "Processing: $file -> $output"
    sox "$file" "$output" gain -n -12
done

echo "Normalization complete."
