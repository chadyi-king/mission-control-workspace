import pytesseract
from PIL import Image
from pathlib import Path
import json
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")

def analyze_callistofx():
    """Read and analyze CallistoFx channel for trading signals"""
    try:
        screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not screenshots:
            return {"error": "No screenshots found"}
        
        # Read latest 3 screenshots to find signal pattern
        results = []
        for i, screenshot in enumerate(screenshots[:3]):
            img = Image.open(screenshot)
            text = pytesseract.image_to_string(img)
            
            # Look for trading signals
            signal_patterns = {
                "symbol": r"(XAUUSD|EURUSD|GBPUSD|USDJPY|GBPJPY|XAGUSD)",
                "direction": r"(BUY|SELL)",
                "entry": r"entry[:\s]+(\d+\.?\d*)",
                "sl": r"SL[:\s]+(\d+\.?\d*)",
                "tp": r"TP[:\s]+(\d+\.?\d*)"
            }
            
            found = {"file": screenshot.name, "text": text[:500], "signals": {}}
            
            for key, pattern in signal_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found["signals"][key] = matches
            
            results.append(found)
        
        return results
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    results = analyze_callistofx()
    print(json.dumps(results, indent=2))
