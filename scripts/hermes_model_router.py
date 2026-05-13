#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

CONFIG = Path('/root/.hermes/config.yaml')
POLICY = Path('/root/.hermes/model_routing/routing_policy.yaml')
DEFAULT_MODEL = 'qwen3-32b'
REASONING_MODEL = 'kimi-k2.6'
CODING_MODEL = 'deepseek-v3.2'
PROVIDER = 'NewCoin'
FALLBACK_PROVIDER = 'OpenRouter'

SECRET_RE = re.compile(r'(Bearer\s+[A-Za-z0-9._:-]+|bot\d+:[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|[A-Za-z0-9_-]{24,}\.[A-Za-z0-9._-]+)')

TOOL_RULES = [
    ('/btw', 'hermes_btw_handler', ['^/btw\b']),
    ('provider-status', 'hermes_provider_status', ['provider.*using', 'model.*using', 'what model', 'what provider', 'provider status']),
    ('reminder-lookup', 'hermes_reminder_lookup', ['show me all my reminders', 'list my reminders', 'what reminders', 'scheduled reminders', 'next .*reminder', 'when is my next .*reminder', 'reminder lookup']),
    ('healthcheck', 'hermes_ops_healthcheck', ['healthcheck', 'health check', 'ops health', 'gateway status', 'is hermes healthy']),
]

CODING_KEYWORDS = [
    'traceback', 'stack trace', 'exception', 'python', 'bash', 'shell', 'systemd', 'journalctl', 'logs', 'log output',
    'file path', '/root/', '/usr/local/', 'config.yaml', '.py', '.sh', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml',
    'gateway', 'router', 'script', 'function', 'class ', 'code block', 'debug this code', 'fix this code', 'implement',
    'database', 'firebase', 'firestore', 'sql', 'postgres', 'mysql', 'redis', 'docker', 'nginx', 'api error', 'http 500',
    'app bug', 'frontend', 'backend', 'deployment', 'cronjob_tools.py', 'scheduler.py', 'run.py', 'write code', 'edit file',
]

REASONING_KEYWORDS = [
    'why did', 'root cause', 'root-cause', 'what caused', 'diagnose', 'architecture', 'architect', 'planning', 'plan ',
    'multi-step', 'troubleshoot', 'troubleshooting', 'task decomposition', 'decompose', 'strategy', 'decision',
    'agent behavior', 'workflow design', 'system design', 'failure analysis', 'investigate', 'tradeoff', 'design a',
]

SIMPLE_KEYWORDS = [
    'write a short', 'short message', 'translate', 'rewrite', 'summarize briefly', 'simple explanation', 'explain simply',
    'normal chat', 'thank you', 'draft a message', 'what is', 'who is', 'define ', 'meaning of',
]


def mask(text: str) -> str:
    text = SECRET_RE.sub('<REDACTED>', text)
    text = re.sub(r'(chat_id|token|api[_-]?key|password|secret)(["\':= ]+)([^,\s}\]]+)', r'\1\2<REDACTED>', text, flags=re.I)
    return text


def load_yaml(path: Path) -> dict[str, Any]:
    if not yaml or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(errors='ignore')) or {}


def policy_models() -> dict[str, str]:
    policy = load_yaml(POLICY)
    selected = policy.get('selected_models') if isinstance(policy.get('selected_models'), dict) else {}
    cfg = load_yaml(CONFIG)
    model_cfg = cfg.get('model') if isinstance(cfg.get('model'), dict) else {}
    return {
        'default': selected.get('default_general_simple') or model_cfg.get('default') or DEFAULT_MODEL,
        'reasoning': selected.get('reasoning_agentic') or REASONING_MODEL,
        'coding': selected.get('coding_debugging') or CODING_MODEL,
    }


def fallbacks() -> list[dict[str, Any]]:
    policy = load_yaml(POLICY)
    cfg = load_yaml(CONFIG)
    fb = cfg.get('fallback_providers') or (cfg.get('model') or {}).get('fallback_providers') or []
    coding_fb = policy.get('coding_fallback_order') if isinstance(policy.get('coding_fallback_order'), list) else []
    return [{'provider': FALLBACK_PROVIDER, 'models': fb, 'coding_order': coding_fb}]


def contains_any(text: str, needles: list[str]) -> bool:
    return any(n in text for n in needles)


def match_tool(text: str) -> tuple[str, str] | None:
    for route, tool, patterns in TOOL_RULES:
        for pat in patterns:
            if re.search(pat, text, flags=re.I):
                return route, tool
    return None


def classify_message(message: str) -> dict[str, Any]:
    raw = message or ''
    low = raw.lower().strip()
    models = policy_models()
    tool = match_tool(low)
    if tool:
        route, tool_name = tool
        return {
            'route': 'tool',
            'tool_route': route,
            'tool': tool_name,
            'provider': PROVIDER,
            'model': models['default'],
            'model_use': 'formatting_only_if_needed',
            'reason': 'verified tool/script route matched before model guessing',
            'fallback_provider': FALLBACK_PROVIDER,
        }
    if contains_any(low, CODING_KEYWORDS) or re.search(r'```|\b(error|failed|failure)\b.*\b(line|trace|log|code)\b', low):
        return {
            'route': 'coding',
            'provider': PROVIDER,
            'model': models['coding'],
            'reason': 'coding/debugging signals matched',
            'fallback_provider': FALLBACK_PROVIDER,
            'fallback_order': fallbacks()[0]['coding_order'],
        }
    if contains_any(low, REASONING_KEYWORDS):
        return {
            'route': 'reasoning',
            'provider': PROVIDER,
            'model': models['reasoning'],
            'reason': 'multi-step reasoning/root-cause/planning signals matched',
            'fallback_provider': FALLBACK_PROVIDER,
        }
    return {
        'route': 'default',
        'provider': PROVIDER,
        'model': models['default'],
        'reason': 'default/simple route',
        'fallback_provider': FALLBACK_PROVIDER,
    }


