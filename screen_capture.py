import time
import os
from datetime import datetime
from PIL import ImageGrab
import json

# Configuration
SCREENSHOT_DIR = os.path.expanduser("~/openclaw_screenshots")
INTERVAL = 5  # seconds
MAX_SCREENSHOTS = 100  # Keep last 100

def ensure_dir():
    """Create screenshot directory if not exists"""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        print(f"Created directory: {SCREENSHOT_DIR}")

def take_screenshot():
    """Capture full screen and save"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    
    try:
        # Capture screen
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        print(f"✓ Screenshot saved: {filename}")
        
        # Update latest.json for easy access
        latest_info = {
            "latest_screenshot": filename,
            "timestamp": timestamp,
            "path": filepath
        }
        with open(os.path.join(SCREENSHOT_DIR, "latest.json"), "w") as f:
            json.dump(latest_info, f)
        
        # Clean up old screenshots
        cleanup_old_screenshots()
        
        return filepath
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def cleanup_old_screenshots():
    """Keep only the most recent MAX_SCREENSHOTS"""
    files = sorted([f for f in os.listdir(SCREENSHOT_DIR) if f.startswith("screenshot_") and f.endswith(".png")])
    
    while len(files) > MAX_SCREENSHOTS:
        old_file = files.pop(0)
        os.remove(os.path.join(SCREENSHOT_DIR, old_file))
        print(f"  Deleted old: {old_file}")

def main():
    """Main loop - screenshot every INTERVAL seconds"""
    ensure_dir()
    print(f"\n{'='*60}")
    print("OpenClaw Screen Capture Service")
    print(f"{'='*60}")
    print(f"Directory: {SCREENSHOT_DIR}")
    print(f"Interval:  {INTERVAL} seconds")
    print(f"Max files: {MAX_SCREENSHOTS}")
    print(f"{'='*60}\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            take_screenshot()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n\nStopping screen capture...")
        print(f"Screenshots saved in: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
