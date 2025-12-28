#!/bin/bash

# Your choices here
NUM_CASES=5                                     # Change number of test cases here
MAXIMUM_SEED=128                                # Change maximum seed (height/width range) here 

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
FOLDERS=("mode_CW" "mode_CCW" "mode_H" "mode_R")

# Function to generate random number between 1 and MAXIMUM_SEED
rand1_to_seed() {
    echo $(( RANDOM % $MAXIMUM_SEED + 1 ))
}

# Array of test case modes
MODES=("mode_CW" "mode_CCW" "mode_H" "mode_R")

echo -e "${GREEN}[<>] STARTING TEST CASE GENERATION ..."

for FOLDER in ${FOLDERS[@]}; do
    echo -e "${BLUE}[+] Creating test case in $FOLDER ..."
    mkdir -p $FOLDER
    mkdir -p $FOLDER/gray_img_in
    mkdir -p $FOLDER/mem_file
    mkdir -p $FOLDER/pgm_file

    for (( i=1; i<=$NUM_CASES; i++ )); do
        echo -e "${BLUE}[~] Creating test case $i"

        # Generate random height and width between 1 and MAXIMUM_SEED
        h_rand=$(rand1_to_seed)
        w_rand=$(rand1_to_seed)

        # Generate gray image and save to memory file
        python3 gray2mem.py --height $h_rand \
                            --width $w_rand \
                            --mode gradient \
                            --name_gray "$FOLDER/gray_img_in/gray_$i.png" \
                            --name_mem  "$FOLDER/mem_file/mem_$i.mem"
    done
done

# Done init test cases
echo -e "${GREEN}[<>] TEST CASE GENERATION COMPLETE."