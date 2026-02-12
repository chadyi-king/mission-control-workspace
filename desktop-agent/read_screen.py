import pytesseract
from PIL import Image
from pathlib import Path
import sys

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")

def read_latest_screenshot():
    """Read text from most recent screenshot"""
    try:
        # Get most recent screenshot
        screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not screenshots:
            return "No screenshots found"
        
        latest = screenshots[0]
        
        # Read image
        img = Image.open(latest)
        
        # OCR
        text = pytesseract.image_to_string(img)
        
        return {
            "file": latest.name,
            "text": text
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = read_latest_screenshot()
    
    if isinstance(result, dict) and "text" in result:
        print("="*50)
        print(f"Screenshot: {result['file']}")
        print("="*50)
        print(result['text'])
        print("="*50)
    else:
        print(result)