def friendly(decision: dict[str, Any]) -> str:
    if decision.get('route') == 'tool':
        return (
            f"route=tool\n"
            f"tool={decision.get('tool')}\n"
            f"provider={decision.get('provider')}\n"
            f"model={decision.get('model')} only if formatting is needed\n"
            f"reason={decision.get('reason')}"
        )
    return (
        f"route={decision.get('route')}\n"
        f"provider={decision.get('provider')}\n"
        f"model={decision.get('model')}\n"
        f"fallback_provider={decision.get('fallback_provider')}\n"
        f"reason={decision.get('reason')}"
    )


def status(fmt: str) -> int:
    models = policy_models()
    data = {
        'tool_first': True,
        'provider': PROVIDER,
        'default_simple_model': models['default'],
        'reasoning_agentic_model': models['reasoning'],
        'coding_debugging_model': models['coding'],
        'fallback_provider': FALLBACK_PROVIDER,
        'openrouter_fallback_only': True,
        'future_nc': {'planned_only': True, 'examples': ['/nc code <task>', '/nc reason <task>', '/nc cheap <task>', '/nc status']},
    }
    if fmt == 'raw':
        print(mask(json.dumps(data, indent=2, ensure_ascii=False)))
    else:
        print('Hermes task-aware model router:')
        print(f"Tool-first routing: enabled")
        print(f"Default/simple: NewCoin {models['default']}")
        print(f"Reasoning/agentic: NewCoin {models['reasoning']}")
        print(f"Coding/debugging: NewCoin {models['coding']}")
        print('OpenRouter: fallback only')
        print('/nc: documented for future planning only, not implemented')
    return 0


def self_test(fmt: str) -> int:
    cases = [
        ('simple', 'write a short message to Mr Wang', 'default', DEFAULT_MODEL),
        ('simple_chat', 'tell me what CST means for me', 'default', DEFAULT_MODEL),
        ('reasoning', 'why did the reminder system hallucinate?', 'reasoning', REASONING_MODEL),
        ('architecture', 'make an architecture plan for safer routing', 'reasoning', REASONING_MODEL),
        ('traceback', 'fix this Python traceback: ValueError on line 12', 'coding', CODING_MODEL),
        ('systemd', 'debug these Linux systemd logs from hermes-gateway.service', 'coding', CODING_MODEL),
        ('app_db', 'fix my Firebase database app bug', 'coding', CODING_MODEL),
        ('reminder_tool', 'show me all my reminders', 'tool', DEFAULT_MODEL),
        ('btw_tool', '/btw what provider are you using now?', 'tool', DEFAULT_MODEL),
    ]
    ok = True
    results = []
    for name, text, expected_route, expected_model in cases:
        got = classify_message(text)
        models = policy_models()
        expected_model = {'default': models['default'], 'reasoning': models['reasoning'], 'coding': models['coding']}.get(expected_route, models['default'])
        passed = got.get('route') == expected_route and got.get('model') == expected_model
        if not passed:
            ok = False
        results.append({'case': name, 'result': 'PASSED' if passed else 'FAILED', 'expected_route': expected_route, 'actual_route': got.get('route'), 'expected_model': expected_model, 'actual_model': got.get('model'), 'tool': got.get('tool')})
    if fmt == 'raw':
        print(mask(json.dumps(results, indent=2, ensure_ascii=False)))
    else:
        for r in results:
            print(f"{r['case']}={r['result']} route={r['actual_route']} model={r['actual_model']}" + (f" tool={r['tool']}" if r.get('tool') else ''))
        print('MODEL_ROUTER_TEST=PASSED' if ok else 'NOT VERIFIED')
    return 0 if ok else 2


def main() -> int:
    p = argparse.ArgumentParser(description='Task-aware Hermes model router for NewCoin routes.')
    p.add_argument('--format', choices=['friendly', 'raw'], default='friendly')
    sub = p.add_subparsers(dest='cmd')
    c = sub.add_parser('classify')
    c.add_argument('message')
    c.add_argument('--format', choices=['friendly', 'raw'], default=None)
    s = sub.add_parser('status')
    s.add_argument('--format', choices=['friendly', 'raw'], default=None)
    t = sub.add_parser('test')
    t.add_argument('--format', choices=['friendly', 'raw'], default=None)
    args = p.parse_args()
    if getattr(args, 'format', None) is None:
        args.format = 'friendly'
    if args.cmd == 'classify':
        decision = classify_message(args.message)
        if args.format == 'raw':
            print(mask(json.dumps(decision, indent=2, ensure_ascii=False)))
        else:
            print(friendly(decision))
        return 0
    if args.cmd == 'status':
        return status(args.format)
    if args.cmd == 'test':
        return self_test(args.format)
    p.print_help()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
