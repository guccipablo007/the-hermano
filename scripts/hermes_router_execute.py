#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import time
from pathlib import Path

MODEL_CALL = Path("/root/.hermes/scripts/hermes_model_call.py")
VERIFY = Path("/root/.hermes/scripts/hermes_verify.py")
LOG_DIR = Path("/root/.hermes/model_routing/logs")

def run(cmd, timeout=180):
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr

def strip_markdown_fences(text):
    s = text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return s

def extract_python_code(content):
    content = content.strip()
    m = re.search(r"```(?:python|py)?\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip() + "\n"
    cleaned = strip_markdown_fences(content)
    idx = cleaned.find("#!/usr/bin/env python")
    if idx > 0:
        cleaned = cleaned[idx:]
    python_markers = ["import ", "from ", "def ", "if __name__", "print(", "argparse"]
    if any(x in cleaned for x in python_markers):
        lines = cleaned.splitlines()
        start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped.startswith("#!")
                or stripped.startswith("#")
                or stripped.startswith("import ")
                or stripped.startswith("from ")
                or stripped.startswith("def ")
                or stripped.startswith("print(")
                or stripped.startswith("if __name__")
            ):
                start = i
                break
        candidate = "\n".join(lines[start:]).strip() + "\n"
        bad_prefixes = ("$", "python ", "python3 ", "cat ", "EOF", "chmod ", "ls ", "-lah", ">", "Then ", "Let's ", "Okay")
        filtered = []
        for line in candidate.splitlines():
            if line.strip().startswith(bad_prefixes):
                continue
            filtered.append(line)
        return "\n".join(filtered).strip() + "\n"
    return ""

