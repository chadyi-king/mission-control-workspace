#!/usr/bin/env python3
"""
Open Telegram Web using Windows Chrome from WSL2
"""

import subprocess
import time

# Launch Windows Chrome with Telegram Web
chrome_path = "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
url = "https://web.telegram.org"

print("Opening Telegram Web in Brave...")
subprocess.Popen([chrome_path, url], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)

print("Browser launched!")
print("Go to your Windows desktop - Brave should be open with Telegram Web")
print("Log in with your phone number, then tell me when you're logged in.")