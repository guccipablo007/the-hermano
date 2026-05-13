#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import hermes_model_router

AUDIT = Path('/root/.hermes/model_routing/live_route_audit.jsonl')
SCRIPTS = Path('/root/.hermes/scripts')

SECRET_RE = re.compile(r'(Bearer\s+[A-Za-z0-9._:-]+|bot\d+:[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]+|[A-Za-z0-9_-]{24,}\.[A-Za-z0-9._-]+)')
ROUTE_QUESTION_RE = re.compile(r'\b(which|what)\s+(route|model|provider)\b|\broute\s+will\s+you\s+use\b|\bmodel\s+would\s+you\s+use\b', re.I)
DEBUG_DETAIL_RE = re.compile(r'```|traceback:|stack trace|\bline\s+\d+\b|\berror:\s*\S+|journalctl|systemctl status|firebase.*(permission-denied|unavailable|error code)', re.I)


def mask(text: str) -> str:
    text = SECRET_RE.sub('<REDACTED>', text or '')
    text = re.sub(r'(chat_id|token|api[_-]?key|password|secret)(["\':= ]+)([^,\s}\]]+)', r'\1\2<REDACTED>', text, flags=re.I)
    text = re.sub(r'(-?\d{8,})', '<chat_id_masked>', text)
    return text


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        out = ((proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')).strip()
        return proc.returncode, mask(out)
    except Exception as exc:
        return 1, f'NOT VERIFIED\nREASON={type(exc).__name__}'


def audit(message: str, decision: dict[str, Any], direct: bool, tool: str | None = None) -> None:
    try:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'route': decision.get('route'),
            'provider': decision.get('provider'),
            'selected_model': decision.get('model'),
            'tool': tool or decision.get('tool'),
            'fallback_used': False,
            'direct_response': direct,
            'intent_snippet': mask((message or '').replace('\n', ' ')[:160]),
        }
        with AUDIT.open('a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + '\n')
    except Exception:
        pass


def reminder_args(message: str) -> list[str]:
    text = (message or '').strip()
    low = text.lower()
    if re.search(r'\b(show|list)\b.*\b(reminders|alerts)\b', low) or re.search(r'\bwhat\s+(reminders|alerts)\s+do\s+i\s+have\b', low):
        return ['list']
    m = re.search(r'when\s+is\s+my\s+next\s+(.+?)\s+(?:reminder|alert)\??$', text, re.I)
    if m:
        return ['next', m.group(1).strip()]
    m = re.search(r'next\s+(.+?)\s+(?:reminder|alert)', text, re.I)
    if m:
        return ['next', m.group(1).strip()]
    return ['list']


def recall_query(message: str) -> str:
    low = (message or '').lower()
    if 'reminder' in low and ('hallucinat' in low or 'failure' in low or 'before' in low):
        return 'reminder failure hallucinate verified root cause'
    if 'hermes' in low and ('hallucinat' in low or 'failure' in low):
        return 'Hermes failure hallucinate verified root cause'
    return message.strip() or 'Hermes previous failure'


def route_preview(decision: dict[str, Any], message: str) -> str:
    route = decision.get('route')
    model = decision.get('model')
    provider = decision.get('provider') or 'NewCoin'
    if route == 'coding':
        return (f'Your Majesty, this routes to coding/debugging.\n\n'
                f'Route: coding/debugging\nProvider: {provider}\nModel: {model}\n\n'
                f'Please send the exact error message, relevant logs, and the smallest code/config snippet that reproduces it. I will not inspect credentials or execute risky actions without verified need.')
    if route == 'reasoning':
        return (f'Your Majesty, this routes to reasoning/agentic analysis.\n\n'
                f'Route: reasoning/agentic\nProvider: {provider}\nModel: {model}')
    if route == 'default':
        return (f'Your Majesty, this routes to default/simple.\n\n'
                f'Route: default/simple\nProvider: {provider}\nModel: {model}')
    if route == 'tool':
        return (f'Your Majesty, this routes to a verified tool first.\n\n'
                f'Tool: {decision.get("tool")}\nProvider: {provider}\nModel: {model} only if formatting is needed')
    return 'NOT VERIFIED\nREASON=ROUTE_UNKNOWN'


def should_direct_for_debug(decision: dict[str, Any], message: str) -> bool:
    if decision.get('route') != 'coding':
        return False
    if ROUTE_QUESTION_RE.search(message or ''):
        return True
    # If the user only states there is a debugging problem, ask for evidence instead of guessing.
    return not DEBUG_DETAIL_RE.search(message or '')


def handle(message: str) -> dict[str, Any]:
    decision = hermes_model_router.classify_message(message or '')
    route = decision.get('route')
    tool = decision.get('tool')
    response = ''
    direct = False

    if route == 'tool':
        direct = True
        if tool == 'hermes_provider_status':
            _, response = run(['python3', str(SCRIPTS / 'hermes_provider_status.py'), 'status', '--format', 'friendly'], timeout=45)
        elif tool == 'hermes_reminder_lookup':
            args = reminder_args(message)
            cmd = ['python3', str(SCRIPTS / 'hermes_reminder_lookup.py'), *args, '--format', 'friendly']
            _, response = run(cmd, timeout=45)
        elif tool == 'hermes_btw_handler':
            text = message if (message or '').lstrip().lower().startswith('/btw') else '/btw ' + (message or '')
            _, response = run(['python3', str(SCRIPTS / 'hermes_btw_handler.py'), text], timeout=60)
        elif tool == 'hermes_session_recall':
            q = recall_query(message)
            _, response = run(['python3', str(SCRIPTS / 'hermes_btw_handler.py'), '/btw search ' + q], timeout=80)
            if response and 'NOT VERIFIED' not in response:
                response = 'Your Majesty, I checked local Hermes records first.\n\n' + response
            elif not response:
                response = 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'
        else:
            response = 'NOT VERIFIED\nREASON=UNKNOWN_TOOL_ROUTE'
    elif ROUTE_QUESTION_RE.search(message or '') or should_direct_for_debug(decision, message or ''):
        direct = True
        response = route_preview(decision, message or '')

    audit(message or '', decision, direct, tool=tool)
    return {'direct_response': direct, 'response': response.strip(), 'decision': decision}


def main() -> int:
    p = argparse.ArgumentParser(description='Live Telegram natural-language pre-router for Hermes.')
    p.add_argument('message')
    p.add_argument('--format', choices=['json', 'friendly'], default='json')
    args = p.parse_args()
    result = handle(args.message)
    if args.format == 'friendly':
        if result['direct_response']:
            print(result['response'])
        else:
            print(hermes_model_router.friendly(result['decision']))
    else:
        print(mask(json.dumps(result, indent=2, ensure_ascii=False)))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
