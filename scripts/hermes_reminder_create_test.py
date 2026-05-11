#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import timedelta, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

AGENT_ROOT = Path('/usr/local/lib/hermes-agent')
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))
if str(AGENT_ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT / 'tools'))

from hermes_time import now as hermes_now
from tools.cronjob_tools import cronjob
from cron.jobs import get_job

CHINA = ZoneInfo('Asia/Shanghai')

def fail(reason: str) -> int:
    print('NOT VERIFIED')
    print('REASON=' + reason)
    return 1

def main() -> int:
    before = hermes_now().astimezone(CHINA)
    expected = before + timedelta(minutes=2)
    result_raw = cronjob(
        action='create',
        prompt='Test reminder: remind me in 2 minutes. This is an automated Hermes reminder creation test.',
        schedule='in 2 minutes',
        name='phase7ca_reminder_create_test',
        repeat=1,
        deliver='local',
        no_agent=True,
        script='hermes_time_context.py',
    )
    try:
        result = json.loads(result_raw)
    except Exception as exc:
        return fail('CREATE_RETURN_NOT_JSON:' + type(exc).__name__)
    if not result.get('success'):
        return fail('CREATE_FAILED:' + str(result.get('error') or result.get('reason')))
    job_id = result.get('job_id')
    if not job_id:
        return fail('JOB_ID_MISSING')
    job = get_job(job_id)
    if not job:
        return fail('JOB_NOT_FOUND_IN_STORAGE')
    next_run_raw = job.get('next_run_at')
    if not next_run_raw:
        return fail('NEXT_RUN_MISSING')
    try:
        next_run = datetime.fromisoformat(next_run_raw).astimezone(CHINA)
    except Exception as exc:
        return fail('NEXT_RUN_INVALID:' + type(exc).__name__)
    delta = abs((next_run - expected).total_seconds())
    if delta > 5:
        print('EXPECTED=' + expected.isoformat())
        print('ACTUAL=' + next_run.isoformat())
        print('DELTA_SECONDS=' + str(delta))
        return fail('SCHEDULE_TIME_OUTSIDE_5_SECONDS')
    if job.get('schedule', {}).get('kind') != 'once':
        return fail('SCHEDULE_KIND_NOT_ONCE')
    if job.get('repeat', {}).get('times') != 1:
        return fail('REPEAT_NOT_ONE')
    print('REMINDER_CREATE_TEST=PASSED')
    print('JOB_ID=' + job_id)
    print('EXPECTED=' + expected.isoformat())
    print('ACTUAL=' + next_run.isoformat())
    print('DELTA_SECONDS=' + str(delta))
    print('TIMEZONE=Asia/Shanghai')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
