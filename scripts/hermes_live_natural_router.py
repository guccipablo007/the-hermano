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
AGENT_PREVIEW_RE = re.compile(
    r'\b(which|what)\s+agent\b|\bwho\s+(would\s+)?handle(s)?\b|'
    r'\bwhich\s+part\s+of\s+hermes\s+handles\b|\bagent\s+would\s+handle\b|'
    r'\bwhat\s+agents\s+do\s+you\s+have\b|\bshow\s+(recent\s+)?delegated\s+tasks\b|'
    r'\bshow\s+agent\s+tasks\b|\bdelegated\s+task\s+status\b|\blist\s+agents\b|'
    r'\bwhich\s+agent\s+handles\b',
    re.I,
)
AGENT_EXECUTION_RE = re.compile(
    r'\b(delegate|agent)\b.*\b(run|execute|start|fix|patch|edit|create|restart|deploy|change)\b|'
    r'\b(run|execute|start)\b.*\b(agent|delegated\s+task)\b',
    re.I,
)


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



def parse_key_values(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in (text or '').splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip()
    return data


def agent_list_response() -> str:
    return (
        'Your Majesty, Hermes has exactly four agents:\n\n'
        '- Hermes Overseer / Main Agent\n'
        '- Apps, Coding & Complex Builds Agent\n'
        '- Ops & Verification Agent\n'
        '- Personal/Admin & Tutor Agent\n\n'
        'No additional specialist agents are enabled.'
    )


def delegated_status_response() -> str:
    rc, out = run(['python3', str(SCRIPTS / 'hermes_agent_delegate.py'), 'status', '--limit', '8'], timeout=45)
    if rc != 0 or not out.strip():
        return 'Your Majesty, I could not verify delegated task status from the task ledger.\n\nNOT VERIFIED'
    if 'NO_DELEGATED_TASKS_FOUND' in out:
        return 'Your Majesty, there are no delegated tasks recorded yet.'
    rows = []
    for line in out.splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        task_id = item.get('task_id', 'unknown')
        agent = item.get('assigned_agent', 'unknown agent')
        status = item.get('status', 'unknown')
        verification = item.get('verification_status', 'NOT VERIFIED')
        route = item.get('route', 'unknown route')
        rows.append(f'- {task_id}: {agent} ({route}) - {status}, verification: {verification}')
    if not rows:
        return 'Your Majesty, I could not verify delegated task status from the task ledger.\n\nNOT VERIFIED'
    return 'Your Majesty, these are the recent delegated task records from storage:\n\n' + '\n'.join(rows[:8])


def agent_preview_response(message: str) -> str:
    low = (message or '').lower()
    if re.search(r'what\s+agents\s+do\s+you\s+have|list\s+agents', low):
        return agent_list_response()
    if re.search(r'show\s+(recent\s+)?delegated\s+tasks|show\s+agent\s+tasks|delegated\s+task\s+status', low):
        return delegated_status_response()
    if AGENT_EXECUTION_RE.search(message or ''):
        return ('Your Majesty, live delegation execution is not enabled yet.\n\n'
                'I can prepare a dry-run delegation plan, but I will not execute delegated tasks from live Telegram in this phase.')

    rc, out = run(['python3', str(SCRIPTS / 'hermes_agent_delegate.py'), 'classify', message or ''], timeout=45)
    data = parse_key_values(out)
    agent = data.get('recommended_agent') or 'NOT VERIFIED'
    route = data.get('route') or 'NOT VERIFIED'
    model = data.get('model') or 'NOT VERIFIED'
    provider = data.get('provider') or 'NewCoin'

    if 'Apps, Coding & Complex Builds Agent' in agent:
        return (f'Your Majesty, this would be handled by the Apps, Coding & Complex Builds Agent.\n\n'
                f'Route: coding/debugging\nModel: {provider} {model}\n\n'
                'Live execution is not enabled yet; I can prepare a dry-run delegation plan.')
    if 'Ops & Verification Agent' in agent:
        return (f'Your Majesty, this would be handled by the Ops & Verification Agent.\n\n'
                f'Route: {route}\n'
                'It would verify service status, healthchecks, logs, and evidence before reporting.')
    if 'Personal/Admin & Tutor Agent' in agent:
        return (f'Your Majesty, reminders and lesson plans belong to the Personal/Admin & Tutor Agent.\n\n'
                'Reminders stay tool-first and storage-backed. Lesson/admin tasks use the personal/admin/tutor route.')
    if 'Hermes Overseer' in agent:
        return (f'Your Majesty, this would stay with the Hermes Overseer / Main Agent.\n\n'
                f'Route: {route}\nModel: {provider} {model}')
    return 'Your Majesty, I could not verify the correct agent from the delegation framework.\n\nNOT VERIFIED'


def is_agent_preview_intent(message: str) -> bool:
    text = message or ''
    return bool(AGENT_PREVIEW_RE.search(text) or AGENT_EXECUTION_RE.search(text))



def reminder_guard(message: str) -> dict[str, Any]:
    rc, out = run(['python3', str(SCRIPTS / 'hermes_reminder_intent_guard.py'), message or '', '--format', 'json'], timeout=45)
    if rc != 0 or not out.strip():
        return {'applies': False, 'direct_response': False, 'category': 'guard_unavailable'}
    try:
        data = json.loads(out)
        return data if isinstance(data, dict) else {'applies': False, 'direct_response': False, 'category': 'guard_bad_json'}
    except Exception:
        return {'applies': False, 'direct_response': False, 'category': 'guard_parse_failed'}


def handle(message: str) -> dict[str, Any]:
    decision = hermes_model_router.classify_message(message or '')
    route = decision.get('route')
    tool = decision.get('tool')
    response = ''
    direct = False

    guard = reminder_guard(message or '')
    if guard.get('applies') and guard.get('create_allowed') and not guard.get('direct_response'):
        # Fully specified reminder create requests may continue to the existing
        # verified reminder creation path. The guard only prevents ambiguous
        # requests from falling through to model guessing.
        decision = {'route': 'default', 'provider': 'NewCoin', 'model': 'qwen3-32b', 'reason': 'validated reminder create intent; storage verification required after create'}
        route = 'default'
        tool = None
    if guard.get('applies') and guard.get('direct_response'):
        direct = True
        response = str(guard.get('response') or '').strip() or 'NOT VERIFIED\nREASON=REMINDER_GUARD_EMPTY_RESPONSE'
        decision = {'route': 'tool', 'tool': 'hermes_reminder_intent_guard', 'provider': 'NewCoin', 'model': 'qwen3-32b', 'reason': guard.get('category')}
        tool = 'hermes_reminder_intent_guard'
    elif is_agent_preview_intent(message or ''):
        direct = True
        response = agent_preview_response(message or '')
    elif route == 'tool':
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
