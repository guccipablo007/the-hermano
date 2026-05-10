#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path

EXECUTOR = Path("/root/.hermes/scripts/hermes_rich_output_execute.py")
BATCH_EXECUTOR = Path("/root/.hermes/scripts/hermes_rich_batch_execute.py")

PRIVATE_WORDS = [
    "gmail", "email", "mail inbox", "youtube", "analytics", "subscriber",
    "api key", "token", "oauth", "password", "credential", "delete", "trash",
    "send email", "reply to email"
]

CREATE_WORDS = [
    "create", "make", "build", "generate", "prepare", "produce", "design"
]

ARTIFACT_WORDS = [
    "pdf", "docx", "word document", "word file", "pptx", "powerpoint",
    "slides", "slide deck", "presentation", "html", "webpage", "web page",
    "frontpage", "front page", "markdown", "md file", "flashcard",
    "flashcards", "worksheet", "lesson document", "lesson", "spreadsheet",
    "excel", "xlsx", "report", "dashboard"
]

DELIVERY_WORDS = [
    "send it to me", "send to telegram", "send it", "deliver", "as a pdf",
    "as docx", "as a docx", "as pptx", "as a pptx", "as xlsx", "as a file"
]

def _norm(text: str) -> str:
    return (text or "").lower().strip()

def _contains_any(text: str, words) -> bool:
    return any(w in text for w in words)

def is_artifact_request(text: str) -> bool:
    t = _norm(text)
    if not t:
        return False
    if _contains_any(t, PRIVATE_WORDS):
        return False
    has_create = _contains_any(t, CREATE_WORDS)
    has_artifact = _contains_any(t, ARTIFACT_WORDS)
    has_delivery = _contains_any(t, DELIVERY_WORDS)
    if has_create and has_artifact:
        return True
    if has_artifact and has_delivery:
        return True
    return False

def _clean_summary(output: str, max_chars: int = 3500) -> str:
    lines = []
    keep_prefixes = (
        "RICH_OUTPUT_EXECUTION_PLAN=", "RICH_OUTPUT_EXECUTION=",
        "BATCH_ARTIFACT_EXECUTION_PLAN=", "BATCH_ARTIFACT_EXECUTION=",
        "REQUESTED_FORMATS=", "ARTIFACT_START=", "ARTIFACT_RESULT=",
        "PASSED_FORMAT=", "PASSED_ROUTE=", "PASSED_OUTPUT=",
        "FAILED_FORMAT=", "FAILED_ROUTE=", "FAILED_REASON=",
        "OUTPUT_FORMAT=", "CONTENT_TYPE=", "VISUAL_POLICY=", "ROUTE=",
        "ROUTE_IMPLEMENTED=", "OUTPUT_PATH=", "VERIFICATION=",
        "MEDIA_VERIFY=", "MEDIA_COUNT=", "CHART_COUNT=", "DRAWING_COUNT=",
        "TELEGRAM_DELIVERY=", "NOT VERIFIED", "REASON=",
    )
    for raw in (output or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(keep_prefixes):
            lines.append(line)
    if not lines:
        text = (output or "").strip()
        return text[:max_chars] if text else "NOT VERIFIED\nREASON=NO_OUTPUT_FROM_EXECUTOR"
    final = ["ARTIFACT_PREROUTER=HANDLED"] + lines
    return "\n".join(final)[:max_chars]


def _requested_format_count(text: str) -> int:
    t = _norm(text)
    groups = [
        ("pdf", ["pdf"]),
        ("docx", ["docx", "word document", "word file", "word"]),
        ("pptx", ["pptx", "ppt", "powerpoint", "power point", "slides", "slide deck", "presentation"]),
        ("html", ["html", "webpage", "web page", "frontpage", "front page"]),
        ("xlsx", ["xlsx", "excel", "spreadsheet", "workbook"]),
        ("md", ["markdown", "md file"]),
    ]
    negated = set()
    negation_phrases = {
        "pdf": ["do not create pdf", "do not create a pdf", "not pdf"],
        "docx": ["do not create docx", "do not create a docx", "do not create word", "not docx"],
        "pptx": ["do not create pptx", "do not create ppt", "do not create powerpoint", "do not create power point", "not pptx"],
    }
    for fmt, phrases in negation_phrases.items():
        if any(p in t for p in phrases):
            negated.add(fmt)
    count = 0
    for fmt, words in groups:
        if fmt not in negated and any(w in t for w in words):
            count += 1
    return count

def handle_artifact_request(text: str) -> str:
    if not is_artifact_request(text):
        return ""
    executor = BATCH_EXECUTOR if _requested_format_count(text) > 1 else EXECUTOR
    cmd = [str(executor), "--request", text]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=420)
    except Exception as exc:
        return f"NOT VERIFIED\nREASON=ARTIFACT_EXECUTOR_EXCEPTION:{type(exc).__name__}:{exc}"
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    summary = _clean_summary(combined)
    if proc.returncode != 0:
        return "NOT VERIFIED\nREASON=ARTIFACT_EXECUTOR_FAILED\n" + summary
    return summary

def main():
    parser = argparse.ArgumentParser(description="Telegram natural artifact pre-router.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        print("IS_ARTIFACT_REQUEST=" + str(is_artifact_request(args.text)).upper())
        return 0
    result = handle_artifact_request(args.text)
    if not result:
        print("ARTIFACT_PREROUTER=NOT_HANDLED")
        return 2
    print(result)
    return 0 if "NOT VERIFIED" not in result else 1

if __name__ == "__main__":
    raise SystemExit(main())
