import os
from PIL import Image

def process_signature():
    # Source path from the local brain workspace where the uploaded signature image is stored
    input_path = r"C:\Users\suis\.gemini\antigravity-ide\brain\9b17a871-b6ab-4b36-8017-31be0d0dd2b1\media__1779350268349.jpg"
    output_path = "signature.png"
    
    if not os.path.exists(input_path):
        print(f"Notice: Source signature image {input_path} not found.")
        print("If you have already processed the signature, signature.png will be reused.")
        return

    print("Processing signature image...")
    # Load image
    img = Image.open(input_path)
    # Convert to grayscale
    gray = img.convert("L")
    
    # Create new RGBA transparent image
    new_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    
    pixels = gray.load()
    new_pixels = new_img.load()
    
    for x in range(img.width):
        for y in range(img.height):
            val = pixels[x, y]
            if val > 30:  # Threshold to filter out noise
                # Direct mapping to alpha channel for smooth anti-aliased edges
                alpha = min(255, int(val * 1.8))
                new_pixels[x, y] = (17, 17, 17, alpha)  # Solid black/dark gray
                
    # Save the resulting transparent PNG
    new_img.save(output_path)
    print("Signature processed and saved to signature.png successfully!")

if __name__ == "__main__":
    process_signature()
