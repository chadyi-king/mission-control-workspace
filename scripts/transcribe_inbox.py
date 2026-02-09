#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import whisper  # type: ignore
except Exception as e:
    print(f"ERROR: whisper module not available: {e}", file=sys.stderr)
    sys.exit(2)

INBOX = Path("/home/chad-yi/.openclaw/media/inbound")
STATE_PATH = Path("/home/chad-yi/.openclaw/workspace/memory/voice_state.json")


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return {"processed": {}}
    return {"processed": {}}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def transcribe(model, file_path: Path, language: str = "en"):
    audio_path = str(file_path)
    result = model.transcribe(audio_path, language=language, fp16=False)
    text = (result.get("text") or "").strip()
    segments = result.get("segments") or []
    lang = result.get("language") or language
    # Confidence heuristics
    avg_logprobs = [s.get("avg_logprob") for s in segments if s.get("avg_logprob") is not None]
    mean_avg_logprob = sum(avg_logprobs) / len(avg_logprobs) if avg_logprobs else None
    no_speech = [s.get("no_speech_prob") for s in segments if s.get("no_speech_prob") is not None]
    mean_no_speech = sum(no_speech) / len(no_speech) if no_speech else None
    compression_ratio = result.get("compression_ratio")

    low_conf = False
    if mean_avg_logprob is not None and mean_avg_logprob < -1.1:
        low_conf = True
    if compression_ratio is not None and compression_ratio > 2.4:
        low_conf = True
    if mean_no_speech is not None and mean_no_speech > 0.85 and len(text) < 20:
        low_conf = True

    meta = {
        "file": file_path.name,
        "text": text,
        "language": lang,
        "segments": len(segments),
        "mean_avg_logprob": mean_avg_logprob,
        "mean_no_speech": mean_no_speech,
        "compression_ratio": compression_ratio,
        "needs_clarification": low_conf,
        "ts": int(time.time()),
    }
    return text, meta


def process_once(model_name: str = "medium", language: str = "en", limit: int = 2):
    model = whisper.load_model(model_name)
    state = load_state()
    processed = state.get("processed", {})

    # Pick new .ogg files without sidecar .txt
    files = sorted([p for p in INBOX.glob("*.ogg")], key=lambda p: p.stat().st_mtime)

    done = 0
    outputs = []
    for f in files:
        key = f.name
        if key in processed:
            continue
        try:
            text, meta = transcribe(model, f, language=language)
            # Write sidecars
            txt_path = f.with_suffix(f.suffix + ".txt")
            json_path = f.with_suffix(f.suffix + ".json")
            txt_path.write_text(text + "\n")
            json_path.write_text(json.dumps(meta, indent=2))

            processed[key] = meta
            outputs.append(meta)
            done += 1
        except Exception as e:
            processed[key] = {"error": str(e), "ts": int(time.time())}
        if done >= limit:
            break

    state["processed"] = processed
    save_state(state)
    return outputs


def main():
    ap = argparse.ArgumentParser(description="Transcribe new Telegram voice messages in the inbox using OpenAI Whisper.")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--language", default="en")
    ap.add_argument("--limit", type=int, default=2, help="max files to process per run")
    args = ap.parse_args()

    outs = process_once(args.model, args.language, args.limit)
    # Print a concise JSON for the caller
    print(json.dumps({"processed": outs}, indent=2))


if __name__ == "__main__":
    main()
