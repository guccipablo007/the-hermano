#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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


def mask(text: object) -> str:
    out = str(text)
    for pat, repl in MASK_PATTERNS:
        out = pat.sub(repl, out)
    return out


def verified(summary: str) -> int:
    print('VERIFIED')
    print(mask(summary))
    return 0


def not_verified(reason: str) -> int:
    print('NOT VERIFIED')
    print('REASON=' + mask(reason))
    return 2


def cmd_file_exists(path_s: str) -> int:
    p = Path(path_s)
    try:
        if p.is_file() and p.stat().st_size > 0:
            return verified(f'file exists and size={p.stat().st_size}: {p}')
        if p.exists() and p.is_dir():
            return not_verified(f'path is a directory, not a file: {p}')
        if p.exists():
            return not_verified(f'file exists but is empty: {p}')
        return not_verified(f'file missing: {p}')
    except Exception as exc:
        return not_verified(f'file check failed: {type(exc).__name__}: {exc}')


def cmd_service_active(service: str) -> int:
    proc = subprocess.run(['systemctl', 'is-active', service], text=True, capture_output=True, timeout=30)
    status = (proc.stdout or proc.stderr).strip()
    if proc.returncode == 0 and status == 'active':
        return verified(f'service active: {service}')
    return not_verified(f'service not active: {service}; status={status or proc.returncode}')


def cmd_command_contains(command: str, expected: str) -> int:
    proc = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=180)
    combined = (proc.stdout or '') + '\n' + (proc.stderr or '')
    if expected in combined and proc.returncode == 0:
        return verified(f'command output contained expected text: {expected}')
    if expected in combined:
        return not_verified(f'expected text found but command exit was {proc.returncode}: {expected}')
    excerpt = mask(combined.strip()[:500]) if combined.strip() else '<no output>'
    return not_verified(f'expected text not found: {expected}; exit={proc.returncode}; output={excerpt}')


def _load_jobs():
    for path in [Path('/root/.hermes/cron/jobs.json'), Path('/root/.hermes/cron/cron_jobs.json')]:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(errors='ignore'))
            jobs = data.get('jobs', data if isinstance(data, list) else [])
            if isinstance(jobs, list):
                return jobs
        except Exception:
            continue
    return None


def cmd_job_status(job_id: str) -> int:
    jobs = _load_jobs()
    if jobs is None:
        return not_verified('cron storage not found or not readable')
    for job in jobs:
        if str(job.get('id')) == str(job_id):
            state = job.get('state')
            last_status = job.get('last_status')
            delivery_error = job.get('last_delivery_error')
            deliver = job.get('deliver')
            if state == 'completed' and last_status == 'ok' and not delivery_error:
                return verified(f'job terminal ok: id={job_id}; state={state}; deliver={deliver}')
            if state in {'error', 'failed'} or last_status == 'error' or delivery_error:
                return not_verified(f'job terminal error: id={job_id}; state={state}; last_status={last_status}; delivery_error={delivery_error}')
            return not_verified(f'job not terminal ok: id={job_id}; state={state}; last_status={last_status}')
    return not_verified(f'job not found: {job_id}')


def cmd_latest_backup() -> int:
    repo = Path('/root/hermano-backup')
    if not (repo / '.git').exists():
        return not_verified('backup repo missing: /root/hermano-backup')
    try:
        commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL, timeout=30).strip()
        branch = subprocess.check_output(['git', '-C', str(repo), 'branch', '--show-current'], text=True, stderr=subprocess.DEVNULL, timeout=30).strip()
        remote = subprocess.check_output(['git', '-C', str(repo), 'remote', 'get-url', 'origin'], text=True, stderr=subprocess.DEVNULL, timeout=30).strip()
    except Exception as exc:
        return not_verified(f'git backup check failed: {type(exc).__name__}: {exc}')
    if re.fullmatch(r'[0-9a-f]{40}', commit):
        return verified(f'latest backup commit={commit}; branch={branch}; remote={remote}')
    return not_verified('latest backup commit was not a valid hash')


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify a Hermes success claim with local evidence.')
    sub = parser.add_subparsers(dest='mode')
    p = sub.add_parser('file-exists', help='Verify file exists and size > 0')
    p.add_argument('path')
    p = sub.add_parser('service-active', help='Verify systemd service is active')
    p.add_argument('service')
    p = sub.add_parser('command-contains', help='Verify command exits 0 and output contains expected text')
    p.add_argument('command')
    p.add_argument('expected')
    p = sub.add_parser('job-status', help='Verify cron job terminal status if storage is clear')
    p.add_argument('job_id')
    sub.add_parser('latest-backup', help='Verify latest safe Git backup commit')
    args = parser.parse_args()
    try:
        if args.mode == 'file-exists':
            return cmd_file_exists(args.path)
        if args.mode == 'service-active':
            return cmd_service_active(args.service)
        if args.mode == 'command-contains':
            return cmd_command_contains(args.command, args.expected)
        if args.mode == 'job-status':
            return cmd_job_status(args.job_id)
        if args.mode == 'latest-backup':
            return cmd_latest_backup()
        parser.print_help()
        return 0
    except subprocess.TimeoutExpired:
        return not_verified('verification command timed out')
    except Exception as exc:
        print('SCRIPT ERROR')
        print('REASON=' + mask(f'{type(exc).__name__}: {exc}'))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
