import subprocess
import sys
import json
import os

# Usage: python3 transcribe.py input_audio.ogg output_base
# Outputs:
#   output_base.txt - plain text transcript
#   output_base.json - JSON output with confidence info

def transcribe(input_audio, output_base):
    # Command setup
    cmd = [
        "python3", "-m", "whisper",
        input_audio,
        "--model", "medium",
        "--language", "en",
        "--output_format", "json",
        "--output_dir", os.path.dirname(output_base)
    ]

    # Run transcription
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

    # Whisper with --output_format json outputs JSON file
    json_file = f"{output_base}.json"
    txt_file = f"{output_base}.txt"

    # Sometimes Whisper creates txt file also; if not, create one from JSON text
    if not os.path.exists(txt_file) and os.path.exists(json_file):
        with open(json_file, "r") as jf:
            data = json.load(jf)
            text = data.get("text", "")
        with open(txt_file, "w") as tf:
            tf.write(text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 transcribe.py input_audio.ogg output_base")
        sys.exit(1)

    input_audio = sys.argv[1]
    output_base = sys.argv[2]

    transcribe(input_audio, output_base)
