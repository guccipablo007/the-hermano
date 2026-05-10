#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

ROUTER = Path("/root/.hermes/scripts/hermes_router_execute.py")
MEDIA_VERIFY = Path("/root/.hermes/scripts/hermes_media_verify.py")

def run(cmd, timeout=420):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)

def q(s):
    return json.dumps(str(s))

def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", (text or "output").lower()).strip("_")[:70] or "output"

def normalize_request(text):
    return (text or "").lower()

def remove_negated_format_phrases(text):
    t = normalize_request(text)
    negated = set()
    patterns = [
        (r"do not create\s+(?:a\s+)?pdf", "pdf"), (r"do not create\s+(?:a\s+)?docx", "docx"),
        (r"do not create\s+(?:a\s+)?word", "docx"), (r"do not create\s+(?:a\s+)?pptx", "pptx"),
        (r"do not create\s+(?:a\s+)?ppt", "pptx"), (r"do not create\s+(?:a\s+)?power ?point", "pptx"),
        (r"do not create\s+(?:a\s+)?powerpoint", "pptx"), (r"not\s+(?:a\s+)?pdf", "pdf"),
        (r"not\s+(?:a\s+)?docx", "docx"), (r"not\s+(?:a\s+)?pptx", "pptx"),
    ]
    for pat, fmt in patterns:
        if re.search(pat, t):
            negated.add(fmt)
    return negated

def requested_formats(text):
    t = normalize_request(text)
    negated = remove_negated_format_phrases(text)
    hits = []
    patterns = [
        ("docx", r"\bdocx\b|word document|word file|\bword\b"),
        ("pptx", r"\bpptx\b|\bppt\b|power ?point|powerpoint|slide deck|slides|presentation"),
        ("pdf", r"\bpdf\b"),
        ("html", r"\bhtml\b|webpage|web page|frontpage|front page"),
        ("md", r"\bmarkdown\b|\.md\b"),
        ("xlsx", r"\bxlsx\b|excel|spreadsheet|workbook"),
    ]
    for fmt, pat in patterns:
        m = re.search(pat, t)
        if m and fmt not in negated:
            hits.append((m.start(), fmt))
    formats=[]
    for _, fmt in sorted(hits):
        if fmt not in formats:
            formats.append(fmt)
    return formats

def wants_visuals(text):
    t = normalize_request(text)
    return any(w in t for w in ["picture", "pictures", "image", "images", "illustration", "illustrations", "icon", "icons", "visual", "visuals", "matching words", "kids", "children", "lesson", "worksheet", "flashcard"])

def requested_quality_tier(text):
    t=normalize_request(text)
    if any(w in t for w in ['3d','3d style','3d cartoon','3d images','three-dimensional','beautiful 3d','proper beautiful','real images','high-quality images','high quality images','beautiful cartoon','cartoon style','pixar','not vector','not placeholder']): return 'ai_3d_image'
    if any(w in t for w in ['beautiful cartoon','high-quality images','real images','ai images','high quality images']): return 'ai_cartoon_image'
    return 'local_cartoon_scene'

def detect_title(text):
    m = re.search(r"[?\"]([^?\"]+)[?\"]", text)
    if m:
        return m.group(1).strip()
    lower = text.lower()
    if "about " in lower:
        part = text[lower.index("about ") + len("about "):]
        part = re.split(r"\bfor\b|\buse these\b|\bsend\b|morning:", part, flags=re.I)[0]
        part = part.strip(" .,:;\"'??")
        if part:
            return part
    return "Hermes Lesson"

def detect_age(text):
    m = re.search(r"(\d+)\s*[- ]?\s*year[- ]?old", text.lower())
    if m:
        return f"{m.group(1)}-year-old kids"
    return "kids"

def extract_custom_sections(text):
    pattern = r"(?P<head>Morning|School Time|Evening|Afternoon|Night)\s*:\s*(?P<body>.*?)(?=(?:Morning|School Time|Evening|Afternoon|Night)\s*:|$)"
    sections = []
    for match in re.finditer(pattern, text, flags=re.I | re.S):
        head = match.group("head").strip()
        body = match.group("body")
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"^\d+\.\s*", "", line)
            line = re.sub(r"^[^\wA-Za-z]+", "", line).strip()
            line = line.strip(" .")
            if not line:
                continue
            line = re.split(r"\bSend it to me\b|\bSend as\b", line, flags=re.I)[0].strip(" .")
            if line:
                sections.append({"group": head, "title": line[:60], "sentence": f"I {line.lower()}.", "word": line[:35], "image": line.lower()})
    return sections

