#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'

# Array of test case folders
FOLDERS=("mode_CW" "mode_CCW" "mode_H" "mode_R")

echo -e "${GREEN}[<>] STARTING CONVERSION OF PGM FILES TO PNG FILES ..."

for FOLDER in "${FOLDERS[@]}"; do
    echo -e "${BLUE}[+] Converting files in folder: $FOLDER"
    cd $FOLDER || exit 1
    mkdir -p gray_img_out   # Create output directory if it doesn't exist

    # Start conversion
    for PGM_FILE in *.pgm; do
        PNG_FILE="${PGM_FILE%.pgm}.png"
        echo -e "${BLUE}[~] Converting $PGM_FILE to $PNG_FILE"
        
        # Convert PGM to PNG
        python ../pgm2gray.py "$FOLDER/pgm_file/$PGM_FILE" "$FOLDER/gray_img_out/$PNG_FILE"
    done

    cd .. || exit 1
done

# Done conversion
echo -e "${GREEN}[<>] CONVERSION COMPLETE."