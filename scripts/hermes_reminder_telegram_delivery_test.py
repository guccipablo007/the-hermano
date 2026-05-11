#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERMES_AGENT = Path('/usr/local/lib/hermes-agent')
sys.path.insert(0, str(HERMES_AGENT))
sys.path.insert(0, str(HERMES_AGENT / 'tools'))

from cron.jobs import get_job, list_jobs  # noqa: E402
from cron.scheduler import tick  # noqa: E402
from tools.cronjob_tools import cronjob  # noqa: E402

TZ = ZoneInfo('Asia/Shanghai')
AUDIT = Path('/root/.hermes/cron/delivery_audit.jsonl')


def _hash(value: str) -> str:
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:12]


def _find_chat_id() -> str:
    candidates = []
    for job in list_jobs(include_disabled=True):
        origin = job.get('origin') or {}
        if origin.get('platform') == 'telegram' and origin.get('chat_id'):
            candidates.append(str(origin['chat_id']))
        deliver = str(job.get('deliver') or '')
        if deliver.startswith('telegram:'):
            parts = deliver.split(':')
            if len(parts) >= 2 and parts[1]:
                candidates.append(parts[1])
    if not candidates:
        raise RuntimeError('NO_TELEGRAM_CHAT_ID_FOUND')
    return candidates[-1]


def _audit_events(job_id: str):
    if not AUDIT.exists():
        return []
    events = []
    for line in AUDIT.read_text(errors='ignore').splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if item.get('job_id') == job_id:
            events.append(item)
    return events


def main() -> int:
    chat_id = _find_chat_id()
    run_at = datetime.now(TZ) + timedelta(seconds=20)
    name = 'Telegram real delivery verification'
    prompt = 'Reminder delivery test: this message verifies real Telegram reminder delivery.'

    created_raw = cronjob(
        action='create',
        name=name,
        prompt=prompt,
        schedule=run_at.isoformat(),
        repeat=1,
        deliver=f'telegram:{chat_id}',
        no_agent=True,
        script='hermes_time_context.py',
    )
    created = json.loads(created_raw)
    if not created.get('success') or not created.get('verified'):
        print('NOT VERIFIED')
        print('REASON=CREATE_FAILED')
        print(created_raw)
        return 1

    job_id = created['job_id']
    job = get_job(job_id)
    if not job:
        print('NOT VERIFIED')
        print('REASON=JOB_MISSING_AFTER_CREATE')
        return 1
    if not str(job.get('deliver') or '').startswith('telegram:'):
        print('NOT VERIFIED')
        print('REASON=DELIVER_TARGET_NOT_TELEGRAM')
        print('DELIVER=' + str(job.get('deliver')))
        return 1

    print('TEST_JOB_ID=' + job_id)
    print('TELEGRAM_CHAT_ID_PRESENT=TRUE')
    print('TELEGRAM_CHAT_ID_HASH=' + _hash(chat_id))
    print('DUE_AT=' + run_at.isoformat())

    deadline = time.time() + 75
    terminal = None
    while time.time() < deadline:
        tick(verbose=True)
        job = get_job(job_id)
        if job and job.get('state') in ('completed', 'error'):
            terminal = job
            break
        time.sleep(5)

    if not terminal:
        print('NOT VERIFIED')
        print('REASON=JOB_NOT_TERMINAL_AFTER_WAIT')
        return 1

    events = _audit_events(job_id)
    success_events = [e for e in events if e.get('event') == 'success' and e.get('target_type') == 'telegram']
    failure_events = [e for e in events if e.get('event') == 'failure']

    print('FINAL_JOB_STATE=' + str(terminal.get('state')))
    print('FINAL_LAST_STATUS=' + str(terminal.get('last_status')))
    print('DELIVERY_AUDIT_EVENTS=' + str(len(events)))
    print('TELEGRAM_SEND_ATTEMPTED=' + str(any(e.get('event') == 'attempt' and e.get('target_type') == 'telegram' for e in events)).upper())
    print('TELEGRAM_API_SUCCESS=' + str(bool(success_events)).upper())

    if terminal.get('state') == 'completed' and terminal.get('last_status') == 'ok' and success_events:
        print('REMINDER_TELEGRAM_DELIVERY_TEST=PASSED')
        return 0

    print('NOT VERIFIED')
    print('REASON=TELEGRAM_DELIVERY_NOT_VERIFIED')
    if failure_events:
        print('FAILURE_EVENT=' + json.dumps(failure_events[-1], ensure_ascii=False))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
