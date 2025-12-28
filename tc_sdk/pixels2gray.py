#!/usr/bin/env python3
"""
Decimal Matrix to Grayscale Image Converter
Converts text file containing decimal pixel values to PNG grayscale image
"""

import numpy as np
from PIL import Image
import argparse
import sys
from pathlib import Path
import re

MAX_HEIGHT = 512    # Change height larger if you want (rely on architecture your FPGA)
MAX_WIDTH = 512     # Change width larger if you want (rely on architecture your FPGA)

class MatrixConverter:
    """Convert decimal matrix text file to grayscale image"""
    
    def __init__(self, input_file, width, height, output_file):
        """
        Initialize converter with file paths and dimensions
        
        Args:
            input_file: Path to input text file with decimal values
            width: Image width in pixels
            height: Image height in pixels
            output_file: Path to output PNG file
        """
        self.input_file = Path(input_file)
        self.width = width
        self.height = height
        self.output_file = Path(output_file)
        
    def validate_input(self):
        """Validate input parameters"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Invalid dimensions: {self.height}x{self.width}")
        
        if self.width > MAX_WIDTH or self.height > MAX_HEIGHT:
            print(f"[WARNING] Large image size: {self.height}x{self.width}", 
                  file=sys.stderr)
    
    def parse_value(self, value_str):
        """
        Parse a single value string, handling leading zeros
        
        Args:
            value_str: String representation of a number
            
        Returns:
            Integer value
            
        Raises:
            ValueError: If value cannot be parsed
        """
        value_str = value_str.strip()
        
        # Remove leading zeros (e.g., "09" -> "9", "00" -> "0")
        # But keep single "0"
        if value_str and value_str != "0":
            value_str = value_str.lstrip('0') or '0'
        
        try:
            return int(value_str)
        except ValueError:
            # Try hex format (0x...)
            if value_str.lower().startswith('0x'):
                return int(value_str, 16)
            raise ValueError(f"Cannot parse value: {value_str}")
    
    def read_matrix(self):
        """
        Read decimal values from text file
        
        Returns:
            numpy array of pixel values
            
        Raises:
            ValueError: If pixel count doesn't match dimensions
        """
        data = []
        
        try:
            with open(self.input_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        # Split by whitespace or comma
                        # Handle multiple separators
                        values = re.split(r'[,\s]+', line)
                        
                        for val_str in values:
                            if val_str:  # Skip empty strings
                                value = self.parse_value(val_str)
                                data.append(value)
                                
                    except ValueError as e:
                        print(f"[WARNING] Skipping invalid value at line {line_num}: {e}",
                              file=sys.stderr)
                        continue
        
        except IOError as e:
            raise IOError(f"Failed to read input file: {e}") from e
        
        expected = self.width * self.height
        if len(data) != expected:
            raise ValueError(
                f"Pixel count mismatch:\n"
                f"  Expected: {expected} ({self.width}x{self.height})\n"
                f"  Got:      {len(data)} pixels"
            )
        
        return np.array(data, dtype=np.int32)
    
    def process_pixels(self, data):
        """
        Process and validate pixel values
        
        Args:
            data: numpy array of raw pixel values
            
        Returns:
            numpy array of uint8 pixel values (0-255)
        """
        # Check for out-of-range values
        min_val, max_val = data.min(), data.max()
        
        if min_val < 0 or max_val > 255:
            print(f"[WARNING] Values out of range [0, 255]:", file=sys.stderr)
            print(f"          Min: {min_val}, Max: {max_val}", file=sys.stderr)
            print(f"          Clamping to valid range...", file=sys.stderr)
            data = np.clip(data, 0, 255)
        
        return data.astype(np.uint8)
    
    def create_image(self, pixels):
        """
        Create PIL Image from pixel array
        
        Args:
            pixels: 1D numpy array of pixel values
            
        Returns:
            PIL Image object
        """
        img_array = pixels.reshape((self.height, self.width))
        return Image.fromarray(img_array, mode="L")
    
    def save_image(self, img):
        """
        Save image to output file
        
        Args:
            img: PIL Image object
        """
        try:
            # Create output directory if it doesn't exist
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            img.save(self.output_file)
        except IOError as e:
            raise IOError(f"Failed to save image: {e}") from e
    
    def convert(self):
        """
        Main conversion process
        
        Returns:
            True if successful
        """
        print(f"[INFO] Converting matrix to image...")
        print(f"       Input:  {self.input_file}")
        print(f"       Output: {self.output_file}")
        print(f"       Size:   {self.height}x{self.width}")
        
        # Validation
        self.validate_input()
        
        # Read and process
        data = self.read_matrix()
        pixels = self.process_pixels(data)
        
        # Create and save image
        img = self.create_image(pixels)
        self.save_image(img)
        
        # Success summary
        print("\n" + "="*50)
        print("[OK] Conversion complete!")
        print(f"     Input:  {self.input_file} ({len(data)} values)")
        print(f"     Output: {self.output_file}")
        print(f"     Size:   {self.height}x{self.width} pixels")
        print("="*50)
        
        return True


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert decimal matrix text file to grayscale PNG image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input File Format:
  - Space or comma separated decimal values (0-255)
  - Leading zeros are automatically handled (e.g., 09 -> 9)
  - Hex format supported (e.g., 0xFF)
  - Values arranged in any layout (will be reshaped)
  - Empty lines and lines starting with # are ignored
  
Examples:
  %(prog)s input.txt 64 64 output.png
  %(prog)s matrix.txt 128 128 result.png
  %(prog)s --input out_data.txt --height 32 --width 32 --output gray_out.png
        """
    )
    
    parser.add_argument("input", nargs='?', 
                       help="Input text file with decimal values")
    parser.add_argument("height", nargs='?', type=int,
                       help="Image height in pixels")
    parser.add_argument("width", nargs='?', type=int,
                       help="Image width in pixels")
    parser.add_argument("output", nargs='?',
                       help="Output PNG filename")
    
    # Alternative named arguments
    parser.add_argument("-i", "--input-file", dest="input_alt",
                       help="Input text file (alternative)")
    parser.add_argument("-ht", "--height-alt", type=int, dest="height_alt",
                       help="Image height (alternative)")
    parser.add_argument("-wt", "--width-alt", type=int, dest="width_alt",
                       help="Image width (alternative)")
    parser.add_argument("-o", "--output-file", dest="output_alt",
                       help="Output PNG file (alternative)")
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Determine which arguments to use (positional or named)
    input_file = args.input or args.input_alt
    width = args.width or args.width_alt
    height = args.height or args.height_alt
    output_file = args.output or args.output_alt
    
    # Validate required arguments
    if not all([input_file, width, height, output_file]):
        print("[ERROR] Missing required arguments", file=sys.stderr)
        print("\nUsage:", file=sys.stderr)
        print("  python pixels2gray.py out_data.txt height width gray_out.png",
              file=sys.stderr)
        print("\nOr use: python pixels2gray.py  --help", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create converter and run
        converter = MatrixConverter(input_file, width, height, output_file)
        converter.convert()
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()