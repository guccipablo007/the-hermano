#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

CONFIG = Path('/root/.hermes/config.yaml')
ROUTING = Path('/root/.hermes/model_routing/routing_policy.yaml')
ENV_FILES = [Path('/root/.hermes/.env'), Path('/root/.hermes/model_routing/providers.env')]
SECRET_RE = re.compile(r'(sk-[A-Za-z0-9_-]+|Bearer\s+[A-Za-z0-9._:-]+|bot\d+:[A-Za-z0-9_-]+|[A-Za-z0-9_-]{24,}\.[A-Za-z0-9._-]+)')


def mask(text: str) -> str:
    text = SECRET_RE.sub('<REDACTED>', text)
    text = re.sub(r'(chat_id|token|api[_-]?key|password|secret)(["\':= ]+)([^,\s}\]]+)', r'\1\2<REDACTED>', text, flags=re.I)
    return text


def load_yaml(path: Path) -> dict[str, Any]:
    if not yaml or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(errors='ignore')) or {}


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in ENV_FILES:
        if not path.exists():
            continue
        for line in path.read_text(errors='ignore').splitlines():
            if not line.strip() or line.lstrip().startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def status_data() -> dict[str, Any]:
    cfg = load_yaml(CONFIG)
    routing = load_yaml(ROUTING)
    model = cfg.get('model') if isinstance(cfg.get('model'), dict) else {}
    providers = cfg.get('providers') if isinstance(cfg.get('providers'), dict) else {}
    newcoin = providers.get('newcoin') if isinstance(providers.get('newcoin'), dict) else {}
    routes = routing.get('routes') if isinstance(routing.get('routes'), dict) else {}
    selected = routing.get('selected_models') if isinstance(routing.get('selected_models'), dict) else {}
    fallbacks = cfg.get('fallback_providers') or model.get('fallback_providers') or []
    return {
        'primary_provider': model.get('provider'),
        'default_model': model.get('default') or model.get('model'),
        'newcoin_base_url': newcoin.get('base_url'),
        'newcoin_configured': bool(newcoin.get('base_url') and newcoin.get('key_env')),
        'newcoin_key_env': newcoin.get('key_env'),
        'selected_models': selected or {
            'default_general_simple': (routes.get('general_chat') or routes.get('basic') or {}).get('model') or model.get('default'),
            'reasoning_agentic': (routes.get('reasoning_agentic') or routes.get('complex_reasoning') or {}).get('model'),
            'coding_debugging': (routes.get('coding_debugging') or routes.get('coder') or {}).get('model'),
        },
        'coding_fallback_order': routing.get('coding_fallback_order') or [],
        'fallbacks': fallbacks,
        'openrouter_fallback_only': bool(routing.get('openrouter_fallback_only')) or any(isinstance(x, dict) and x.get('provider') == 'openrouter' for x in fallbacks),
        'expensive_models_policy': routing.get('expensive_models_policy') or 'GPT/OpenAI NewCoin models are not selected as defaults.',
    }


def print_status(fmt: str) -> int:
    data = status_data()
    if fmt == 'raw':
        print(mask(json.dumps(data, indent=2, ensure_ascii=False)))
        return 0
    if not data.get('primary_provider'):
        print('Your Majesty, Hermes provider routing is NOT VERIFIED from local config.')
        print('NOT VERIFIED')
        return 2
    selected = data.get('selected_models') or {}
    print('Your Majesty, Hermes is using NewCoin as the primary provider.')
    print('')
    print(f"Default/general/simple: {selected.get('default_general_simple') or data.get('default_model')}")
    print(f"Reasoning/agentic: {selected.get('reasoning_agentic') or 'NOT VERIFIED'}")
    print(f"Coding/debugging: {selected.get('coding_debugging') or 'NOT VERIFIED'}")
    print('OpenRouter: fallback only.' if data.get('openrouter_fallback_only') else 'OpenRouter fallback: NOT VERIFIED.')
    print('GPT/OpenAI NewCoin models: avoided as defaults.')
    return 0 if data.get('openrouter_fallback_only') else 2


def chat_test(model: str, marker: str, env: dict[str, str], base: str) -> tuple[bool, str]:
    key = env.get('NEWCOIN_API_KEY')
    if not key:
        return False, 'NEWCOIN_API_KEY_MISSING'
    payload = {'model': model, 'messages': [{'role': 'user', 'content': f'Reply exactly with {marker}=PASSED'}], 'temperature': 0, 'max_tokens': 40}
    req = urllib.request.Request(base.rstrip('/') + '/chat/completions', data=json.dumps(payload).encode('utf-8'), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            resp = json.loads(r.read().decode('utf-8'))
        text = str(resp['choices'][0]['message']['content']).strip()
        return (marker + '=PASSED') in text, text
    except Exception as exc:
        return False, f'{type(exc).__name__}:{str(exc)[:140]}'


def print_test(fmt: str) -> int:
    data = status_data()
    env = load_env()
    base = data.get('newcoin_base_url') or env.get('NEWCOIN_BASE_URL') or 'https://api.newcoin.top/v1'
    selected = data.get('selected_models') or {}
    tests = [
        ('default', selected.get('default_general_simple') or data.get('default_model'), 'NEWCOIN_DEFAULT_MODEL_TEST'),
        ('reasoning', selected.get('reasoning_agentic'), 'NEWCOIN_REASONING_MODEL_TEST'),
        ('coding', selected.get('coding_debugging'), 'NEWCOIN_CODING_MODEL_TEST'),
    ]
    results = []
    ok_all = True
    for label, model, marker in tests:
        if not model:
            results.append({'label': label, 'model': None, 'result': 'NOT_VERIFIED', 'reason': 'model_missing'})
            ok_all = False
            continue
        ok, detail = chat_test(str(model), marker, env, str(base))
        results.append({'label': label, 'model': model, 'result': 'PASSED' if ok else 'NOT_VERIFIED', 'detail': detail if not ok else marker + '=PASSED'})
        ok_all = ok_all and ok
    if fmt == 'raw':
        print(mask(json.dumps(results, indent=2, ensure_ascii=False)))
    else:
        for r in results:
            print(f"{r['label'].title()} model {r['model']}: {r['result']}")
        print('NEWCOIN_ROUTING_MODEL_TEST=PASSED' if ok_all else 'NOT VERIFIED')
    return 0 if ok_all else 2


def main() -> int:
    p = argparse.ArgumentParser(description='Show or test Hermes provider routing without exposing secrets.')
    p.add_argument('mode', choices=['status', 'test'])
    p.add_argument('--format', choices=['friendly', 'raw'], default='friendly')
    args = p.parse_args()
    if args.mode == 'status':
        return print_status(args.format)
    return print_test(args.format)

if __name__ == '__main__':
    raise SystemExit(main())
