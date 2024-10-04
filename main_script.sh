#!/bin/bash

source config.sh

mkdir -p "$INPUT_DIR"
mkdir -p "$OUTPUT_DIR"

source "$PY_ENV"

python3 "$PY_SCRIPT" "$INPUT_DIR"

for zip_file in "$INPUT_DIR"/*.zip; do
	date=$(basename "$zip_file" | grep -oP '\d{8}')

	if ! ls "$OUTPUT_DIR"/*"$date"*Term_Structures.xlsx >/dev/null 2>&1; then
		unzip -j "$zip_file" "*Term_Structures.xlsx" -d "$OUTPUT_DIR"

	echo "Extracted Term_Structures file for date $date"
else
	echo "Term_Structures file for date $date already exists, skipping"
fi

done 

echo "Extraction complete"

deactivate
