#!/usr/bin/env python3
import argparse
import json
import re
import zipfile
from pathlib import Path

MEDIA_PREFIXES = {"pptx": "ppt/media/", "docx": "word/media/", "xlsx": "xl/media/"}
CHART_PREFIXES = {"pptx": "ppt/charts/", "docx": "word/charts/", "xlsx": "xl/charts/"}
DRAWING_PREFIXES = {"pptx": "ppt/drawings/", "docx": "word/drawings/", "xlsx": "xl/drawings/"}

def count_zip_prefix(path: Path, prefix: str) -> int:
    if not zipfile.is_zipfile(path):
        return 0
    with zipfile.ZipFile(path, "r") as z:
        return len([n for n in z.namelist() if n.startswith(prefix)])

def count_pdf_images(path: Path) -> int:
    raw = path.read_bytes()
    return raw.count(b"/Subtype /Image") + raw.count(b"/Subtype/Image")

def html_visual_count(path: Path) -> int:
    text = path.read_text(errors="ignore").lower()
    patterns = [r"<img\b", r"<svg\b", r"<canvas\b", r"background-image\s*:", r"data:image/", r"<picture\b"]
    return sum(len(re.findall(p, text)) for p in patterns)

def main():
    parser = argparse.ArgumentParser(description="Verify embedded media/visual evidence in generated output files.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--type", required=True, choices=["pptx", "docx", "xlsx", "pdf", "html"])
    parser.add_argument("--min-media", type=int, default=0)
    parser.add_argument("--min-charts", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.file)
    result = {
        "file": str(path), "type": args.type, "exists": path.exists(),
        "media_count": 0, "chart_count": 0, "drawing_count": 0,
        "media_prefix": MEDIA_PREFIXES.get(args.type, ""),
        "chart_prefix": CHART_PREFIXES.get(args.type, ""),
        "drawing_prefix": DRAWING_PREFIXES.get(args.type, ""),
        "passed": False, "reason": "",
    }

    if not path.exists() or not path.is_file():
        result["reason"] = "FILE_NOT_FOUND"
    elif args.type in ["pptx", "docx", "xlsx"]:
        if not zipfile.is_zipfile(path):
            result["reason"] = "NOT_ZIP_BASED_OFFICE_FILE"
        else:
            result["media_count"] = count_zip_prefix(path, MEDIA_PREFIXES[args.type])
            result["chart_count"] = count_zip_prefix(path, CHART_PREFIXES[args.type])
            result["drawing_count"] = count_zip_prefix(path, DRAWING_PREFIXES[args.type])
            if result["media_count"] < args.min_media:
                result["reason"] = f"MEDIA_COUNT_TOO_LOW:{result['media_count']}<{args.min_media}"
            elif result["chart_count"] < args.min_charts:
                result["reason"] = f"CHART_COUNT_TOO_LOW:{result['chart_count']}<{args.min_charts}"
            else:
                result["passed"] = True
                result["reason"] = "OK"
    elif args.type == "pdf":
        if not path.read_bytes().startswith(b"%PDF"):
            result["reason"] = "NOT_PDF"
        else:
            result["media_count"] = count_pdf_images(path)
            if result["media_count"] < args.min_media:
                result["reason"] = f"PDF_IMAGE_COUNT_TOO_LOW:{result['media_count']}<{args.min_media}"
            else:
                result["passed"] = True
                result["reason"] = "OK"
    elif args.type == "html":
        result["media_count"] = html_visual_count(path)
        if result["media_count"] < args.min_media:
            result["reason"] = f"HTML_VISUAL_COUNT_TOO_LOW:{result['media_count']}<{args.min_media}"
        else:
            result["passed"] = True
            result["reason"] = "OK"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("MEDIA_VERIFY=" + ("PASSED" if result["passed"] else "FAILED"))
        print("FILE=" + result["file"])
        print("TYPE=" + result["type"])
        print("MEDIA_COUNT=" + str(result["media_count"]))
        print("CHART_COUNT=" + str(result["chart_count"]))
        print("DRAWING_COUNT=" + str(result["drawing_count"]))
        print("MEDIA_PATH_PREFIX=" + result["media_prefix"])
        print("REASON=" + result["reason"])
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
