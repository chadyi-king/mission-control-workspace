import os
import glob
from pathlib import Path
import time

SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")
LOG_DIR = Path("C:/DesktopControlAgent/logs")

def cleanup_screenshots(keep=300):
    """Keep only the most recent N screenshots"""
    if not SCREENSHOT_DIR.exists():
        print("Screenshots folder doesn't exist")
        return
    
    # Get all screenshot files sorted by modification time
    screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    total = len(screenshots)
    if total <= keep:
        print(f"Found {total} screenshots, keeping all (under limit of {keep})")
        return
    
    # Delete older screenshots
    to_delete = screenshots[keep:]
    for screenshot in to_delete:
        try:
            screenshot.unlink()
            print(f"Deleted: {screenshot.name}")
        except Exception as e:
            print(f"Error deleting {screenshot}: {e}")
    
    print(f"\nCleanup complete: Deleted {len(to_delete)} screenshots")
    print(f"Kept {keep} most recent screenshots")
    print(f"Freed approximately {len(to_delete) * 200 / 1024:.1f} MB")

def cleanup_logs(keep_days=7):
    """Delete log files older than N days"""
    if not LOG_DIR.exists():
        return
    
    now = time.time()
    cutoff = now - (keep_days * 86400)
    
    logs = LOG_DIR.glob("*.log")
    deleted = 0
    
    for log in logs:
        if log.stat().st_mtime < cutoff:
            try:
                log.unlink()
                deleted += 1
            except:
                pass
    
    if deleted > 0:
        print(f"Deleted {deleted} old log files")

def get_storage_usage():
    """Show current storage usage"""
    if SCREENSHOT_DIR.exists():
        screenshots = list(SCREENSHOT_DIR.glob("*.png"))
        total_size = sum(f.stat().st_size for f in screenshots)
        print(f"Screenshots: {len(screenshots)} files, {total_size / 1024 / 1024:.1f} MB")
    
    if LOG_DIR.exists():
        logs = list(LOG_DIR.glob("*.log"))
        total_size = sum(f.stat().st_size for f in logs)
        print(f"Logs: {len(logs)} files, {total_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    print("="*50)
    print("Desktop Control Agent - Storage Cleanup")
    print("="*50)
    print()
    
    print("BEFORE cleanup:")
    get_storage_usage()
    print()
    
    cleanup_screenshots(keep=20)  # Keep only 20 most recent
    cleanup_logs(keep_days=7)  # Keep 7 days of logs
    
    print()
    print("AFTER cleanup:")
    get_storage_usage()
    print()
    print("Done! Run this weekly to keep storage low.")
    input("Press Enter to exit...")
