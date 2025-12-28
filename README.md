# Image Transformation Detector

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com) <!-- Replace with actual build badge if available -->
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

This project is a suite of tools for generating grayscale test images, converting between image formats (e.g., PNG to MEM, PGM to PNG), and detecting common transformations (rotations and mirrors) between two grayscale images. It is designed for testing image processing pipelines, such as those used in FPGA-based image rotators or similar hardware systems.

Key features:

- Generate random, gradient, or constant grayscale images.
- Convert images to memory files (.mem) or PGM hex files.
- Detect transformations like 90° rotations (CW/CCW), 180° rotation, horizontal/vertical mirrors.
- Initialize and manage test cases for different transformation modes.
- Clean up generated files with shell scripts.

## Installation

1. Clone the repository:

```
git clone https://github.com/DgHnG36/Tc-Img-Rot-Script.git
cd Tc-Img-Rot-Script/
```

2. Install Python dependencies:

```
pip install numpy pillow argparse
```

3. Ensure you have Bash for running shell scripts (available on Linux/Mac; use WSL on Windows).

No additional setup is required for the core tools.

## Usage

### 1. Generating Test Images and Memory Files

Use `gray2mem.py` to generate grayscale images and corresponding .mem files.

**Command:**

```
python gray2mem.py --height <height> --width <width> --mode <mode> --name_gray <output_image.png> --name_mem <output_mem.mem>
```

- `--height`: Image height (required).
- `--width`: Image width (required).
- `--mode`: One of `gradient` (or `g`), `random` (or `r`), `constant` (or `c`) (default: `random`).
- `--name_gray`: Output PNG filename (default: `gray.png`).
- `--name_mem`: Output MEM filename (default: `gray.mem`).

**Example:**

```
python gray2mem.py --height 64 --width 64 --mode gradient --name_gray test_gradient.png --name_mem test_gradient.mem
```

### 2. Initializing Test Cases

Use `init_tc.sh` to create test case folders and generate images/memory files for different modes (CW, CCW, H, R).

**Command:**

```
./init_tc.sh
```

This script uses configurable variables:

- `NUM_CASES`: Number of test cases per mode (default: 5).
- `MAXIMUM_SEED`: Max random height/width (default: 128).

It creates folders like `mode_CW/`, `mode_CCW/`, etc., with subfolders for images and files.

### 3. Converting PGM to Grayscale PNG

Use `pgm2gray.py` to convert PGM hex files to PNG.

**Command:**

```
python pgm2gray.py <input_pgm.pgm> <output_png.png>
```

**Example:**

```
python pgm2gray.py input.pgm output.png
```

### 4. Running Batch Conversions

Use `run_convert.sh` to convert all PGM files in test case folders to PNG.

**Command:**

```
./run_convert.sh
```

This processes folders like `mode_CW/`, etc., and outputs to `gray_img_out/` subfolders.

### 5. Detecting Image Transformations

Use `compare_data.py` to compare an original image with a transformed one and detect the transformation.

**Command:**

```
python compare_data.py <original.png> <transformed.png> [options]
```

Options:

- `-t, --threshold`: Similarity threshold (0-1, default: 0.95).
- `-d, --diff`: Save difference map as `difference_map.png`.
- `-v, --verbose`: Show detailed results.
- `--no-color`: Disable colored terminal output.

**Example:**

```
python compare_data.py original.png rotated.png --threshold 0.98 --diff --verbose
```

Supported transformations:

- Identical (no change)
- Rotate Clockwise 90°
- Rotate Counter-Clockwise 90°
- Rotate 180°
- Mirror Horizontal
- Mirror Vertical

### 6. Generating Images for FPGA (Alternative Tools)

- `gray2pixels.py`: Generates images and C header files (.h) for embedded systems.

```
python gray2pixels.py --height 32 --width 32 --mode gradient --name_img gray_in.png --name_h in_data.h
```

- `pixels2gray.py`: Converts decimal pixel matrix text files to PNG.

```
python pixels2gray.py input.txt 64 64 output.png
```

### 7. Cleaning Up Files

Use `clear.sh` to remove generated files.

**Command:**

```
./clear.sh
```

Interactive menu:

- 1: Clear gray images
- 2: Clear memory files
- 3: Clear PGM files
- 4: Clear output images
- 5: Clear all test case folders

There's also a simple `clear.sh` for removing all .png, .h, .txt files in the current directory.

### Commands for Each Test Case Mode

After running `./init_tc.sh`, you can process each mode (e.g., for verification):

1. **Mode CW (Clockwise Rotation)**:

   - Navigate: `cd mode_CW`
   - Compare: `python ../compare_data.py gray_img_in/gray_1.png gray_img_out/gray_1.png`
   - Expected: Rotate Clockwise 90°

2. **Mode CCW (Counter-Clockwise Rotation)**:

   - Navigate: `cd mode_CCW`
   - Compare: `python ../compare_data.py gray_img_in/gray_1.png gray_img_out/gray_1.png`
   - Expected: Rotate Counter-Clockwise 90°

3. **Mode H (Horizontal Mirror)**:

   - Navigate: `cd mode_H`
   - Compare: `python ../compare_data.py gray_img_in/gray_1.png gray_img_out/gray_1.png`
   - Expected: Mirror Horizontal

4. **Mode R (Assuming Vertical Mirror or 180° based on context)**:
   - Navigate: `cd mode_R`
   - Compare: `python ../compare_data.py gray_img_in/gray_1.png gray_img_out/gray_1.png`
   - Expected: Mirror Vertical (or adjust based on your implementation)

Repeat for each test case number (1 to NUM_CASES).

## Project Structure

```
image-transformation-detector/
├── compare_data.py          # Main image comparison script
├── clear.sh                 # Interactive cleanup script
├── gray2mem.py              # Generate grayscale to MEM
├── init_tc.sh               # Initialize test cases
├── run_convert.sh           # Batch PGM to PNG conversion
├── pgm2gray.py              # PGM to PNG converter
├── gray2pixels.py           # Generate images and C headers
├── pixels2gray.py           # Text matrix to PNG
├── README.md                # This documentation
├── mode_CW/                 # Test cases for CW mode (generated)
│   ├── gray_img_in/         # Input images
│   ├── mem_file/            # Memory files
│   ├── pgm_file/            # PGM files
│   └── gray_img_out/        # Output images (after conversion)
├── mode_CCW/                # Similar structure
├── mode_H/                  # Similar structure
└── mode_R/                  # Similar structure
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (Note: If no LICENSE file exists, add one with MIT terms.)
