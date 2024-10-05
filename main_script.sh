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

mkdir -p "$RAW_EXCELS_FOLDER"

if [ -z "$(ls -A "$OUTPUT_DIR"/*.xlsx 2>/dev/null)" ]; then
    echo "No .xlsx files found in $OUTPUT_DIR"
fi

for excel in "$OUTPUT_DIR"/*.xlsx; do
    echo "Processing file $excel"
    date=$(basename "$excel" | grep -oP '\d{8}')
    
    if [ -z "$date" ]; then
        echo "Could not extract date from filename $excel, skipping"
        continue
    fi

    if ! ls "$RAW_EXCELS_FOLDER"/*"$date"*.xlsx >/dev/null 2>&1; then
        echo "Running processing script on $excel"
        python3 "$PROCESSING_SCRIPT" "$excel" "$RAW_EXCELS_FOLDER"
        output=$(python3 "$PROCESSING_SCRIPT" "$excel" "$RAW_EXCELS_FOLDER" 2>&1)
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            echo "Error occurred while processing $excel"
            echo "Python script output:"
            echo "$output"
        fi
    else
        echo "Raw file for $date already in folder, skipping"
    fi
done

echo "Processing complete"

for file in "$RAW_EXCELS_FOLDER"/*.XLSX; do
    # Check if files with .abc extension exist
    if [ -e "$file" ]; then
        # Get the filename without the extension
        filename="${file%.XLSX}"
        # Rename the file with the new extension
        mv "$file" "${filename}.xlsx"
        echo "Renamed $file to ${filename}.xlsx"
    else
        echo "No files with .XLSX extension found in the directory"
        echo "No renaming of extensions needed"
    fi
done

for file in "$RAW_EXCELS_FOLDER"/*.xlsx; do

    date=$(basename "$file" | grep -oP '\d{8}')
    if [ -z "$date" ]; then
            echo "Could not extract date from filename $file, skipping"
            continue
        fi
    if ! ls "$FORMATTED_FILES_FOLDER"/*"$date"*.xlsx >/dev/null 2>&1; then    

        if [ -e "$file" ]; then
            echo "Running formatting script on $file"
            python3 "$FORMATTING_SCRIPT" "$file" "$FORMATTED_FILES_FOLDER"
            output=$(python3 "$FORMATTING_SCRIPT" "$file" "$FORMATTED_FILES_FOLDER" 2>&1)
            exit_code=$?
            
            if [ $exit_code -ne 0 ]; then
                echo "Error occurred while formatting $file"
                echo "Python script output:"
                echo "$output"
            fi
        fi
    else 
        echo "Formatted file for $date already in folder, skipping"
    fi
done

for file in "$FORMATTED_FILES_FOLDER"/*.xlsx; do
    if [ -e "$file" ]; then
        echo "Uploading $file on table $TABLE_NAME"
        python3 "$UPLOADING_SCRIPT" "$file" "$TABLE_NAME"
        output=$(python3 "$UPLOADING_SCRIPT" "$file" "$TABLE_NAME" 2>&1)
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            echo "Error occurred while uploading $file"
            echo "Python script output:"
            echo "$output"
            else
            echo "Successfully loaded file"
        fi
    fi
done

deactivate