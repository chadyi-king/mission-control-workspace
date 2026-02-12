Set WshShell = CreateObject("WScript.Shell")

' Start the Desktop Control Agent in a new window
WshShell.Run "cmd /k cd /d C:\DesktopControlAgent && py agent.py", 1, False

' Wait 5 seconds
WScript.Sleep 5000

' Start ngrok in another window
WshShell.Run "cmd /k ngrok http 5000", 1, False

MsgBox "Agent and ngrok are starting!" & vbCrLf & vbCrLf & "Wait for the ngrok URL to appear, then copy it and give it to CHAD_YI.", vbInformation, "Desktop Agent Starting"
