#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

import yaml

ROOT = Path("/root/.hermes")
ROUTING_DIR = ROOT / "model_routing"
POLICY_PATH = ROUTING_DIR / "routing_policy.yaml"
PROVIDERS_ENV = ROUTING_DIR / "providers.env"
AGENTS_DIR = ROUTING_DIR / "agents"
LOG_DIR = ROUTING_DIR / "logs"

AGENT_TEMPLATE_BY_ROUTE = {
    "basic": "basic_worker.md",
    "coder": "coder_worker.md",
    "complex_reasoning": "complex_architect_worker.md",
    "vision": "vision_worker.md",
    "source_verified_research": "source_verified_research_worker.md",
    "private_data": "private_data_worker.md",
}

def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value

def load_policy():
    if not POLICY_PATH.exists():
        raise SystemExit(f"ROUTING_POLICY_NOT_FOUND: {POLICY_PATH}")
    return yaml.safe_load(POLICY_PATH.read_text()) or {}

def read_prompt(args):
    if args.prompt_file:
        return Path(args.prompt_file).read_text(errors="ignore")
    if args.prompt:
        return args.prompt
    data = sys.stdin.read()
    if data.strip():
        return data
    raise SystemExit("NO_PROMPT_PROVIDED")

def route_config(policy, route):
    routes = policy.get("routes") or {}
    if route not in routes:
        raise SystemExit(f"UNKNOWN_ROUTE: {route}")
    return routes[route] or {}

def read_worker_template(route):
    filename = AGENT_TEMPLATE_BY_ROUTE.get(route)
    if not filename:
        raise SystemExit(f"NO_TEMPLATE_FOR_ROUTE: {route}")
    path = AGENTS_DIR / filename
    if not path.exists():
        raise SystemExit(f"WORKER_TEMPLATE_NOT_FOUND: {path}")
    return path.read_text(errors="ignore")

def call_newcoin(model, system_prompt, user_prompt, max_tokens):
    api_key = os.environ.get("NEWCOIN_API_KEY", "").strip()
    base_url = os.environ.get("NEWCOIN_BASE_URL", "").strip().rstrip("/")
    if not api_key:
        raise SystemExit("NEWCOIN_API_KEY_MISSING")
    if not base_url:
        raise SystemExit("NEWCOIN_BASE_URL_MISSING")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(json.dumps({"error": "HTTP_ERROR", "status": e.code, "body_preview": err_body[:500]}, indent=2))
    data = json.loads(body)
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})
    return {"status": status, "content": content, "usage": usage, "raw_id": data.get("id")}

def log_result(route, provider, model, prompt, result):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = LOG_DIR / f"model_call_{ts}_{route}.json"
    safe = {
        "timestamp": ts,
        "route": route,
        "provider": provider,
        "model": model,
        "prompt_preview": prompt[:500],
        "status": result.get("status"),
        "usage": result.get("usage"),
        "raw_id": result.get("raw_id"),
        "content": result.get("content"),
    }
    path.write_text(json.dumps(safe, indent=2, ensure_ascii=False))
    return path

def main():
    parser = argparse.ArgumentParser(description="Manual Hermes decentralized model route caller.")
    parser.add_argument("--route", required=True, help="Route name from routing_policy.yaml")
    parser.add_argument("--prompt", help="Prompt text")
    parser.add_argument("--prompt-file", help="Prompt file path")
    parser.add_argument("--max-tokens", type=int, default=800)
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()
    load_env_file(PROVIDERS_ENV)
    policy = load_policy()
    cfg = route_config(policy, args.route)
    provider = cfg.get("provider")
    model = cfg.get("model")
    if not provider or not model:
        raise SystemExit(f"ROUTE_PROVIDER_OR_MODEL_MISSING: {args.route}")
    if args.route == "private_data":
        raise SystemExit("PRIVATE_DATA_ROUTE_NOT_ACTIVE_YET")
    if provider != "newcoin":
        raise SystemExit(f"PROVIDER_NOT_SUPPORTED_BY_HELPER_YET: {provider}")
    user_prompt = read_prompt(args)
    worker_template = read_worker_template(args.route)
    system_prompt = (
        worker_template
        + "\n\n# Manual Route Test Context\n"
        + "You are being called through hermes_model_call.py for a manual route test. "
        + "Follow your worker rules. Do not claim tool execution unless tool output is provided. "
        + "Do not handle Gmail, YouTube analytics/account data, secrets, or credentials."
    )
    result = call_newcoin(model, system_prompt, user_prompt, args.max_tokens)
    log_path = log_result(args.route, provider, model, user_prompt, result)
    output = {
        "route": args.route,
        "provider": provider,
        "model": model,
        "status": result["status"],
        "log_path": str(log_path),
        "usage": result.get("usage"),
        "content": result.get("content", "").strip(),
    }
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"ROUTE={args.route}")
        print(f"PROVIDER={provider}")
        print(f"MODEL={model}")
        print(f"STATUS={result['status']}")
        print(f"LOG_PATH={log_path}")
        print("")
        print(output["content"])

if __name__ == "__main__":
    main()
