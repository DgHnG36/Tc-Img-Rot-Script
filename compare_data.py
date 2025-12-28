import numpy as np
from PIL import Image
import argparse
import sys
from pathlib import Path
from enum import Enum


# ANSI Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    
    @staticmethod
    def disable():
        """Disable colors (for Windows or when piping output)"""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.WHITE = ''
        Colors.BG_RED = ''
        Colors.BG_GREEN = ''
        Colors.BG_YELLOW = ''
        Colors.BG_BLUE = ''


class TransformType(Enum):
    """Enumeration of possible image transformations"""
    IDENTICAL = "Identical (No transformation)"
    ROTATE_CW = "Rotate Clockwise 90°"
    ROTATE_CCW = "Rotate Counter-Clockwise 90°"
    ROTATE_180 = "Rotate 180°"
    MIRROR_H = "Mirror Horizontal"
    MIRROR_V = "Mirror Vertical"
    UNKNOWN = "Unknown transformation"


class ImageComparator:
    """Compare two images to detect transformations"""
    
    def __init__(self, original_path, transformed_path, threshold=0.95, use_color=True):
        """
        Initialize comparator with image paths
        
        Args:
            original_path: Path to original image
            transformed_path: Path to transformed image
            threshold: Similarity threshold (0-1) for match detection
            use_color: Enable colored output
        """
        self.original_path = Path(original_path)
        self.transformed_path = Path(transformed_path)
        self.threshold = threshold
        
        self.original_img = None
        self.transformed_img = None
        
        # Disable colors if requested or on Windows without support
        if not use_color or (sys.platform == 'win32' and not self._supports_color()):
            Colors.disable()
    
    @staticmethod
    def _supports_color():
        """Check if terminal supports color"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        
    def load_images(self):
        """Load and validate both images"""
        try:
            self.original_img = np.array(Image.open(self.original_path).convert('L'))
            print(f"{Colors.GREEN}[+] Loaded original:{Colors.RESET} {Colors.CYAN}{self.original_path}{Colors.RESET}")
            print(f"    {Colors.BLUE}Size:{Colors.RESET} {self.original_img.shape[1]}x{self.original_img.shape[0]}")
            
        except Exception as e:
            raise FileNotFoundError(f"Failed to load original image: {e}")
        
        try:
            self.transformed_img = np.array(Image.open(self.transformed_path).convert('L'))
            print(f"{Colors.GREEN}[+] Loaded transformed:{Colors.RESET} {Colors.CYAN}{self.transformed_path}{Colors.RESET}")
            print(f"    {Colors.BLUE}Size:{Colors.RESET} {self.transformed_img.shape[1]}x{self.transformed_img.shape[0]}")
            
        except Exception as e:
            raise FileNotFoundError(f"Failed to load transformed image: {e}")
    
    def calculate_similarity(self, img1, img2):
        """
        Calculate similarity percentage between two images
        
        Args:
            img1: First numpy array
            img2: Second numpy array
            
        Returns:
            Similarity percentage (0-100)
        """
        if img1.shape != img2.shape:
            return 0.0
        
        # Calculate percentage of matching pixels
        matches = np.sum(img1 == img2)
        total = img1.size
        similarity = (matches / total) * 100
        
        return similarity
    
    def apply_rotate_cw(self, img):
        """Rotate image 90° clockwise"""
        return np.rot90(img, k=-1)  # k=-1 for clockwise
    
    def apply_rotate_ccw(self, img):
        """Rotate image 90° counter-clockwise"""
        return np.rot90(img, k=1)  # k=1 for counter-clockwise
    
    def apply_rotate_180(self, img):
        """Rotate image 180°"""
        return np.rot90(img, k=2)
    
    def apply_mirror_h(self, img):
        """Mirror image horizontally (flip left-right)"""
        return np.fliplr(img)
    
    def apply_mirror_v(self, img):
        """Mirror image vertically (flip up-down)"""
        return np.flipud(img)
    
    def detect_transformation(self):
        """
        Detect which transformation was applied
        
        Returns:
            tuple: (TransformType, similarity_percentage, all_results)
        """
        transformations = [
            (TransformType.IDENTICAL, lambda x: x),
            (TransformType.ROTATE_CW, self.apply_rotate_cw),
            (TransformType.ROTATE_CCW, self.apply_rotate_ccw),
            (TransformType.ROTATE_180, self.apply_rotate_180),
            (TransformType.MIRROR_H, self.apply_mirror_h),
            (TransformType.MIRROR_V, self.apply_mirror_v),
        ]
        
        best_match = TransformType.UNKNOWN
        best_similarity = 0.0
        results = []
        
        print("\n" + f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Testing transformations...{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        for trans_type, trans_func in transformations:
            try:
                transformed = trans_func(self.original_img)
                similarity = self.calculate_similarity(transformed, self.transformed_img)
                results.append((trans_type, similarity))
                
                # Color coding based on similarity
                is_match = similarity >= self.threshold * 100
                
                if is_match:
                    status = f"{Colors.GREEN}{Colors.BOLD}[+] MATCH{Colors.RESET}"
                    sim_color = Colors.GREEN
                elif similarity > 50:
                    status = f"{Colors.YELLOW}[~] PARTIAL{Colors.RESET}"
                    sim_color = Colors.YELLOW
                else:
                    status = f"{Colors.RED}[x] NO MATCH{Colors.RESET}"
                    sim_color = Colors.RED
                
                # Format output with colors
                trans_name = f"{Colors.WHITE}{trans_type.value}{Colors.RESET}"
                sim_value = f"{sim_color}{similarity:6.2f}%{Colors.RESET}"
                
                print(f"{status} {trans_name:.<55} {sim_value}")
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = trans_type
                    
            except Exception as e:
                print(f"{Colors.RED}[x] {trans_type.value:.<45} ERROR: {e}{Colors.RESET}")
        
        return best_match, best_similarity, results
    
    def visualize_difference(self, save_path=None):
        """
        Create difference visualization between images
        
        Args:
            save_path: Optional path to save difference image
        """
        if self.original_img.shape != self.transformed_img.shape:
            print(f"{Colors.YELLOW}[~] Cannot create difference map - different sizes{Colors.RESET}")
            return
        
        # Calculate absolute difference
        diff = np.abs(self.original_img.astype(np.int16) - 
                     self.transformed_img.astype(np.int16))
        diff_img = diff.astype(np.uint8)
        
        # Amplify differences for visualization
        diff_amplified = np.clip(diff * 5, 0, 255).astype(np.uint8)
        
        if save_path:
            Image.fromarray(diff_amplified).save(save_path)
            print(f"{Colors.GREEN}[+] Difference map saved:{Colors.RESET} {Colors.CYAN}{save_path}{Colors.RESET}")
        
        # Calculate statistics
        non_zero = np.count_nonzero(diff)
        total = diff.size
        diff_percentage = (non_zero / total) * 100
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}Difference Statistics:{Colors.RESET}")
        print(f"  {Colors.WHITE}Different pixels:{Colors.RESET} {non_zero}/{total} ({Colors.YELLOW}{diff_percentage:.2f}%{Colors.RESET})")
        print(f"  {Colors.WHITE}Max difference:{Colors.RESET}   {Colors.RED}{np.max(diff)}{Colors.RESET}")
        print(f"  {Colors.WHITE}Mean difference:{Colors.RESET}  {Colors.YELLOW}{np.mean(diff):.2f}{Colors.RESET}")
    
    def compare(self, save_diff=False):
        """
        Main comparison process
        
        Args:
            save_diff: Whether to save difference map
            
        Returns:
            TransformType detected
        """
        print("\n" + f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}       IMAGE TRANSFORMATION DETECTOR{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        # Load images
        self.load_images()
        
        # Detect transformation
        detected_type, similarity, all_results = self.detect_transformation()
        
        # Print results
        print("\n" + f"{Colors.BOLD}{Colors.MAGENTA}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}           DETECTION RESULT{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*60}{Colors.RESET}")
        
        if similarity >= self.threshold * 100:
            print(f"{Colors.GREEN}{Colors.BOLD}[+] Detected transformation:{Colors.RESET} {Colors.CYAN}{detected_type.value}{Colors.RESET}")
            print(f"    {Colors.BLUE}Confidence:{Colors.RESET} {Colors.GREEN}{Colors.BOLD}{similarity:.2f}%{Colors.RESET}")
            
            # Map to mode values
            mode_map = {
                TransformType.ROTATE_CW: 0,
                TransformType.ROTATE_CCW: 1,
                TransformType.MIRROR_H: 2,
                TransformType.MIRROR_V: 3,
            }
            
            if detected_type in mode_map:
                print(f"    {Colors.BLUE}Mode value:{Colors.RESET} {Colors.YELLOW}{mode_map[detected_type]}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}[~] No clear transformation detected{Colors.RESET}")
            print(f"    {Colors.WHITE}Best match:{Colors.RESET} {detected_type.value} ({Colors.YELLOW}{similarity:.2f}%{Colors.RESET})")
            print(f"    {Colors.WHITE}Threshold:{Colors.RESET}  {Colors.RED}{self.threshold * 100:.2f}%{Colors.RESET}")
        
        # Create difference visualization if requested
        if save_diff:
            diff_path = self.transformed_path.parent / "difference_map.png"
            self.visualize_difference(diff_path)
        
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*60}{Colors.RESET}\n")
        
        return detected_type


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Detect transformation between two grayscale images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Transformations:
  - Rotate Clockwise 90° (CW)
  - Rotate Counter-Clockwise 90° (CCW)
  - Rotate 180°
  - Mirror Horizontal (flip left-right)
  - Mirror Vertical (flip up-down)

Examples:
  %(prog)s original.png output.png
  %(prog)s input.png rotated.png --threshold 0.98
  %(prog)s original.png transformed.png --diff
  %(prog)s original.png output.png --no-color
        """
    )
    
    parser.add_argument("original", 
                       help="Path to original image")
    parser.add_argument("transformed",
                       help="Path to transformed image")
    parser.add_argument("-t", "--threshold", type=float, default=0.95,
                       help="Similarity threshold for match (0-1, default: 0.95)")
    parser.add_argument("-d", "--diff", action="store_true",
                       help="Save difference map visualization")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Show detailed comparison results")
    parser.add_argument("--no-color", action="store_true",
                       help="Disable colored output")
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Validate threshold
    if not 0 <= args.threshold <= 1:
        print(f"{Colors.RED}[ERROR] Threshold must be between 0 and 1{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create comparator and run
        comparator = ImageComparator(
            args.original, 
            args.transformed,
            args.threshold,
            use_color=not args.no_color
        )
        
        detected = comparator.compare(save_diff=args.diff)
        
        # Exit code based on detection
        if detected != TransformType.UNKNOWN:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # No clear match
            
    except FileNotFoundError as e:
        print(f"{Colors.RED}[ERROR] {e}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Unexpected error: {e}{Colors.RESET}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()