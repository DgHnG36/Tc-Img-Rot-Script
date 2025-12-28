#!/usr/bin/env python3
"""
Image Data Generator for FPGA Image Rotator
Generates test images and C header files for embedded systems
"""

import numpy as np
from PIL import Image
import argparse
import random
import sys

MAX_HEIGHT = 512    # Change height larger if you want (rely on architecture your FPGA)
MAX_WIDTH = 512     # Change width larger if you want (rely on architecture your FPGA)



class ImageGenerator:
    """Generate test images with different patterns"""
    
    @staticmethod
    def random(width, height):
        """Generate random noise image"""
        return np.random.randint(0, 256, (height, width), dtype=np.uint8)
    
    @staticmethod
    def gradient(width, height):
        """Generate horizontal gradient image"""
        return np.tile(
            np.linspace(0, 255, width, dtype=np.uint8),
            (height, 1)
        )
    
    @staticmethod
    def constant(width, height, value=MAX_HEIGHT):
        """Generate constant value image"""
        return np.full((height, width), value, dtype=np.uint8)


class CHeaderWriter:
    """Write image data to C header file format"""
    
    @staticmethod
    def write(filename, img):
        """
        Write image data as C header file with Little Endian format
        
        Args:
            filename: Output .h file path
            img: numpy array (height, width) with uint8 values
        """
        height, width = img.shape
        
        try:
            with open(filename, "w") as f:
                # Header guard and includes
                f.write("#ifndef IN_DATA_H\n")
                f.write("#define IN_DATA_H\n\n")
                f.write("#include <stdint.h>\n\n")
                f.write("typedef uint8_t u8;\n\n")
                
                # Array declaration
                f.write("// Image data with header (Little Endian format)\n")
                f.write("// Structure: [Height 4B][Width 4B][Pixel Data]\n")
                f.write("u8 raw_image_file[] __attribute__ ((aligned (32))) = {\n")
                
                # Write header (8 bytes total)
                f.write("    // --- HEADER (8 Bytes) ---\n")
                f.write(f"    // Height = {height}\n")
                CHeaderWriter._write_u32_le(f, height)
                f.write(f"    // Width = {width}\n")
                CHeaderWriter._write_u32_le(f, width)
                f.write("\n")
                
                # Write pixel data
                f.write("    // --- PIXEL DATA ---\n")
                for y in range(height):
                    f.write("    ")
                    for x in range(width):
                        f.write(f"0x{img[y, x]:02X}")
                        if y < height - 1 or x < width - 1:
                            f.write(", ")
                        if (x + 1) % 16 == 0 and x < width - 1:
                            f.write("\n    ")
                    f.write("\n")
                
                # Close array and header guard
                f.write("};\n\n")
                f.write("#endif // IN_DATA_H\n")
                
        except IOError as e:
            print(f"[ERROR] Failed to write header file: {e}", file=sys.stderr)
            sys.exit(1)
    
    @staticmethod
    def _write_u32_le(f, value):
        """Write 32-bit unsigned integer in Little Endian format"""
        f.write(f"    0x{value & 0xFF:02X}, 0x{(value >> 8) & 0xFF:02X}, "
                f"0x{(value >> 16) & 0xFF:02X}, 0x{(value >> 24) & 0xFF:02X},\n")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate test images and C header files for FPGA image rotator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --width 64 --height 64 --mode gradient
  %(prog)s --random_size --mode random
  %(prog)s --width 128 --height 128 --mode checkerboard --out_img test.png
        """
    )
    
    # Size arguments
    size_group = parser.add_argument_group('Image Size')
    size_group.add_argument("--height", type=int, default=32,
                           help="Image height (default: 32, max: 512)")
    size_group.add_argument("--width", type=int, default=32,
                           help="Image width (default: 32, max: 512)")
    size_group.add_argument("--random_size", action="store_true",
                           help="Generate random size between 1-512")
    
    # Pattern arguments
    pattern_group = parser.add_argument_group('Image Pattern')
    pattern_group.add_argument("--mode", 
                              choices=["random", "gradient", "constant"],
                              default="random",
                              help="Image generation mode (default: random)")
    
    # Output arguments
    output_group = parser.add_argument_group('Output Files')
    output_group.add_argument("--name_img", default="gray_in.png",
                             help="Output image filename (default: gray_in.png)")
    output_group.add_argument("--name_h", default="in_data.h",
                             help="Output header filename (default: in_data.h)")
    
    return parser.parse_args()


def validate_size(width, height):
    """Validate image dimensions"""
    if width < 1 or width > MAX_WIDTH:
        print(f"[ERROR] Width must be between 1 and {MAX_WIDTH}, got {width}", file=sys.stderr)
        sys.exit(1)
    if height < 1 or height > MAX_HEIGHT:
        print(f"[ERROR] Height must be between 1 and {MAX_HEIGHT}, got {height}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Determine image size
    if args.random_size:
        width = random.randint(1, MAX_WIDTH)
        height = random.randint(1, MAX_HEIGHT)
        print(f"[INFO] Random size generated: {height}x{width}")
    else:
        width = args.width
        height = args.height
    
    validate_size(width, height)
    
    # Generate image
    generator = ImageGenerator()
    mode_map = {
        "random": generator.random,
        "gradient": generator.gradient,
        "constant": generator.constant,
    }
    
    print(f"[INFO] Generating {args.mode} image...")
    img = mode_map[args.mode](width, height)
    
    # Save image file
    try:
        Image.fromarray(img, mode="L").save(args.name_img)
        print(f"[OK] Image saved: {args.name_img}")
    except Exception as e:
        print(f"[ERROR] Failed to save image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write header file
    print(f"[INFO] Writing C header file...")
    CHeaderWriter.write(args.name_h, img)
    print(f"[OK] Header saved: {args.name_h}")

    # Summary
    print("\n" + "="*50)
    print(f"Generation complete!")
    print(f"  Mode   : {args.mode}")
    print(f"  Size   : {height} x {width} pixels")
    print(f"  Total  : {height * width} bytes")
    print(f"  Files  : {args.name_img}, {args.name_h}")
    print("="*50)


if __name__ == "__main__":
    main()