def extract_html(content):
    content = content.strip()
    fenced = re.search(r"```(?:html)?\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1).strip()
    else:
        candidate = strip_markdown_fences(content)
    doctype_index = candidate.lower().find("<!doctype html")
    html_index = candidate.lower().find("<html")
    if doctype_index >= 0:
        candidate = candidate[doctype_index:]
    elif html_index >= 0:
        candidate = candidate[html_index:]
    close_index = candidate.lower().rfind("</html>")
    if close_index >= 0:
        candidate = candidate[:close_index + len("</html>")]
    return candidate.strip() + "\n"

def validate_html(html, expect_text=None):
    lower = html.lower()
    required = ["<!doctype html", "<html", "<head", "<body"]
    missing = [x for x in required if x not in lower]
    if missing:
        return False, "MISSING_HTML_TAGS=" + ",".join(missing)
    if len(html.strip()) < 300:
        return False, "HTML_TOO_SHORT"
    if expect_text and expect_text not in html:
        return False, "EXPECTED_TEXT_MISSING"
    text_without_tags = re.sub(r"<[^>]+>", " ", html)
    visible_words = [w for w in re.split(r"\s+", text_without_tags.strip()) if w]
    if len(visible_words) < 10:
        return False, "TOO_LITTLE_VISIBLE_TEXT"
    return True, "HTML_VALID"

def call_worker(route, prompt, max_tokens=1800):
    cmd = f"{MODEL_CALL} --route {route} --prompt {json.dumps(prompt)} --max-tokens {max_tokens} --json"
    rc, out, err = run(cmd, timeout=240)
    if rc != 0:
        raise RuntimeError(f"MODEL_CALL_FAILED rc={rc}\nSTDOUT={out}\nSTDERR={err}")
    return json.loads(out)

def call_coder_python(description, output_path, attempt):
    strictness = "Return only valid Python code. No markdown. No explanation. No shell commands."
    if attempt == 2:
        strictness = "CRITICAL: Your previous answer was not raw code. Return ONLY executable Python code. No explanation, no markdown fences, no shell commands, no filename line."
    prompt = f"""
You are the Coding and Builder Worker.

Create a Python script for this exact file path:
{output_path}

Task:
{description}

Rules:
- Python only.
- {strictness}
"""
    return call_worker("coder", prompt, max_tokens=1200)

def call_coder_html(description, output_path, expect_text, attempt):
    strictness = "Return only complete HTML code. No markdown. No explanation. No shell commands."
    if attempt == 2:
        strictness = "CRITICAL: Your previous answer was not clean HTML. Return ONLY complete single-file HTML/CSS. No explanation, no markdown fences, no shell commands."
    prompt = f"""
You are the Coding and Builder Worker.

Create a complete single-file HTML/CSS page for this exact file path:
{output_path}

Task:
{description}

Required:
- Include <!DOCTYPE html>
- Include <html>, <head>, and <body>
- Use embedded CSS inside <style>
- Make it visually polished and readable
- Include responsive layout
- Include this exact visible text somewhere if relevant: {expect_text or ""}

Rules:
- {strictness}
"""
    return call_worker("coder", prompt, max_tokens=2200)





def rich_lesson_file(args):
    fmt = "pdf" if args.mode == "rich_pdf_picture_file" else "docx"
    cmd = (f"/usr/bin/python3 /root/.hermes/scripts/hermes_rich_lesson_builder.py --format {fmt} --output {json.dumps(args.output)} --title {json.dumps(args.title)} --topic {json.dumps(args.topic)} --age {json.dumps(args.age)} --min-media {int(args.min_media)}")
    if args.sections_json:
        cmd += f" --sections-json {json.dumps(args.sections_json)}"
    if getattr(args, "quality_tier", ""):
        cmd += f" --quality-tier {json.dumps(args.quality_tier)}"
    if getattr(args, "no_deliver_telegram", False): cmd += " --no-deliver-telegram"
    else: cmd += " --deliver-telegram"
    rc,out,err=run(cmd,timeout=args.timeout); print(out.strip())
    if err.strip(): print(err.strip())
    if rc!=0:
        print("NOT VERIFIED"); return rc
    return 0



def pptx_picture_file(args):
    cmd = (
        f"/usr/bin/python3 /root/.hermes/scripts/hermes_pptx_picture_builder.py "
        f"--output {json.dumps(args.output)} "
        f"--title {json.dumps(args.title)} "
        f"--topic {json.dumps(args.topic)} "
        f"--age {json.dumps(args.age)} "
        f"--slide-count {int(args.slide_count)} "
        f"--min-media {int(args.min_media)}"
    )
    if getattr(args, "quality_tier", ""):
        cmd += f" --quality-tier {json.dumps(args.quality_tier)}"
    if args.slides_json:
        cmd += f" --slides-json {json.dumps(args.slides_json)}"
    if getattr(args, "no_deliver_telegram", False):
        cmd += " --no-deliver-telegram"
    else:
        cmd += " --deliver-telegram"
    rc, out, err = run(cmd, timeout=args.timeout)
    print(out.strip())
    if err.strip(): print(err.strip())
    if rc != 0:
        print("NOT VERIFIED")
        return rc
    return 0


def flashcards_pdf(args):
    cmd = (f"/usr/bin/python3 /root/.hermes/scripts/hermes_flashcard_builder.py --output {json.dumps(args.output)} --title {json.dumps(args.title)} --theme {json.dumps(args.theme)} --age {json.dumps(args.age)}")
    if args.cards_json:
        cmd += f" --cards-json {json.dumps(args.cards_json)}"
    if getattr(args, "no_deliver_telegram", False):
        cmd += " --no-deliver-telegram"
    else:
        cmd += " --deliver-telegram"
    rc, out, err = run(cmd, timeout=args.timeout)
    print(out.strip())
    if err.strip(): print(err.strip())
    if rc != 0:
        print("NOT VERIFIED")
        return rc
    return 0

def document_file(args):
    output_path = Path(args.output)
    fmt = args.mode.replace("_file", "")
    cmd = (f"/usr/bin/python3 /root/.hermes/scripts/hermes_document_builder.py --format {fmt} --output {json.dumps(str(output_path))} --title {json.dumps(args.title)} --description {json.dumps(args.description)} --expect-text {json.dumps(args.expect_text or args.title)}")
    if getattr(args, "no_deliver_telegram", False):
        cmd += " --no-deliver-telegram"
    else:
        cmd += " --deliver-telegram"
    rc, out, err = run(cmd, timeout=args.timeout)
    print(out.strip())
    if err.strip(): print(err.strip())
    if rc != 0:
        print("NOT VERIFIED")
        return rc
    return 0

def deliver_file(args):
    file_path = Path(args.file)
    if not file_path.exists() or not file_path.is_file():
        print("NOT VERIFIED")
        print("REASON=FILE_NOT_FOUND")
        print("FILE=" + str(file_path))
        return 50
    preview = args.preview_link or "auto"
    caption = args.caption or ("Your Majesty, here is your verified file: " + file_path.name)
    deliver_cmd = (
        f"/root/.hermes/scripts/hermes_telegram_deliver.py "
        f"--file {json.dumps(str(file_path))} "
        f"--caption {json.dumps(caption)} "
        f"--preview-link {json.dumps(preview)}"
    )
    rc, d_out, d_err = run(deliver_cmd, timeout=args.timeout)
    print("ROUTE=deliver_file")
    print("OUTPUT_PATH=" + str(file_path))
    print("TELEGRAM_DELIVERY_OUTPUT_START")
    print(d_out.strip())
    if d_err.strip():
        print(d_err.strip())
    print("TELEGRAM_DELIVERY_OUTPUT_END")
    if rc != 0:
        print("NOT VERIFIED")
        print("TELEGRAM_DELIVERY=FAILED")
        return rc
    print("TELEGRAM_DELIVERY=PASSED")
    return 0


def write_log(mode, model_data, output_path, description, test_cmd, test_output, verification_output):
    ts = time.strftime("%Y%m%d_%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"router_execute_{ts}_{mode}.json"
    log_path.write_text(json.dumps({
        "mode": mode,
        "route": "coder",
        "worker_model": model_data.get("model") if model_data else None,
        "output_path": str(output_path),
        "description": description,
        "test_cmd": test_cmd,
        "test_output": test_output,
        "verification_output": verification_output,
        "model_call_log_path": model_data.get("log_path") if model_data else None,
    }, indent=2))
    return log_path

def coder_file(args):
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    last_data = None
    code = ""
    for attempt in [1, 2]:
        data = call_coder_python(args.description, output_path, attempt)
        last_data = data
        code = extract_python_code(data.get("content", ""))
        if code and "print(" in code:
            break
    if not code:
        print("NOT VERIFIED")
        print("REASON=NO_VALID_PYTHON_CODE_EXTRACTED")
        return 20
    output_path.write_text(code)
    output_path.chmod(0o700)
    rc, out, err = run(f"python3 -m py_compile {output_path}")
    if rc != 0:
        print("NOT VERIFIED")
        print("REASON=PY_COMPILE_FAILED")
        print(err)
        return rc
    rc, test_out, test_err = run(args.test_cmd, timeout=args.timeout)
    if rc != 0:
        print("NOT VERIFIED")
        print("REASON=TEST_COMMAND_FAILED")
        print("TEST_STDOUT=" + test_out.strip())
        print("TEST_STDERR=" + test_err.strip())
        return rc
    if args.expect_output and args.expect_output not in test_out:
        print("NOT VERIFIED")
        print("REASON=EXPECTED_OUTPUT_MISSING")
        print("EXPECTED=" + args.expect_output)
        print("TEST_STDOUT=" + test_out.strip())
        return 30
    verify_cmd = f"{VERIFY} script --path {output_path} --test-cmd {json.dumps(args.test_cmd)}"
    rc, verify_out, verify_err = run(verify_cmd, timeout=args.timeout)
    if rc != 0:
        print("NOT VERIFIED")
        print("REASON=HERMES_VERIFY_FAILED")
        print(verify_out)
        print(verify_err)
        return rc
    log_path = write_log("coder_file", last_data, output_path, args.description, args.test_cmd, test_out, verify_out)
    print("ROUTE=coder")
    print("WORKER_MODEL=" + str(last_data.get("model")))
    print("OUTPUT_PATH=" + str(output_path))
    print("TEST_OUTPUT=" + test_out.strip())
    print("VERIFICATION=PASSED")
    print("LOG_PATH=" + str(log_path))
    return 0

def html_file(args):
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    last_data = None
    html = ""
    for attempt in [1, 2]:
        data = call_coder_html(args.description, output_path, args.expect_text, attempt)
        last_data = data
        html = extract_html(data.get("content", ""))
        ok, reason = validate_html(html, args.expect_text)
        if ok:
            break
    ok, reason = validate_html(html, args.expect_text)
    if not ok:
        print("NOT VERIFIED")
        print("REASON=" + reason)
        if last_data:
            print("MODEL_CONTENT_PREVIEW=" + (last_data.get("content", "")[:700]).replace("\n", "\\n"))
        return 40
    output_path.write_text(html)
    output_path.chmod(0o644)
    rc, verify_out, verify_err = run(f"{VERIFY} file --path {output_path}", timeout=args.timeout)
    if rc != 0:
        print("NOT VERIFIED")
        print("REASON=HERMES_VERIFY_FILE_FAILED")
        print(verify_out)
        print(verify_err)
        return rc
    lower = html.lower()
    checks = [("DOCTYPE", "<!DOCTYPE html"), ("HTML_TAG", "<html"), ("HEAD_TAG", "<head"), ("BODY_TAG", "<body")]
    for name, token in checks:
        if token.lower() not in lower:
            print("NOT VERIFIED")
            print(f"REASON={name}_MISSING")
            return 41
    if args.expect_text and args.expect_text not in html:
        print("NOT VERIFIED")
        print("REASON=EXPECTED_TEXT_MISSING_AFTER_SAVE")
        return 42
    log_path = write_log("html_file", last_data, output_path, args.description, None, "HTML_FILE_CREATED", verify_out)
    print("ROUTE=coder")
    print("WORKER_MODEL=" + str(last_data.get("model")))
    print("OUTPUT_PATH=" + str(output_path))
    print("EXPECT_TEXT=" + str(args.expect_text or ""))
    print("VERIFICATION=PASSED")
    print("LOG_PATH=" + str(log_path))
    should_deliver = not getattr(args, "no_deliver_telegram", False) or getattr(args, "deliver_telegram", False)
    if should_deliver:
        deliver_cmd = f"/root/.hermes/scripts/hermes_telegram_deliver.py --file {json.dumps(str(output_path))} --caption {json.dumps('Your Majesty, here is your verified HTML output: ' + output_path.name)} --preview-link auto"
        rc, d_out, d_err = run(deliver_cmd, timeout=180)
        print("TELEGRAM_DELIVERY_OUTPUT_START")
        print(d_out.strip())
        if d_err.strip():
            print(d_err.strip())
        print("TELEGRAM_DELIVERY_OUTPUT_END")
        if rc != 0:
            print("TELEGRAM_DELIVERY=FAILED")
            return rc
    return 0

def main():
    parser = argparse.ArgumentParser(description="Deterministic Hermes router executor.")
    sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("coder_file")
    p.add_argument("--output", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--test-cmd", required=True)
    p.add_argument("--expect-output")
    p.add_argument("--timeout", type=int, default=120)
    h = sub.add_parser("html_file")
    h.add_argument("--output", required=True)
    h.add_argument("--description", required=True)
    h.add_argument("--expect-text")
    h.add_argument("--timeout", type=int, default=120)
    h.add_argument("--deliver-telegram", action="store_true")
    h.add_argument("--no-deliver-telegram", action="store_true")

    d = sub.add_parser("deliver_file")
    d.add_argument("--file", required=True)
    d.add_argument("--caption", default="")
    d.add_argument("--preview-link", choices=["yes", "no", "auto"], default="auto")
    d.add_argument("--timeout", type=int, default=120)




    for rich_mode in ["rich_pdf_picture_file", "rich_docx_picture_file"]:
        rich = sub.add_parser(rich_mode)
        rich.add_argument("--output", required=True)
        rich.add_argument("--title", required=True)
        rich.add_argument("--topic", default="")
        rich.add_argument("--age", default="kids")
        rich.add_argument("--sections-json", default="")
        rich.add_argument("--min-media", type=int, default=1)
        rich.add_argument("--timeout", type=int, default=240)
        rich.add_argument("--quality-tier", default="local_cartoon_scene")
        rich.add_argument("--no-deliver-telegram", action="store_true")

    pic = sub.add_parser("pptx_picture_file")
    pic.add_argument("--output", required=True)
    pic.add_argument("--title", required=True)
    pic.add_argument("--topic", default="")
    pic.add_argument("--age", default="kids")
    pic.add_argument("--slide-count", type=int, default=8)
    pic.add_argument("--slides-json", default="")
    pic.add_argument("--min-media", type=int, default=1)
    pic.add_argument("--timeout", type=int, default=300)
    pic.add_argument("--quality-tier", default="local_cartoon_scene")
    pic.add_argument("--no-deliver-telegram", action="store_true")

    f = sub.add_parser("flashcards_pdf")
    f.add_argument("--output", required=True)
    f.add_argument("--title", required=True)
    f.add_argument("--theme", default="mothers_day")
    f.add_argument("--age", default="3-4")
    f.add_argument("--cards-json", default="")
    f.add_argument("--timeout", type=int, default=240)
    f.add_argument("--no-deliver-telegram", action="store_true")

    for mode_name in ["pdf_file", "docx_file", "md_file", "pptx_file"]:
        doc_parser = sub.add_parser(mode_name)
        doc_parser.add_argument("--output", required=True)
        doc_parser.add_argument("--title", required=True)
        doc_parser.add_argument("--description", required=True)
        doc_parser.add_argument("--expect-text", default="")
        doc_parser.add_argument("--timeout", type=int, default=240)
        doc_parser.add_argument("--no-deliver-telegram", action="store_true")

    args = parser.parse_args()
    if args.mode == "coder_file":
        return coder_file(args)
    if args.mode == "html_file":
        return html_file(args)
    if args.mode == "deliver_file":
        return deliver_file(args)
    if args.mode in ["pdf_file", "docx_file", "md_file", "pptx_file"]:
        return document_file(args)
    if args.mode == "flashcards_pdf":
        return flashcards_pdf(args)
    if args.mode == "pptx_picture_file":
        return pptx_picture_file(args)
    if args.mode in ["rich_pdf_picture_file", "rich_docx_picture_file"]:
        return rich_lesson_file(args)
    print("UNKNOWN_MODE")
    return 99

if __name__ == "__main__":
    raise SystemExit(main())
