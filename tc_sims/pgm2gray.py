import numpy as np
from PIL import Image
import argparse

def pgmHex2Png(pgm_file, png_file):
    with open(pgm_file, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Magic
    if lines[0] != "P2":
        raise ValueError("Not a P2 PGM file")

    # IMPORTANT: height first, width second
    height, width = map(int, lines[1].split())

    pixel_lines = lines[3:]
    expected_pixels = height * width

    if len(pixel_lines) != expected_pixels:
        raise ValueError(
            f"Pixel count mismatch: expect {expected_pixels}, got {len(pixel_lines)}"
        )

    # Hex -> uint8
    pixels = np.array(
        [int(v, 16) for v in pixel_lines],
        dtype=np.uint8
    )

    # Row-major reshape
    img = pixels.reshape((height, width))

    # Save PNG
    Image.fromarray(img, mode="L").save(png_file)
    
    return height, width 

def main():
    parser = argparse.ArgumentParser(description="Convert PGM (P2) hex file to PNG grayscale image.")
    parser.add_argument("--name_pgm", default="pgm.png")
    parser.add_argument("--name_gray", default="gray.png")
    
    args = parser.parse_args()
    
    h, w = pgmHex2Png(args.name_pgm, args.name_gray) 
    
    print("Convert done!")
    print(f"Input : {args.name_pgm}")
    print(f"Output: {args.name_gray}")
    print(f"Size  : {h} x {w}")

if __name__ == "__main__":
    main()