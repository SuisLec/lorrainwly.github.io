import os
import re
import base64
from io import BytesIO

def trace_and_replace():
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("=" * 60)
        print("Error: Pillow (PIL) is not installed.")
        print("Please install it by running: pip install Pillow")
        print("=" * 60)
        return

    # Check for local signature files
    search_paths = [
        "signature.png",
        "signature.jpg",
        r"C:\Users\suis\.gemini\antigravity-ide\brain\9b17a871-b6ab-4b36-8017-31be0d0dd2b1\media__1779350641972.png",
        r"C:\Users\suis\.gemini\antigravity-ide\brain\9b17a871-b6ab-4b36-8017-31be0d0dd2b1\media__1779350268349.jpg"
    ]
    
    input_path = ""
    for path in search_paths:
        if os.path.exists(path):
            input_path = path
            print(f"Found signature image: {path}")
            break
            
    if not input_path:
        print("Error: Could not find signature image signature.png or signature.jpg in local folder.")
        return
        
    html_path = "index.html"
    
    print("Extracting handwriting with pixel-perfect anti-aliasing...")
    img = Image.open(input_path)
    
    # 1. Convert to RGBA and handle transparency
    img = img.convert("RGBA")
    width, height = img.size
    
    # 2. Extract handwriting alpha channel (pure white background to transparent, preserve gray antialiasing)
    # Threshold for absolute background white is set to 230 to filter out shadow/noise
    bg_threshold = 230
    
    # Calculate bounding box of non-white pixels first
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    
    # Create empty alpha mask and calculate bounding box
    alpha_data = []
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # Calculate luminance (0-255)
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            
            # If the pixel is transparent or very bright white, treat as background
            if a < 10 or gray >= bg_threshold:
                alpha = 0
            else:
                # Linear mapping of dark handwriting: pure black -> alpha 255, gray 230 -> alpha 0
                alpha = int((1.0 - (gray / bg_threshold)) * 255)
                # Keep alpha bounds
                alpha = max(0, min(255, alpha))
                
            alpha_data.append(alpha)
            
            # Update bounding box if it's a solid part of the signature
            if alpha > 30:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    if max_x < min_x or max_y < min_y:
        print("Error: No signature handwriting pixels detected in image.")
        return
        
    # Crop borders slightly to avoid clipping handwriting edges
    min_x = max(0, min_x - 4)
    min_y = max(0, min_y - 4)
    max_x = min(width - 1, max_x + 4)
    max_y = min(height - 1, max_y + 4)
    
    crop_w = max_x - min_x + 1
    crop_h = max_y - min_y + 1
    print(f"Detected handwriting bounds: {crop_w}x{crop_h} (cropped from {width}x{height})")
    
    # 3. Create two high-fidelity transparent PNGs: one in Black (#111111), one in Deep Purple (#4C1D95)
    # Both will perfectly match the fonts and lines of the user's signature with 0 noise
    dark_sig = Image.new("RGBA", (crop_w, crop_h))
    purple_sig = Image.new("RGBA", (crop_w, crop_h))
    
    dark_pixels = dark_sig.load()
    purple_pixels = purple_sig.load()
    
    for y in range(crop_h):
        for x in range(crop_w):
            orig_x = x + min_x
            orig_y = y + min_y
            alpha = alpha_data[orig_y * width + orig_x]
            
            # Black signature (#111111)
            dark_pixels[x, y] = (17, 17, 17, alpha)
            
            # Deep Purple signature (#4C1D95 = rgb(76, 29, 149))
            purple_pixels[x, y] = (76, 29, 149, alpha)
            
    # 4. Save to base64 strings
    def img_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
        
    base64_dark = img_to_base64(dark_sig)
    base64_purple = img_to_base64(purple_sig)
    
    # 5. Inject into index.html
    if not os.path.exists(html_path):
        print(f"Error: HTML file {html_path} not found.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Match the <a href="#about" class="nav-brand">...</a> tag
    pattern = r'(<a href="#about" class="nav-brand">)(.*?)(</a>)'
    
    # Elegant responsive image tag structure
    replacement_html = (
        f'<img src="data:image/png;base64,{base64_dark}" class="sig-img sig-dark" alt="Lorrain Wei Signature" />'
        f'<img src="data:image/png;base64,{base64_purple}" class="sig-img sig-purple" alt="Lorrain Wei Signature" />'
    )
    
    new_html_content, count = re.subn(pattern, rf'\g<1>{replacement_html}\g<3>', html_content, flags=re.DOTALL)
    
    if count > 0:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_html_content)
        print("Successfully updated index.html with pixel-perfect Base64 handwriting images!")
    else:
        print("Error: Could not find <a href=\"#about\" class=\"nav-brand\"> element in index.html.")

if __name__ == "__main__":
    trace_and_replace()
