import numpy as np
from PIL import Image
import argparse

def generateGrayScale(height, width, mode):
    if mode == "gradient" or mode == "g":
        img = np.tile(
            np.linspace(0, 255, width, dtype=np.uint8),
            (height, 1)
        )
    elif mode == "random" or mode == "r":
        img = np.random.randint(0, 256, (height, width), dtype=np.uint8)
    elif mode == "constant" or mode == "c":
        img = np.full((height, width), 512, dtype=np.uint8)
    else:
        raise ValueError("Please choose right mode from: 'gradient(g)', 'random(r)' or 'constant(c)'")

    return img

def generateMemFile(filename, new_img):
    h, w = new_img.shape
    with open(filename, "w") as f:
        f.write(f"@00000000\n")     # Header
        f.write(f"{h:08X}\n")       # Height
        f.write(f"{w:08X}\n")       # Width
        for y in range(h):
            for x in range(w):
                f.write(f"{new_img[y, x]:02X}\n")

def main():
    parser = argparse.ArgumentParser(description="Generate grayscale image and save as MEM file.")
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--mode", choices=["gradient", "g",
                                           "random", "r", 
                                           "constant", "c"], default="random")
    parser.add_argument("--name_gray", default="gray.png")
    parser.add_argument("--name_mem", default="gray.mem")

    args = parser.parse_args()

    img = generateGrayScale(args.height, args.width, args.mode)

    # Save image
    Image.fromarray(img, mode="L").save(args.name_gray)

    # Save mem
    generateMemFile(args.name_mem, img)

    print("Done!")
    print(f"Image saved : {args.name_gray}")
    print(f"MEM file saved : {args.name_mem}")
    
if __name__ == "__main__":
    main()
