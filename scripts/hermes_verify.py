#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None


def is_probably_binary(path: Path) -> bool:
    try:
        data = path.read_bytes()[:2048]
    except Exception:
        return False
    return b"\0" in data


def run_cmd(cmd, timeout=60):
    proc = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def verify_file(args):
    p = Path(args.path)
    if not p.exists():
        print(f"FILE_NOT_FOUND: {p}")
        return 2
    if not p.is_file():
        print(f"PATH_EXISTS_BUT_NOT_FILE: {p}")
        return 3

    st = p.stat()
    print(f"FILE_OK: {p}")
    print(f"SIZE_BYTES: {st.st_size}")

    if is_probably_binary(p):
        print("PREVIEW: BINARY_FILE_NOT_PRINTED")
        return 0

    print("PREVIEW_START")
    try:
        with p.open("r", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                if i > 40:
                    print("...PREVIEW_TRUNCATED_AFTER_40_LINES")
                    break
                print(f"{i}: {line.rstrip()}")
    except Exception as e:
        print(f"PREVIEW_ERROR: {e}")
        return 4
    print("PREVIEW_END")
    return 0


def verify_script(args):
    p = Path(args.path)
    if not p.exists() or not p.is_file():
        print(f"SCRIPT_NOT_FOUND: {p}")
        return 2

    print(f"SCRIPT_FOUND: {p}")
    print(f"SIZE_BYTES: {p.stat().st_size}")

    if p.suffix == ".py":
        rc, out, err = run_cmd(f"python3 -m py_compile {str(p)!r}")
        print("PY_COMPILE_STDOUT_START")
        print(out.rstrip())
        print("PY_COMPILE_STDOUT_END")
        print("PY_COMPILE_STDERR_START")
        print(err.rstrip())
        print("PY_COMPILE_STDERR_END")
        if rc != 0:
            print("PY_COMPILE_FAILED")
            return rc
        print("PY_COMPILE_OK")

    if args.test_cmd:
        print("TEST_CMD_START")
        print(args.test_cmd)
        print("TEST_CMD_END")
        rc, out, err = run_cmd(args.test_cmd, timeout=args.timeout)
        print("TEST_STDOUT_START")
        print(out.rstrip())
        print("TEST_STDOUT_END")
        print("TEST_STDERR_START")
        print(err.rstrip())
        print("TEST_STDERR_END")
        print(f"TEST_RETURN_CODE: {rc}")
        if rc != 0:
            print("TEST_FAILED")
            return rc
        print("TEST_OK")

    return 0


def verify_source_quote(args):
    p = Path(args.file)
    quote = args.quote
    if not p.exists() or not p.is_file():
        print(f"SOURCE_FILE_NOT_FOUND: {p}")
        return 2
    if not quote:
        print("QUOTE_EMPTY")
        return 3

    found = False
    print(f"SOURCE_FILE: {p}")
    print(f"QUOTE: {quote}")
    with p.open("r", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            if quote in line:
                found = True
                print(f"LINE {i}: {line.rstrip()}")

    if not found:
        print("NOT_VERIFIED")
        return 5

    print("QUOTE_VERIFIED")
    return 0


def verify_service(args):
    name = args.name
    rc, out, err = run_cmd(f"systemctl is-active {name!r}")
    active = out.strip()
    print(f"SERVICE: {name}")
    print(f"IS_ACTIVE: {active}")
    print("STATUS_START")
    rc2, out2, err2 = run_cmd(f"systemctl status {name!r} --no-pager -l | tail -n 40")
    print(out2.rstrip())
    if err2.strip():
        print(err2.rstrip())
    print("STATUS_END")
    if active != "active":
        print("SERVICE_NOT_ACTIVE")
        return 6
    print("SERVICE_ACTIVE")
    return 0


def verify_config(args):
    p = Path(args.path)
    if not p.exists() or not p.is_file():
        print(f"CONFIG_NOT_FOUND: {p}")
        return 2

    text = p.read_text(errors="replace")
    suffix = p.suffix.lower()

    try:
        if suffix in [".yaml", ".yml"]:
            if yaml is None:
                print("YAML_MODULE_MISSING")
                return 7
            yaml.safe_load(text)
            print(f"CONFIG_OK: {p}")
            print("FORMAT: YAML")
            return 0
        if suffix == ".json":
            json.loads(text)
            print(f"CONFIG_OK: {p}")
            print("FORMAT: JSON")
            return 0
        print(f"CONFIG_READABLE: {p}")
        print("FORMAT: UNKNOWN_TEXT")
        return 0
    except Exception as e:
        print(f"CONFIG_INVALID: {p}")
        print(f"ERROR: {e}")
        return 8


def main():
    parser = argparse.ArgumentParser(description="Hermes mechanical verification helper.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_file = sub.add_parser("file")
    p_file.add_argument("--path", required=True)

    p_script = sub.add_parser("script")
    p_script.add_argument("--path", required=True)
    p_script.add_argument("--test-cmd")
    p_script.add_argument("--timeout", type=int, default=60)

    p_quote = sub.add_parser("source_quote")
    p_quote.add_argument("--file", required=True)
    p_quote.add_argument("--quote", required=True)

    p_service = sub.add_parser("service")
    p_service.add_argument("--name", required=True)

    p_config = sub.add_parser("config")
    p_config.add_argument("--path", required=True)

    args = parser.parse_args()

    if args.mode == "file":
        return verify_file(args)
    if args.mode == "script":
        return verify_script(args)
    if args.mode == "source_quote":
        return verify_source_quote(args)
    if args.mode == "service":
        return verify_service(args)
    if args.mode == "config":
        return verify_config(args)

    print("UNKNOWN_MODE")
    return 99


if __name__ == "__main__":
    raise SystemExit(main())