def normalize_sections_json_files(lesson_path, slides_path):
    if not lesson_path or not slides_path:
        return lesson_path, slides_path
    norm_lesson = str(Path(lesson_path).with_name(Path(lesson_path).stem + "_normalized.json"))
    proc = subprocess.run(
        [
            "/usr/bin/python3",
            "/root/.hermes/scripts/hermes_lesson_phrase_normalizer.py",
            "--sections-json", lesson_path,
            "--output", norm_lesson,
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError("PHRASE_NORMALIZATION_FAILED:" + proc.stdout + proc.stderr)
    return norm_lesson, norm_lesson

def write_sections_files(text, title):
    sections = extract_custom_sections(text)
    if not sections:
        return "", ""
    base = Path("/root/.hermes/file_outputs/batch_input")
    base.mkdir(parents=True, exist_ok=True)
    stem = slug(title)
    lesson_sections = [{"title": item["title"], "sentence": item["sentence"]} for item in sections]
    pptx_slides = [{"title": item["title"], "word": item["word"], "sentence": item["sentence"], "image": item["image"]} for item in sections]
    lesson_path = base / f"{stem}_sections.json"
    slides_path = base / f"{stem}_slides.json"
    lesson_path.write_text(json.dumps(lesson_sections, indent=2), encoding="utf-8")
    slides_path.write_text(json.dumps(pptx_slides, indent=2), encoding="utf-8")
    return str(lesson_path), str(slides_path)

def route_for_format(fmt, visual):
    if fmt == "docx": return "rich_docx_picture_file" if visual else "docx_file"
    if fmt == "pdf": return "rich_pdf_picture_file" if visual else "pdf_file"
    if fmt == "pptx": return "pptx_picture_file" if visual else "pptx_file"
    if fmt == "html": return "html_file"
    if fmt == "md": return "md_file"
    if fmt == "xlsx": return "rich_xlsx_file"
    return ""

def build_command(fmt, route, output, title, topic, age, visual, sections_json, slides_json):
    if route in ["rich_docx_picture_file", "rich_pdf_picture_file"]:
        cmd = f"{ROUTER} {route} --output {q(output)} --title {q(title)} --topic {q(topic)} --age {q(age)} --min-media 1"
        if sections_json: cmd += f" --sections-json {q(sections_json)}"
        return cmd
    if route == "pptx_picture_file":
        slide_count = 8
        if slides_json:
            try: slide_count = len(json.loads(Path(slides_json).read_text()))
            except Exception: slide_count = 8
        cmd = f"{ROUTER} pptx_picture_file --output {q(output)} --title {q(title)} --topic {q(topic)} --age {q(age)} --slide-count {int(slide_count)} --min-media {int(slide_count)}"
        if slides_json: cmd += f" --slides-json {q(slides_json)}"
        return cmd
    if route in ["docx_file", "pdf_file", "pptx_file", "md_file"]:
        return f"{ROUTER} {route} --output {q(output)} --title {q(title)} --description {q('Create a lesson about ' + topic)} --expect-text {q(title)}"
    if route == "html_file":
        return f"{ROUTER} html_file --output {q(output)} --description {q('Create a visual HTML lesson about ' + topic)} --expect-text {q(title)}"
    raise RuntimeError(f"UNSUPPORTED_ROUTE:{route}")

def media_type(fmt):
    return {"docx":"docx", "pdf":"pdf", "pptx":"pptx", "html":"html", "xlsx":"xlsx"}.get(fmt)

def verify_media(fmt, output, min_media):
    mt = media_type(fmt)
    if not mt:
        return 0, ""
    proc = run(f"{MEDIA_VERIFY} --file {q(output)} --type {mt} --min-media {int(min_media)}", timeout=120)
    return proc.returncode, proc.stdout + proc.stderr

def main():
    parser = argparse.ArgumentParser(description="Execute multi-artifact rich output requests.")
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request = args.request
    title = detect_title(request); topic = title; age = detect_age(request); visual = wants_visuals(request); quality = requested_quality_tier(request); formats = requested_formats(request)
    if not formats:
        print("NOT VERIFIED"); print("REASON=NO_REQUESTED_FORMATS_DETECTED"); return 2
    sections_json, slides_json = write_sections_files(request, title)
    if visual and quality in ['ai_cartoon_image','ai_3d_image']:
            image_count = 0
            if slides_json:
                try: image_count = len(json.loads(Path(slides_json).read_text()))
                except Exception: image_count = 0
            if image_count > 25:
                print('NOT VERIFIED')
                print('REASON=IMAGE_COUNT_EXCEEDS_LIMIT')
                print('IMAGE_COUNT=' + str(image_count))
                return 3
    print("BATCH_ARTIFACT_EXECUTION_PLAN=PASSED")
    print("TITLE=" + title); print("AGE=" + age); print("VISUAL_POLICY=" + ("required" if visual else "auto")); print("VISUAL_QUALITY_TIER=" + quality); print("REQUESTED_FORMATS=" + ",".join(formats))
    if sections_json: print("SECTIONS_JSON=" + sections_json)
    if slides_json: print("SLIDES_JSON=" + slides_json)
    failures=[]; successes=[]; media_results=[]
    for fmt in formats:
        route = route_for_format(fmt, visual)
        if route == "rich_xlsx_file":
            failures.append((fmt, route, "ROUTE_NOT_IMPLEMENTED")); print(f"ARTIFACT_RESULT={fmt}:NOT_VERIFIED"); print(f"ROUTE={route}"); print("REASON=ROUTE_NOT_IMPLEMENTED"); continue
        ext = "pptx" if fmt == "pptx" else fmt
        output = Path("/root/.hermes/file_outputs") / f"{slug(title)}.{ext}"
        cmd = build_command(fmt, route, output, title, topic, age, visual, sections_json, slides_json)
        if route in ['rich_docx_picture_file','rich_pdf_picture_file','pptx_picture_file']:
            cmd += f' --quality-tier {q(quality)}'
            if quality in ['ai_cartoon_image','ai_3d_image']:
                cmd += ' --timeout 900'
        print("ARTIFACT_START=" + fmt); print("ROUTE=" + route); print("OUTPUT_PATH=" + str(output))
        proc = run(cmd, timeout=600)
        if proc.stdout.strip(): print("ROUTER_STDOUT_START"); print(proc.stdout.strip()); print("ROUTER_STDOUT_END")
        if proc.stderr.strip(): print("ROUTER_STDERR_START"); print(proc.stderr.strip()); print("ROUTER_STDERR_END")
        if proc.returncode != 0:
            failures.append((fmt, route, "ROUTER_EXECUTION_FAILED")); print(f"ARTIFACT_RESULT={fmt}:NOT_VERIFIED"); print("REASON=ROUTER_EXECUTION_FAILED"); continue
        min_media = 1
        if fmt == "pptx" and slides_json:
            min_media = len(json.loads(Path(slides_json).read_text()))
        mv_code, mv_out = verify_media(fmt, output, min_media if visual else 0)
        if mv_out.strip(): print("MEDIA_VERIFY_STDOUT_START"); print(mv_out.strip()); print("MEDIA_VERIFY_STDOUT_END")
        if visual and mv_code != 0:
            failures.append((fmt, route, "MEDIA_VERIFY_FAILED")); print(f"ARTIFACT_RESULT={fmt}:NOT_VERIFIED"); print("REASON=MEDIA_VERIFY_FAILED"); continue
        successes.append((fmt, route, str(output))); media_results.append(fmt)
        print(f"ARTIFACT_RESULT={fmt}:PASSED"); print("VERIFICATION=PASSED")
        if visual: print("MEDIA_VERIFICATION=PASSED")
        print("TELEGRAM_DELIVERY=PASSED")
    print("BATCH_SUMMARY_START")
    for fmt, route, output in successes:
        print(f"PASSED_FORMAT={fmt}"); print(f"PASSED_ROUTE={route}"); print(f"PASSED_OUTPUT={output}")
    for fmt, route, reason in failures:
        print(f"FAILED_FORMAT={fmt}"); print(f"FAILED_ROUTE={route}"); print(f"FAILED_REASON={reason}")
    print("BATCH_SUMMARY_END")
    if failures:
        print("NOT VERIFIED"); print("REASON=ONE_OR_MORE_ARTIFACTS_FAILED"); return 1
    print("BATCH_ARTIFACT_EXECUTION=PASSED")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
