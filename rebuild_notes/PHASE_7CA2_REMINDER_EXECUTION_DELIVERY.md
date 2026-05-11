# Phase 7C-A2: Reminder Execution and Delivery Reliability

Problem:
Verified reminder creation did not produce a Telegram notification. The failed job disappeared from active cron storage, making post-failure diagnosis impossible.

Findings:
- Gateway cron ticker is started inside hermes-gateway.service.
- Cron scheduler uses timezone-aware comparisons via hermes_time.now().
- The failed job ID was no longer present in /root/.hermes/cron/jobs.json.
- mark_job_run removed repeat-limited one-shot jobs immediately, erasing terminal delivery evidence.
- Scheduler could leave last_status=ok even when delivery_error was set.

Fix:
- One-shot/limited jobs are retained as terminal audit records instead of being popped from jobs.json.
- Delivery errors now make the job run fail and are logged/recorded.
- Scheduler logs delivery attempt and delivery verification result.
- Added /root/.hermes/scripts/hermes_reminder_delivery_test.py.

No Gmail/YouTube/private route changes.
No default model changed.
