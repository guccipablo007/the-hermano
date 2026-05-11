#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERMES_AGENT = Path('/usr/local/lib/hermes-agent')
sys.path.insert(0, str(HERMES_AGENT))
sys.path.insert(0, str(HERMES_AGENT / 'tools'))

from cron.jobs import get_job, list_jobs  # noqa: E402
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
            if len(parts) >= 2 and parts[1] and not parts[1].startswith('<'):
                candidates.append(parts[1])
    if not candidates:
        raise RuntimeError('NO_TELEGRAM_CHAT_ID_FOUND')
    return candidates[-1]


def _events(job_id: str):
    if not AUDIT.exists():
        return []
    out = []
    for line in AUDIT.read_text(errors='ignore').splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if item.get('job_id') == job_id:
            out.append(item)
    return out


def main() -> int:
    chat_id = _find_chat_id()
    os.environ['HERMES_SESSION_PLATFORM'] = 'telegram'
    os.environ['HERMES_SESSION_CHAT_ID'] = chat_id
    os.environ['HERMES_SESSION_CHAT_NAME'] = 'redacted-live-same-path-test'

    run_at = datetime.now(TZ) + timedelta(seconds=75)
    prompt = 'Reminder: Live same-path scheduler test'
    raw = cronjob(
        action='create',
        name='Reminder: Live same-path scheduler test',
        prompt=prompt,
        schedule=run_at.isoformat(),
        repeat=1,
        deliver=None,
        no_agent=False,
    )
    data = json.loads(raw)
    if not data.get('success') or not data.get('verified'):
        print('NOT VERIFIED')
        print('REASON=CREATE_FAILED')
        print(raw)
        return 1
    job_id = data['job_id']
    job = get_job(job_id)
    if not job:
        print('NOT VERIFIED')
        print('REASON=JOB_MISSING_AFTER_CREATE')
        return 1
    deliver = str(job.get('deliver') or '')
    print('TEST_JOB_ID=' + job_id)
    print('DUE_AT=' + run_at.isoformat())
    print('DELIVER_IS_TELEGRAM=' + str(deliver.startswith('telegram:')).upper())
    print('TELEGRAM_CHAT_ID_PRESENT=TRUE')
    print('TELEGRAM_CHAT_ID_HASH=' + _hash(chat_id))

    if not deliver.startswith('telegram:'):
        print('NOT VERIFIED')
        print('REASON=DELIVER_NOT_RESOLVED_TO_TELEGRAM')
        return 1

    deadline = time.time() + 240
    terminal = None
    while time.time() < deadline:
        job = get_job(job_id)
        if job and job.get('state') in ('completed', 'error'):
            terminal = job
            break
        time.sleep(5)

    if not terminal:
        print('NOT VERIFIED')
        print('REASON=GATEWAY_SCHEDULER_DID_NOT_RUN_JOB')
        return 1

    events = _events(job_id)
    attempted = any(e.get('event') == 'attempt' and e.get('target_type') == 'telegram' for e in events)
    success = any(e.get('event') == 'success' and e.get('target_type') == 'telegram' for e in events)
    failure_events = [e for e in events if e.get('event') == 'failure']
    print('FINAL_JOB_STATE=' + str(terminal.get('state')))
    print('FINAL_LAST_STATUS=' + str(terminal.get('last_status')))
    print('TELEGRAM_SEND_ATTEMPTED=' + str(attempted).upper())
    print('TELEGRAM_API_SUCCESS=' + str(success).upper())
    print('DELIVERY_AUDIT_EVENTS=' + str(len(events)))

    if terminal.get('state') == 'completed' and terminal.get('last_status') == 'ok' and attempted and success:
        print('LIVE_REMINDER_SAME_PATH_TEST=PASSED')
        return 0

    print('NOT VERIFIED')
    print('REASON=LIVE_SAME_PATH_NOT_VERIFIED')
    if failure_events:
        print('FAILURE_EVENT=' + json.dumps(failure_events[-1], ensure_ascii=False))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
