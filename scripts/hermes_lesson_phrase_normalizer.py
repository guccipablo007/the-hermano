#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

PHRASE_MAP = {
    "wake up": ("Wake Up", "I wake up in the morning."),
    "brush teeth": ("Brush My Teeth", "I brush my teeth."),
    "wash face": ("Wash My Face", "I wash my face."),
    "get dressed": ("Get Dressed", "I get dressed."),
    "eat breakfast": ("Eat Breakfast", "I eat breakfast."),
    "pack school bag": ("Pack My School Bag", "I pack my school bag."),
    "go to school": ("Go to School", "I go to school."),
    "learn new things": ("Learn New Things", "I learn new things."),
    "do art projects": ("Do Art Projects", "I do art projects."),
    "play with friends": ("Play With Friends", "I play with my friends."),
    "eat lunch": ("Eat Lunch", "I eat lunch."),
    "come home": ("Come Home", "I come home."),
    "play time": ("Play Time", "I have play time."),
    "do homework": ("Do Homework", "I do my homework."),
    "eat dinner": ("Eat Dinner", "I eat dinner."),
    "take bath": ("Take a Bath", "I take a bath."),
    "take a bath": ("Take a Bath", "I take a bath."),
    "go to bed": ("Go to Bed", "I go to bed."),
}

def clean_label(text):
    text = re.sub(r"^\d+\.\s*", "", text or "")
    text = re.sub(r"^[^\wA-Za-z]+", "", text)
    text = re.sub(r"\s+", " ", text).strip(" .,:;")
    return text

def normalize_phrase(text):
    raw = clean_label(text)
    key = raw.lower()
    for phrase, pair in PHRASE_MAP.items():
        if phrase == key or phrase in key:
            return {"title": pair[0], "word": pair[0], "sentence": pair[1], "image": phrase, "source_label": raw}
    title = raw[:1].upper() + raw[1:] if raw else "Daily Routine"
    return {"title": title, "word": title, "sentence": f"I {raw.lower()}." if raw else "I follow my routine.", "image": raw.lower(), "source_label": raw}

def normalize_sections_file(path, output):
    data = json.loads(Path(path).read_text())
    normalized = []
    for item in data:
        label = item.get("title") or item.get("word") or item.get("image") or ""
        normalized.append(normalize_phrase(label))
    Path(output).write_text(json.dumps(normalized, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Normalize kids lesson routine phrases into clean titles and grammar.")
    parser.add_argument("--phrase", default="")
    parser.add_argument("--sections-json", default="")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    if args.phrase:
        print(json.dumps(normalize_phrase(args.phrase), indent=2))
        return 0
    if args.sections_json and args.output:
        normalize_sections_file(args.sections_json, args.output)
        print("PHRASE_NORMALIZATION=PASSED")
        print("OUTPUT=" + args.output)
        return 0
    parser.print_help()
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
