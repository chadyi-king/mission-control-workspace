import pytesseract
from PIL import Image
from pathlib import Path
import json
import re
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")

def analyze_all_screenshots():
    """Analyze all recent screenshots for signal patterns"""
    screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    all_signals = []
    
    print(f"Analyzing {min(10, len(screenshots))} recent screenshots...")
    
    for i, screenshot in enumerate(screenshots[:10]):
        try:
            img = Image.open(screenshot)
            text = pytesseract.image_to_string(img)
            
            # Look for signal patterns
            patterns = {
                "symbol": r"(XAUUSD|XAGUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|USDCAD|GBPJPY|EURJPY)",
                "direction": r"\b(BUY|SELL)\b",
                "entry_range": r"(?:Buy|Sell)\s*Range[:\s]+(\d+\.?\d*)\s*[-~to]+\s*(\d+\.?\d*)",
                "entry_single": r"(?:entry|Entry)[:\s]+(\d+\.?\d*)",
                "sl": r"SL[:\s]+(\d+\.?\d*)",
                "tp_all": r"TP[:\s]+([\d\s/.]+)",
                "tp_single": r"TP\d*[:\s]+(\d+\.?\d*)"
            }
            
            signal = {
                "file": screenshot.name,
                "time": time.ctime(screenshot.stat().st_mtime),
                "raw_text": text[:300],
                "detected": {}
            }
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    signal["detected"][key] = matches
            
            # Only keep if we found trading signals
            if signal["detected"] and ("BUY" in text.upper() or "SELL" in text.upper()):
                all_signals.append(signal)
                print(f"\n✓ Screenshot {i+1}: {screenshot.name}")
                print(f"  Detected: {list(signal['detected'].keys())}")
            
        except Exception as e:
            print(f"✗ Error analyzing {screenshot}: {e}")
    
    return all_signals

if __name__ == "__main__":
    signals = analyze_all_screenshots()
    
    print("\n" + "="*60)
    print(f"ANALYSIS COMPLETE: Found {len(signals)} screenshots with signals")
    print("="*60)
    
    # Summary of patterns
    symbols = set()
    directions = set()
    
    for s in signals:
        if "symbol" in s["detected"]:
            symbols.update(s["detected"]["symbol"])
        if "direction" in s["detected"]:
            directions.update(s["detected"]["direction"])
    
    print(f"\nSymbols detected: {list(symbols)}")
    print(f"Directions detected: {list(directions)}")
    print(f"\nFull results saved to: signal_analysis.json")
    
    # Save detailed results
    with open("C:/DesktopControlAgent/signal_analysis.json", "w") as f:
        json.dump(signals, f, indent=2)
    
    print("\nDone! Check signal_analysis.json for details.")
