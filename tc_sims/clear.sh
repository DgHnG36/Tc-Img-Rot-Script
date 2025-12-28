#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'

# Array of test case folders
FOLDERS=("mode_CW" "mode_CCW" "mode_H" "mode_R")

# Clear all test case folders
clear_all() {                 
    for FOLDER in ${FOLDERS[@]}; do
        echo -e "${RED}[x] Clearing folder $FOLDER${NC}"
        rm -rf $FOLDER
    done
    echo -e "${BLUE}[+] All test case folders cleared.${NC}"
}

# Clear only gray images in each test case folder
clear_img_in() {
    for FOLDER in ${FOLDERS[@]}; do
        echo -e "${RED}[x] Clearing gray images in folder $FOLDER${NC}"
        rm -rf $FOLDER/gray_img
    done
    echo -e "${BLUE}[+] All gray images cleared.${NC}"
}

# Clear only output images in each test case folder
clear_img_out() {
    for FOLDER in ${FOLDERS[@]}; do
        echo -e "${RED}[x] Clearing output images in folder $FOLDER${NC}"
        rm -rf $FOLDER/gray_img_out
    done
    echo -e "${BLUE}[+] All output images cleared.${NC}"
}

# Clear only memory files in each test case folder
clear_mem_file() {
    for FOLDER in ${FOLDERS[@]}; do
        echo -e "${RED}[x] Clearing memory files in folder $FOLDER${NC}"
        rm -rf $FOLDER/mem_file
    done
    echo -e "${BLUE}[+] All memory files cleared.${NC}"
}

# Clear only PGM files in each test case folder
clear_pgm_file() {
    for FOLDER in ${FOLDERS[@]}; do
        echo -e "${RED}[x] Clearing PGM files in folder $FOLDER${NC}"
        rm -rf $FOLDER/pgm_file
    done
    echo -e "${BLUE}[+] All PGM files cleared.${NC}"
}

# Menu select option
echo "Select an option to clear:"
echo -e "$GREEN[1] Clear only gray images"
echo -e "$GREEN[2] Clear only memory images"
echo -e "$GREEN[3] Clear only PGM files"
echo -e "$GREEN[4] Clear only output images"
echo -e "$GREEN[5] Clear all test case folders"
read -p "Enter your choice (1-5): " choice

case $choice in
    1) clear_img_in ;;
    2) clear_mem_file ;;
    3) clear_pgm_file ;;
    4) clear_img_out ;;
    5) clear_all ;;
    *) echo -e "${RED}Invalid choice. Exiting." ;;
esac
