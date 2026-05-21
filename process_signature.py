import os
import re

def trace_and_replace():
    try:
        from PIL import Image
    except ImportError:
        print("=" * 60)
        print("Error: Pillow (PIL) is not installed.")
        print("Please install it by running: pip install Pillow")
        print("=" * 60)
        return

    # Look for signature.png first, then signature.jpg, and cache paths as fallbacks
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
        print("Error: Could not find signature image in local folder or system cache.")
        return
        
    html_path = "index.html"
    
    print("Tracing signature image to high-fidelity vector SVG...")
    img = Image.open(input_path)
    
    # Handle transparency in PNG: composite over a white background
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        gray = background.convert("L")
    else:
        gray = img.convert("L")
    
    # Resize to height of 48px to keep the SVG compact, smooth out noise, 
    # and match the navbar signature height perfectly.
    target_h = 48
    width, height = img.size
    aspect = width / height
    target_w = int(target_h * aspect)
    
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        # Fallback for older Pillow versions
        resample_filter = Image.ANTIALIAS
        
    gray_resized = gray.resize((target_w, target_h), resample_filter)
    
    # Get bounding box of pixels below threshold (dark handwriting on light background)
    pixels = gray_resized.load()
    threshold = 150  # Ink is dark (low value), background is light (high value)
    
    min_x, min_y = target_w, target_h
    max_x, max_y = 0, 0
    
    for y in range(target_h):
        for x in range(target_w):
            if pixels[x, y] < threshold:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    if max_x < min_x or max_y < min_y:
        print("Error: No signature pixels detected.")
        return
        
    # Crop dimensions
    crop_w = max_x - min_x + 1
    crop_h = max_y - min_y + 1
    
    print(f"Resized bounding box: x={min_x}..{max_x}, y={min_y}..{max_y} (size: {crop_w}x{crop_h})")
    
    # Extract horizontal spans, offset to (0, 0)
    path_segments = []
    for y in range(min_y, max_y + 1):
        in_span = False
        start_x = 0
        for x in range(min_x, max_x + 2):
            is_active = (x <= max_x) and (pixels[x, y] < threshold)
            if is_active:
                if not in_span:
                    in_span = True
                    start_x = x
            else:
                if in_span:
                    in_span = False
                    w = x - start_x
                    offset_x = start_x - min_x
                    offset_y = y - min_y
                    path_segments.append(f"M {offset_x} {offset_y} h {w}")
                    
    path_d = " ".join(path_segments)
    
    # Create the high-fidelity vector inline SVG
    svg_code = (
        f'<svg viewBox="0 0 {crop_w} {crop_h}" class="nav-signature-svg" aria-label="Lorrain Wei Signature">'
        f'<path d="{path_d}" />'
        f'</svg>'
    )
    
    # 2. Save standalone SVG file
    with open("signature.svg", "w", encoding="utf-8") as f:
        f.write(
            f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {crop_w} {crop_h}" width="{crop_w}" height="{crop_h}">\n'
            f'  <path d="{path_d}" fill="none" stroke="#111111" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />\n'
            f'</svg>\n'
        )
    print("Saved standalone vector SVG to signature.svg")
    
    # 3. Read index.html and replace the brand with this SVG
    if not os.path.exists(html_path):
        print(f"Error: HTML file {html_path} not found.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Match `<a href="#about" class="nav-brand">...</a>`
    pattern = r'(<a href="#about" class="nav-brand">)(.*?)(</a>)'
    
    new_html_content, count = re.subn(pattern, rf'\g<1>{svg_code}\g<3>', html_content, flags=re.DOTALL)
    
    if count > 0:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_html_content)
        print("Successfully updated index.html with inline vector SVG signature!")
    else:
        print("Error: Could not find <a href=\"#about\" class=\"nav-brand\"> element in index.html.")

if __name__ == "__main__":
    trace_and_replace()
