#!/usr/bin/env python3
from __future__ import annotations
import json, sys, time
from pathlib import Path
AGENT_ROOT = Path('/usr/local/lib/hermes-agent')
for p in [AGENT_ROOT, AGENT_ROOT / 'tools']:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from tools.cronjob_tools import cronjob
from cron.jobs import get_job
from cron.scheduler import tick

def fail(reason: str) -> int:
    print('NOT VERIFIED')
    print('REASON=' + reason)
    return 1

def main() -> int:
    raw = cronjob(
        action='create',
        prompt='Test reminder delivery path: remind me in 1 minute. This is an automated local execution path test.',
        schedule='in 1 minute',
        name='phase7ca2_reminder_delivery_test',
        repeat=1,
        deliver='local',
        no_agent=True,
        script='hermes_time_context.py',
    )
    try:
        data=json.loads(raw)
    except Exception as exc:
        return fail('CREATE_RETURN_NOT_JSON:' + type(exc).__name__)
    if not data.get('success'):
        return fail('CREATE_FAILED:' + str(data.get('error') or data.get('reason')))
    job_id=data.get('job_id')
    if not job_id or not get_job(job_id):
        return fail('JOB_NOT_FOUND_AFTER_CREATE')
    print('JOB_ID=' + job_id)
    print('WAITING_FOR_DUE=70_SECONDS')
    time.sleep(70)
    ran = tick(verbose=True)
    print('SCHEDULER_TICK_RAN=' + str(ran))
    job=get_job(job_id)
    if not job:
        return fail('JOB_REMOVED_AFTER_EXECUTION')
    print('JOB_STATE=' + str(job.get('state')))
    print('JOB_LAST_STATUS=' + str(job.get('last_status')))
    print('JOB_LAST_ERROR=' + str(job.get('last_error')))
    print('JOB_LAST_DELIVERY_ERROR=' + str(job.get('last_delivery_error')))
    if job.get('state') not in ('completed','error'):
        return fail('JOB_NOT_TERMINAL_AFTER_TICK')
    if job.get('last_run_at') is None:
        return fail('JOB_LAST_RUN_MISSING')
    if job.get('last_status') != 'ok':
        return fail('JOB_EXECUTION_NOT_OK')
    print('DELIVERY_PATH_VERIFIED=LOCAL_EXECUTION_COMPLETED')
    print('REMINDER_DELIVERY_TEST=PASSED')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
