#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path('/root/.hermes/scripts/hermes_reminder_intent_guard.py')
JOBS = Path('/root/.hermes/cron/jobs.json')

spec = importlib.util.spec_from_file_location('guard', SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)  # type: ignore[union-attr]


def job_count() -> int:
    if not JOBS.exists():
        return 0
    data = json.loads(JOBS.read_text())
    jobs = data.get('jobs') if isinstance(data, dict) else data
    return len(jobs or [])


def assert_case(name: str, message: str, *, category: str | None = None, direct: bool | None = None, create: bool | None = None, must_contain: str | None = None, must_not_contain: str | None = None):
    before = job_count()
    result = guard.classify(message)
    after = job_count()
    if before != after:
        raise AssertionError(f'{name}: guard changed job count {before}->{after}')
    if category is not None and result.get('category') != category:
        raise AssertionError(f'{name}: category {result.get("category")} != {category}')
    if direct is not None and bool(result.get('direct_response')) != direct:
        raise AssertionError(f'{name}: direct {result.get("direct_response")} != {direct}')
    if create is not None and bool(result.get('create_allowed')) != create:
        raise AssertionError(f'{name}: create_allowed {result.get("create_allowed")} != {create}')
    text = str(result.get('response') or '')
    if must_contain and must_contain.lower() not in text.lower():
        raise AssertionError(f'{name}: missing text {must_contain!r}: {text}')
    if must_not_contain and must_not_contain.lower() in text.lower():
        raise AssertionError(f'{name}: forbidden text {must_not_contain!r}: {text}')
    print(f'{name}=PASSED')
    return result


def main() -> int:
    assert_case('AMBIGUOUS_TOMORROW_INQUIRY', 'Reminder for tomorrow?', category='tomorrow_inquiry', direct=True, create=False, must_contain='verified reminder storage')
    assert_case('REMINDER_INQUIRY', 'Any reminders tomorrow?', category='tomorrow_inquiry', direct=True, create=False, must_contain='verified reminder storage')
    assert_case('AMBIGUOUS_CREATE', 'Remind me tomorrow', category='ambiguous_create_missing_task_time', direct=True, create=False, must_contain='did not create')
    assert_case('MISSING_TIME', 'Remind me tomorrow to call Mr Wang', category='missing_time', direct=True, create=False, must_contain='What time')
    assert_case('MISSING_TASK', 'Remind me tomorrow at 8 AM', category='missing_task', direct=True, create=False, must_contain='What should I remind')
    assert_case('VALID_TOMORROW_CREATE', 'Remind me tomorrow at 8 AM to call Mr Wang', category='valid_create', direct=False, create=True)
    assert_case('VALID_RELATIVE_CREATE', 'Remind me in 10 minutes to check the soup', category='valid_create', direct=False, create=True)
    assert_case('EVENT_BASED_REQUIRES_VERIFICATION', 'Remind me 1 hour before my class', category='event_based_needs_verification', direct=True, create=False, must_contain='verified reminder storage')
    r = assert_case('NO_GUESSED_UPLOAD_CLASS', 'Reminder for tomorrow?', category='tomorrow_inquiry', direct=True, create=False, must_not_contain='YouTube upload')
    if 'class' in str(r.get('response', '')).lower() and 'verified reminder storage' not in str(r.get('response', '')).lower():
        raise AssertionError('NO_GUESSED_UPLOAD_CLASS: class appeared without storage verification context')
    print('NO_CREATE_CALLS=PASSED')
    print('REMINDER_INTENT_VALIDATION_TEST=PASSED')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
