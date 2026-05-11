#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SAFE_ROOTS = [
    Path('/root/.hermes/rebuild_notes'),
    Path('/root/.hermes/BOOT.md'),
    Path('/root/.hermes/skills'),
    Path('/root/.hermes/model_routing'),
    Path('/root/.hermes/config.yaml'),
    Path('/root/hermano-backup'),
]
ALLOWED_SUFFIXES = {'.md', '.txt', '.yaml', '.yml', '.json', '.log'}
EXCLUDED_PARTS = {
    '.git', '__pycache__', 'tokens', 'token', 'oauth', 'credentials',
    'file_outputs', 'newcoin_outputs', 'research_sources', 'logs', 'cache',
}
EXCLUDED_NAMES = {
    '.env', 'providers.env', 'credentials.json', 'token.json', 'client_secret.json',
}
MAX_FILE_BYTES = 1_000_000
STOPWORDS = {'the','and','for','not','with','that','this','from','present','before','after','what','when','where','show','latest'}

SECRET_PATTERNS = [
    (re.compile(r'bot\d+:[A-Za-z0-9_-]+'), 'bot<REDACTED>'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._-]+', re.I), 'Bearer <REDACTED>'),
    (re.compile(r'\b(sk-[A-Za-z0-9_-]{10,}|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9_]+)\b'), '<REDACTED_TOKEN>'),
    (re.compile(r'(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(token\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(password\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'(?i)(secret\s*[:=]\s*)[^\s,;]+'), r'\1<REDACTED>'),
    (re.compile(r'telegram:-?\d+(?::\d+)?'), 'telegram:<chat_id_masked>'),
]
CHAT_ID_RE = re.compile(r'(?i)(chat[_-]?id["\']?\s*[:=]\s*["\']?)-?\d+(["\']?)')

@dataclass
class Match:
    path: Path
    line_no: int
    excerpt: str
    score: int


def mask(text: str) -> str:
    out = text
    for pat, repl in SECRET_PATTERNS:
        out = pat.sub(repl, out)
    out = CHAT_ID_RE.sub(r'\1<chat_id_masked>\2', out)
    return out


def is_excluded(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    if parts & EXCLUDED_PARTS:
        return True
    if path.name.lower() in EXCLUDED_NAMES:
        return True
    name_l = path.name.lower()
    if any(x in name_l for x in ['token', 'oauth', 'credential', 'secret']) and path.suffix.lower() not in {'.md', '.txt'}:
        return True
    return False


def iter_files() -> Iterable[Path]:
    for root in SAFE_ROOTS:
        if not root.exists() or is_excluded(root):
            continue
        if root.is_file():
            if root.suffix.lower() in ALLOWED_SUFFIXES and not is_excluded(root):
                yield root
            continue
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES and not is_excluded(p):
                try:
                    if p.stat().st_size <= MAX_FILE_BYTES:
                        yield p
                except OSError:
                    continue


def read_text(path: Path) -> str:
    return path.read_text(errors='ignore')


def score_path(path: Path) -> int:
    s = 0
    txt = str(path)
    if '/rebuild_notes/' in txt:
        s += 50
    if path.name.startswith('PHASE_'):
        s += 25
    if path.name in {'BOOT.md', 'AGENTS.md', 'SOUL.md'}:
        s += 10
    if '/logs/' in txt or path.suffix == '.log':
        s -= 20
    return s


def search(query: str, limit: int = 12) -> list[Match]:
    terms = [t.lower() for t in re.findall(r'[A-Za-z0-9]+', query) if len(t) >= 3 and t.lower() not in STOPWORDS]
    if not terms:
        return []
    matches: list[Match] = []
    for path in iter_files():
        try:
            lines = read_text(path).splitlines()
        except Exception:
            continue
        pscore = score_path(path)
        for i, line in enumerate(lines, 1):
            low = line.lower()
            hit_count = sum(1 for t in terms if t in low)
            if hit_count and (hit_count == len(terms) or (len(terms) > 3 and hit_count >= 2)):
                excerpt = mask(line.strip())[:260]
                score = pscore + hit_count * 10
                matches.append(Match(path, i, excerpt, score))
    matches.sort(key=lambda m: (m.score, str(m.path), -m.line_no), reverse=True)
    return matches[:limit]


def latest_notes(limit: int = 8) -> list[Path]:
    root = Path('/root/.hermes/rebuild_notes')
    if not root.exists():
        return []
    notes = [p for p in root.glob('*.md') if p.is_file() and not is_excluded(p)]
    notes.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return notes[:limit]


def print_matches(matches: list[Match]) -> int:
    if not matches:
        print('NOT VERIFIED')
        print('REASON=NO_EVIDENCE_FOUND')
        return 1
    print('SESSION_RECALL_SEARCH=PASSED')
    for m in matches:
        print(f'{m.path}:{m.line_no}: {m.excerpt}')
    return 0


def cmd_latest(args) -> int:
    notes = latest_notes(args.limit)
    if not notes:
        print('NOT VERIFIED')
        print('REASON=NO_REBUILD_NOTES_FOUND')
        return 1
    print('SESSION_RECALL_LATEST=PASSED')
    for p in notes:
        title = p.name
        first = ''
        try:
            for line in read_text(p).splitlines():
                if line.strip():
                    first = mask(line.strip())[:180]
                    break
        except Exception:
            pass
        print(f'{p}: {title} | {first}')
    return 0


def cmd_phase(args) -> int:
    q = args.phase.strip().lower().replace('phase', '').strip().replace('-', '').replace(' ', '')
    root = Path('/root/.hermes/rebuild_notes')
    candidates = []
    if root.exists():
        for p in root.glob('*.md'):
            normalized = p.name.lower().replace('phase_', '').replace('-', '').replace('_', '')
            if q in normalized:
                candidates.append(p)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return print_matches(search(args.phase, limit=args.limit))
    print('SESSION_RECALL_PHASE=PASSED')
    for p in candidates[:args.limit]:
        print(f'## {p}')
        text = mask(read_text(p))
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
        for ln in lines[:18]:
            print(ln[:240])
    return 0


def git_commit() -> str:
    try:
        out = subprocess.check_output(['git', '-C', '/root/hermano-backup', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        return out
    except Exception:
        return 'NOT VERIFIED'


def file_tail(path: Path, max_lines: int = 20) -> list[str]:
    if not path.exists():
        return []
    lines = mask(read_text(path)).splitlines()
    return [ln for ln in lines[-max_lines:] if ln.strip()]


def cmd_status(args) -> int:
    print('SESSION_RECALL_STATUS=PASSED')
    print('latest_git_backup_commit=' + git_commit())
    print('latest_rebuild_notes=')
    for p in latest_notes(5):
        print(f'- {p.name}')
    for label, path in [
        ('quick_healthcheck', Path('/root/.hermes/rebuild_notes/ops_healthcheck_latest.md')),
        ('deep_healthcheck', Path('/root/.hermes/rebuild_notes/ops_healthcheck_deep_latest.md')),
        ('startup_healthcheck', Path('/root/.hermes/rebuild_notes/startup_healthcheck_last_status.md')),
    ]:
        print(f'{label}=')
        lines = file_tail(path, 12)
        if lines:
            for ln in lines:
                if 'PASSED' in ln or 'NOT_VERIFIED' in ln or 'timestamp:' in ln or 'OPS_HEALTHCHECK' in ln or 'REMINDER_' in ln or 'DELIVERY_PATH_VERIFIED' in ln:
                    print(f'  {ln[:220]}')
        else:
            print('  NOT VERIFIED')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Search safe Hermes rebuild/session context.')
    sub = parser.add_subparsers(dest='mode')
    s = sub.add_parser('search', help='Search safe local context')
    s.add_argument('query')
    s.add_argument('--limit', type=int, default=12)
    l = sub.add_parser('latest', help='Show latest rebuild notes')
    l.add_argument('--limit', type=int, default=8)
    p = sub.add_parser('phase', help='Show notes for a phase, e.g. 7C')
    p.add_argument('phase')
    p.add_argument('--limit', type=int, default=8)
    sub.add_parser('status', help='Summarize current Hermes status evidence')
    args = parser.parse_args()
    if args.mode == 'search':
        return print_matches(search(args.query, args.limit))
    if args.mode == 'latest':
        return cmd_latest(args)
    if args.mode == 'phase':
        return cmd_phase(args)
    if args.mode == 'status':
        return cmd_status(args)
    parser.print_help()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
