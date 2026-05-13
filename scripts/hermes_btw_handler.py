#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

RECALL = Path('/root/.hermes/scripts/hermes_session_recall.py')
VERIFY = Path('/root/.hermes/scripts/hermes_verify_claim.py')
PROVIDER_STATUS = Path('/root/.hermes/scripts/hermes_provider_status.py')
TIME_CONTEXT = Path('/root/.hermes/scripts/hermes_time_context.py')
CONFIG = Path('/root/.hermes/config.yaml')

MASK_PATTERNS = [
    (re.compile(r'bot\d+:[A-Za-z0-9_-]+'), 'bot<REDACTED>'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._-]+', re.I), 'Bearer <REDACTED>'),
    (re.compile(r'\b(sk-[A-Za-z0-9_-]{10,}|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9_]+)\b'), '<REDACTED_TOKEN>'),
    (re.compile(r'(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(token\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(password\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(secret\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'telegram:-?\d+(?::\d+)?'), 'telegram:<chat_id_masked>'),
    (re.compile(r'(?i)(chat[_-]?id["\']?\s*[:=]\s*["\']?)-?\d+(["\']?)'), r'\1<chat_id_masked>\2'),
]
RISKY = [
    'restart', 'start service', 'stop service', 'systemctl', 'delete', 'remove', 'rm ',
    'edit ', 'patch ', 'write ', 'create file', 'configure gmail', 'configure youtube',
    'activate private_data', 'token', 'api key', 'oauth', 'password', 'deploy key', 'send email'
]
RAW_WORDS = {'raw', 'debug', 'technical', 'details', 'detail'}


def mask(text: object) -> str:
    out = str(text or '')
    for pat, repl in MASK_PATTERNS:
        out = pat.sub(repl, out)
    return out


def run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return proc.returncode, mask(((proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')).strip())


def strip_btw(text: str) -> str:
    t = (text or '').strip()
    if t.lower().startswith('/btw'):
        return t[4:].strip(' :\t')
    return t


def wants_raw(question: str) -> bool:
    tokens = re.findall(r'[A-Za-z]+', (question or '').lower())
    return bool(tokens and tokens[0] in RAW_WORDS)


def strip_raw_prefix(question: str) -> str:
    return re.sub(r'^(raw|debug|technical|details?|show details)\b\s*', '', question.strip(), flags=re.I).strip()


def raw_or_not_verified(rc: int, output: str) -> str:
    if rc == 0 and output:
        return output
    return output or 'NOT VERIFIED\nREASON=NO_LOCAL_EVIDENCE'


def clean_line(line: str) -> str:
    line = mask(line.strip())
    line = re.sub(r'^[-*]\s*`?([^`]+?)`?\s*$', r'\1', line)
    line = re.sub(r'`([^`]+)`', r'\1', line)
    return line.strip(' -')


def drop_raw_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        s = clean_line(line)
        if not s:
            continue
        if s.startswith(('SESSION_RECALL_', 'VERIFIED', 'EARLIEST_NEXT_REMINDER', 'MATCH_COUNT=', 'MATCH', 'REASON=')):
            continue
        if s.startswith('/root/') or s.startswith('## /root/'):
            continue
        cleaned.append(s)
    return cleaned


def format_phase_recall(raw: str, phase_text: str) -> str:
    lines = drop_raw_lines(raw.splitlines())
    if not lines:
        return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'
    title = next((ln.lstrip('# ').strip() for ln in lines if ln.startswith('# ')), '')
    if not title:
        title = f'Phase {phase_text.strip()} record'
    purpose = ''
    changed: list[str] = []
    tests: list[str] = []
    for i, line in enumerate(lines):
        low = line.lower().rstrip(':')
        if low == 'purpose' and i + 1 < len(lines):
            purpose = lines[i + 1]
        elif low in {'fix', 'changes', 'created/updated', 'created', 'updated'}:
            for candidate in lines[i + 1:i + 7]:
                if candidate.lower().rstrip(':') in {'purpose', 'script modes', 'verification', 'tests'}:
                    break
                if candidate and not candidate.startswith('#'):
                    changed.append(candidate)
        elif (
            any(key in low for key in ['passed', 'test', 'healthcheck', 'verification'])
            and not line.startswith('#')
            and not re.match(r'^[A-Za-z0-9_-]+$', line)
            and len(tests) < 2
        ):
            tests.append(line)
    if not purpose:
        for line in lines:
            if line.startswith('#'):
                continue
            if len(line) > 20 and not line.lower().endswith(':'):
                purpose = line
                break
    parts = [f'Your Majesty, {title}.']
    if purpose:
        parts.append(purpose.rstrip('. ') + '.')
    if changed:
        short = '; '.join(dict.fromkeys(changed[:3]))
        parts.append('Main change: ' + short.rstrip('. ') + '.')
    if tests:
        parts.append('Verification: ' + '; '.join(dict.fromkeys(tests[:2])).rstrip('. ') + '.')
    parts.append('Verified from rebuild notes.')
    return '\n\n'.join(parts)


def format_search_recall(raw: str) -> str:
    if 'NOT VERIFIED' in raw and 'SESSION_RECALL_SEARCH=PASSED' not in raw:
        return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'
    findings = []
    for line in raw.splitlines():
        if line.startswith('SESSION_RECALL_'):
            continue
        m = re.match(r'.+?:\d+:\s*(.+)', line.strip())
        if m:
            excerpt = clean_line(m.group(1))
            if excerpt and '/root/' not in excerpt and not excerpt.startswith(('python3 ', 'hermes_')) and excerpt not in findings:
                findings.append(excerpt)
        elif line.strip() and not line.startswith('/root/'):
            excerpt = clean_line(line)
            if excerpt and '/root/' not in excerpt and not excerpt.startswith(('python3 ', 'hermes_')) and excerpt not in findings and not excerpt.startswith('SESSION_RECALL_'):
                findings.append(excerpt)
    if not findings:
        return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'
    lines = ['Your Majesty, I found these verified notes:']
    for item in findings[:3]:
        lines.append(f'- {item}')
    return '\n'.join(lines)


def format_latest_backup(raw: str) -> str:
    m = re.search(r'latest backup commit=([0-9a-f]{8,40})', raw, flags=re.I)
    if not m:
        m = re.search(r'([0-9a-f]{40})', raw)
    if m:
        return f'Your Majesty, the latest verified Hermes backup commit is {m.group(1)}.'
    return 'Your Majesty, I could not verify the latest backup commit from local Hermes records.\n\nNOT VERIFIED'


def format_time(raw: str) -> str:
    text = ' '.join(drop_raw_lines(raw.splitlines()))
    return text or 'Your Majesty, I could not verify the current China time.\n\nNOT VERIFIED'


def answer_model(raw_mode: bool = False) -> str:
    if PROVIDER_STATUS.exists():
        fmt = 'raw' if raw_mode else 'friendly'
        rc, out = run(['python3', str(PROVIDER_STATUS), 'status', '--format', fmt], timeout=60)
        if rc == 0 and out.strip():
            return out.strip()
    if not CONFIG.exists():
        return 'Your Majesty, I could not verify the Hermes model from local config.\n\nNOT VERIFIED'
    try:
        import yaml
        data = yaml.safe_load(CONFIG.read_text(errors='ignore')) or {}
        model = data.get('model', {})
        provider = model.get('provider') if isinstance(model, dict) else None
        default = model.get('default') if isinstance(model, dict) else model
        specific = model.get('model') if isinstance(model, dict) else None
        parts = []
        if provider:
            parts.append(f'provider {provider}')
        if specific:
            parts.append(f'model {specific}')
        elif default:
            parts.append(f'default model {default}')
        return 'Your Majesty, Hermes is currently configured for ' + ', '.join(parts) + '.' if parts else 'Your Majesty, I could not verify the Hermes model from local config.\n\nNOT VERIFIED'
    except Exception:
        return 'Your Majesty, I could not verify the Hermes model from local config.\n\nNOT VERIFIED'


def handle(question: str) -> str:
    q = strip_btw(question)
    if not q:
        return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'
    raw_mode = wants_raw(q)
    query = strip_raw_prefix(q) if raw_mode else q
    low = query.lower()

    if any(word in low for word in RISKY):
        return 'This is a side question. Risky actions are NOT EXECUTED from /btw.'

    if 'time' in low and ('china' in low or 'now' in low or 'cst' in low):
        if TIME_CONTEXT.exists():
            rc, out = run(['python3', str(TIME_CONTEXT)], timeout=30)
            return raw_or_not_verified(rc, out) if raw_mode else format_time(out)
        return 'Your Majesty, I could not verify the current China time.\n\nNOT VERIFIED'

    if (('model' in low or 'provider' in low) and ('using' in low or 'current' in low or 'hermes' in low or 'now' in low)):
        return answer_model(raw_mode)

    if 'backup' in low and ('commit' in low or 'latest' in low):
        if VERIFY.exists():
            rc, out = run(['python3', str(VERIFY), 'latest-backup'], timeout=60)
            return raw_or_not_verified(rc, out) if raw_mode else format_latest_backup(out)
        return 'Your Majesty, I could not verify the latest backup commit from local Hermes records.\n\nNOT VERIFIED'

    phase_match = re.search(r'phase\s+([0-9]+[a-z](?:-[a-z0-9]+)?)', low, re.I)
    if phase_match and RECALL.exists():
        phase = phase_match.group(1)
        rc, out = run(['python3', str(RECALL), 'phase', phase], timeout=80)
        return raw_or_not_verified(rc, out) if raw_mode else format_phase_recall(out, phase)

    if any(w in low for w in ['fix', 'fixed', 'changed', 'previous', 'notes', 'recall', 'search', 'phase', 'reminder failure']):
        if RECALL.exists():
            search_query = query
            if low.startswith('search '):
                search_query = query.split(None, 1)[1] if len(query.split(None, 1)) > 1 else query
            rc, out = run(['python3', str(RECALL), 'search', search_query], timeout=80)
            return raw_or_not_verified(rc, out) if raw_mode else format_search_recall(out)
        return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'

    if any(w in low for w in ['status', 'health', 'healthy', 'setup']):
        rc, out = run(['hermes_ops_healthcheck', '--quick'], timeout=60)
        if raw_mode:
            return raw_or_not_verified(rc, out)
        return 'Your Majesty, Hermes quick healthcheck passed.' if 'OPS_HEALTHCHECK_QUICK=PASSED' in out else 'Your Majesty, Hermes health is NOT VERIFIED from the quick healthcheck.'

    return 'Your Majesty, I could not verify that from local Hermes records.\n\nNOT VERIFIED'


def main() -> int:
    parser = argparse.ArgumentParser(description='Handle read-only Hermes /btw side questions.')
    parser.add_argument('question', nargs='+')
    args = parser.parse_args()
    print(mask(handle(' '.join(args.question))))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
