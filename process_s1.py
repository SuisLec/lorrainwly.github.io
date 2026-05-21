import os
import sys

def process_signature():
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is not installed. Installing Pillow...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image

    input_path = "s1.png"
    output_path = "s1_cherry.png"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found in current directory.")
        return False

    print(f"Loading signature from {input_path}...")
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # 230 to 240 is usually perfect for extracting dark handwriting on bright white background
    bg_threshold = 240
    
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    
    # Extract alpha channel while keeping anti-aliasing
    alpha_data = []
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # Handle if the pixel already has transparency
            if a < 10:
                alpha = 0
            else:
                # Calculate luminance
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                if gray >= bg_threshold:
                    alpha = 0
                else:
                    # Linear mapping: black -> 255 alpha, threshold -> 0 alpha
                    alpha = int((1.0 - (gray / bg_threshold)) * 255)
                    alpha = max(0, min(255, alpha))
            
            alpha_data.append(alpha)
            
            # Detect bounds of non-empty pixels
            if alpha > 15:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    if max_x < min_x or max_y < min_y:
        print("Warning: No signature pixels detected. Defaulting to full size.")
        min_x, min_y, max_x, max_y = 0, 0, width - 1, height - 1
    else:
        # Add a 6-pixel padding around signature
        min_x = max(0, min_x - 6)
        min_y = max(0, min_y - 6)
        max_x = min(width - 1, max_x + 6)
        max_y = min(height - 1, max_y + 6)

    crop_w = max_x - min_x + 1
    crop_h = max_y - min_y + 1
    print(f"Signature bounds detected: {crop_w}x{crop_h}")
    
    # Create the high-fidelity Cherry Red signature image
    # #EE6A7B corresponds to RGB (238, 106, 123)
    cherry_red = (238, 106, 123)
    new_img = Image.new("RGBA", (crop_w, crop_h))
    new_pixels = new_img.load()
    
    for y in range(crop_h):
        for x in range(crop_w):
            orig_x = x + min_x
            orig_y = y + min_y
            alpha = alpha_data[orig_y * width + orig_x]
            new_pixels[x, y] = (cherry_red[0], cherry_red[1], cherry_red[2], alpha)
            
    new_img.save(output_path, "PNG")
    print(f"Processed signature saved successfully to {output_path}!")
    return True

if __name__ == "__main__":
    process_signature()
