#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

RECALL = Path('/root/.hermes/scripts/hermes_session_recall.py')
VERIFY = Path('/root/.hermes/scripts/hermes_verify_claim.py')
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


def mask(text: object) -> str:
    out = str(text)
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


def concise(output: str, max_lines: int = 10, max_chars: int = 1400) -> str:
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    # Drop low-signal command headers while keeping evidence paths/status.
    keep = []
    for ln in lines:
        if ln.startswith(('SESSION_RECALL_', 'VERIFIED', 'NOT VERIFIED', 'REASON=', 'OPS_HEALTHCHECK_', 'latest_git_backup_commit=', 'latest_rebuild_notes=', '-', '/root/')):
            keep.append(ln)
        elif len(keep) < max_lines and not ln.startswith('Usage:'):
            keep.append(ln)
    text = '\n'.join(keep[:max_lines]) or output.strip()
    return text[:max_chars]


def answer_model() -> str:
    if not CONFIG.exists():
        return 'NOT VERIFIED\nREASON=config.yaml not found'
    try:
        import yaml
        data = yaml.safe_load(CONFIG.read_text(errors='ignore')) or {}
        model = data.get('model', {})
        provider = model.get('provider') if isinstance(model, dict) else None
        default = model.get('default') if isinstance(model, dict) else model
        specific = model.get('model') if isinstance(model, dict) else None
        return f'Provider: {provider}\nDefault model: {default}\nConfigured model override: {specific}'
    except Exception as exc:
        return f'NOT VERIFIED\nREASON=model config read failed: {type(exc).__name__}'


def handle(question: str) -> str:
    q = strip_btw(question)
    if not q:
        return 'NOT VERIFIED\nREASON=empty /btw question'
    low = q.lower()

    if any(word in low for word in RISKY):
        return 'This is a side question. Risky actions are NOT EXECUTED from /btw.'

    if 'time' in low and ('china' in low or 'now' in low or 'cst' in low):
        if TIME_CONTEXT.exists():
            rc, out = run(['python3', str(TIME_CONTEXT)], timeout=30)
            return concise(out) if rc == 0 else 'NOT VERIFIED\nREASON=time context command failed'
        return 'NOT VERIFIED\nREASON=time context helper missing'

    if 'model' in low and ('using' in low or 'current' in low or 'hermes' in low):
        return answer_model()

    if 'backup' in low and ('commit' in low or 'latest' in low):
        if VERIFY.exists():
            rc, out = run(['python3', str(VERIFY), 'latest-backup'], timeout=60)
            return concise(out)
        return 'NOT VERIFIED\nREASON=verification helper missing'

    phase_match = re.search(r'phase\s+([0-9]+[a-z](?:-[a-z0-9]+)?)', low, re.I)
    if phase_match and RECALL.exists():
        rc, out = run(['python3', str(RECALL), 'phase', phase_match.group(1)], timeout=80)
        return concise(out, max_lines=12)

    if any(w in low for w in ['fix', 'fixed', 'changed', 'previous', 'notes', 'recall', 'search', 'phase', 'reminder failure']):
        if RECALL.exists():
            query = q
            if low.startswith('search '):
                query = q.split(None, 1)[1] if len(q.split(None, 1)) > 1 else q
            rc, out = run(['python3', str(RECALL), 'search', query], timeout=80)
            return concise(out, max_lines=12)
        return 'NOT VERIFIED\nREASON=session recall helper missing'

    if any(w in low for w in ['status', 'health', 'healthy', 'setup']):
        rc, out = run(['hermes_ops_healthcheck', '--quick'], timeout=60)
        return concise(out)

    return 'NOT VERIFIED from local Hermes context.'


def main() -> int:
    parser = argparse.ArgumentParser(description='Handle read-only Hermes /btw side questions.')
    parser.add_argument('question', nargs='+')
    args = parser.parse_args()
    print(mask(handle(' '.join(args.question))))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
