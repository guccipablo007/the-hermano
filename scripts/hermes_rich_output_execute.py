#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

PLAN = Path("/root/.hermes/scripts/hermes_rich_output_plan.py")
ROUTER = Path("/root/.hermes/scripts/hermes_router_execute.py")
MEDIA_VERIFY = Path("/root/.hermes/scripts/hermes_media_verify.py")

def run(cmd, timeout=300):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)

def q(s): return json.dumps(str(s))
def slug(text): return re.sub(r"[^a-z0-9]+", "_", (text or "output").lower()).strip("_")[:70] or "output"

def detect_title(request, plan):
    m = re.search(r"[?\"]([^?\"]+)[?\"]", request)
    if m: return m.group(1).strip()
    low = request.lower()
    for marker in ["about ", "titled ", "called "]:
        if marker in low:
            part = request[low.index(marker)+len(marker):]
            part = re.split(r"\bfor\b|\band\b|\bsend\b|\bas\b|\." , part, flags=re.I)[0]
            title = part.strip(" .,:;\"'??").title()
            if title: return title
    return plan.get("content_type", "Output").replace("_", " ").title()

def detect_age(request):
    low = request.lower()
    m = re.search(r"(\d+)\s*[- ]?\s*year[- ]?old", low)
    if m: return f"{m.group(1)}-year-old kids"
    m = re.search(r"aged?\s+(\d+)\s*(?:to|-)\s*(\d+)", low)
    if m: return f"{m.group(1)}-{m.group(2)} year-old kids"
    if "kids" in low or "children" in low: return "kids"
    return "general audience"

def detect_slide_count(request):
    m = re.search(r"(\d+)\s*[- ]?\s*slide", request.lower())
    return int(m.group(1)) if m else 8

def extension_for_route(route):
    return {"rich_pdf_picture_file":"pdf","rich_docx_picture_file":"docx","pdf_file":"pdf","docx_file":"docx","pptx_file":"pptx","pptx_picture_file":"pptx","md_file":"md","html_file":"html","flashcards_pdf":"pdf"}.get(route,"out")

def media_type_for_ext(ext): return {"pdf":"pdf","docx":"docx","pptx":"pptx","xlsx":"xlsx","html":"html"}.get(ext)

def build_command(route, output, title, topic, age, slide_count, request):
    if route in ["rich_pdf_picture_file", "rich_docx_picture_file"]:
        return f"{ROUTER} {route} --output {q(output)} --title {q(title)} --topic {q(topic)} --age {q(age)} --min-media 1"
    if route == "pptx_picture_file":
        return f"{ROUTER} pptx_picture_file --output {q(output)} --title {q(title)} --topic {q(topic)} --age {q(age)} --slide-count {int(slide_count)} --min-media {int(slide_count)}"
    if route == "flashcards_pdf":
        return f"{ROUTER} flashcards_pdf --output {q(output)} --title {q(title)} --theme {q(topic)} --age {q(age)}"
    if route in ["pdf_file", "docx_file", "pptx_file", "md_file"]:
        return f"{ROUTER} {route} --output {q(output)} --title {q(title)} --description {q(request)} --expect-text {q(title)}"
    if route == "html_file":
        return f"{ROUTER} html_file --output {q(output)} --description {q(request)} --expect-text {q(title)}"
    raise RuntimeError(f"UNSUPPORTED_ROUTE:{route}")

def main():
    parser = argparse.ArgumentParser(description="Plan and execute rich Hermes output requests.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--no-deliver-telegram", action="store_true")
    parser.add_argument("--show-command", action="store_true")
    args = parser.parse_args()

    plan_proc = run(f"{PLAN} --request {q(args.request)} --json", timeout=120)
    if plan_proc.returncode != 0:
        print("NOT VERIFIED"); print("REASON=PLAN_FAILED"); print(plan_proc.stdout); print(plan_proc.stderr); return plan_proc.returncode
    plan = json.loads(plan_proc.stdout)
    route = plan.get("route"); route_implemented = bool(plan.get("route_implemented")); visual_policy = plan.get("visual_policy", "auto"); output_format = plan.get("output_format", "unknown"); content_type = plan.get("content_type", "general")
    title = detect_title(args.request, plan); topic = title; age = detect_age(args.request); slide_count = detect_slide_count(args.request)
    if not route_implemented:
        print("NOT VERIFIED"); print("REASON=ROUTE_NOT_IMPLEMENTED"); print("ROUTE=" + str(route)); print("OUTPUT_FORMAT=" + str(output_format)); print("CONTENT_TYPE=" + str(content_type)); print("VISUAL_POLICY=" + str(visual_policy)); return 2
    ext = extension_for_route(route)
    output = Path(args.output) if args.output else ((Path("/root/.hermes/newcoin_outputs") if ext == "html" else Path("/root/.hermes/file_outputs")) / f"{slug(title)}.{ext}")
    cmd = build_command(route, output, title, topic, age, slide_count, args.request)
    if args.no_deliver_telegram: cmd += " --no-deliver-telegram"
    exec_proc = run(cmd, timeout=360)
    print("RICH_OUTPUT_EXECUTION_PLAN=PASSED"); print("REQUEST=" + args.request); print("OUTPUT_FORMAT=" + str(output_format)); print("CONTENT_TYPE=" + str(content_type)); print("VISUAL_POLICY=" + str(visual_policy)); print("ROUTE=" + str(route)); print("ROUTE_IMPLEMENTED=" + str(route_implemented).upper()); print("OUTPUT_PATH=" + str(output))
    if args.show_command:
        print("EXECUTED_COMMAND=" + cmd)
    print("ROUTER_STDOUT_START"); print(exec_proc.stdout.strip()); print("ROUTER_STDOUT_END")
    if exec_proc.stderr.strip(): print("ROUTER_STDERR_START"); print(exec_proc.stderr.strip()); print("ROUTER_STDERR_END")
    if exec_proc.returncode != 0:
        print("NOT VERIFIED"); print("REASON=ROUTER_EXECUTION_FAILED"); return exec_proc.returncode
    media_type = media_type_for_ext(ext)
    if visual_policy == "required" and media_type:
        min_media = slide_count if route == "pptx_picture_file" else 1
        mv = run(f"{MEDIA_VERIFY} --file {q(output)} --type {media_type} --min-media {int(min_media)}", timeout=120)
        print("MEDIA_VERIFY_STDOUT_START"); print(mv.stdout.strip()); print("MEDIA_VERIFY_STDOUT_END")
        if mv.returncode != 0:
            print("NOT VERIFIED"); print("REASON=MEDIA_VERIFY_FAILED"); return mv.returncode
    print("RICH_OUTPUT_EXECUTION=PASSED"); print("VERIFICATION=PASSED"); print("TELEGRAM_DELIVERY=PASSED_OR_ROUTER_REPORTED"); return 0

if __name__ == "__main__": raise SystemExit(main())
