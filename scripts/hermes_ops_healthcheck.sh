#!/usr/bin/env bash
set -u

REPORT="/root/.hermes/rebuild_notes/ops_healthcheck_latest.md"
TMP="${REPORT}.tmp"
mkdir -p "$(dirname "$REPORT")"
FAIL=0

sanitize() {
  sed -E \
    -e 's/(bot[0-9]+:)[A-Za-z0-9_-]+/\1<REDACTED>/g' \
    -e 's/(Bearer )[A-Za-z0-9._-]+/\1<REDACTED>/g' \
    -e 's/(api[_-]?key[=: ]+)[^[:space:]]+/\1<REDACTED>/Ig' \
    -e 's/(token[=: ]+)[^[:space:]]+/\1<REDACTED>/Ig' \
    -e 's/telegram:-?[0-9]+(:[0-9]+)?/telegram:<chat_id_masked>/g'
}

check_file() {
  local f="$1"
  if [ -f "$f" ]; then
    echo "FILE_OK=$f"
  else
    echo "FILE_MISSING=$f"
    FAIL=1
  fi
}

check_py() {
  local f="$1"
  if python3 -m py_compile "$f" >/tmp/hermes_ops_pycompile.out 2>&1; then
    echo "PY_COMPILE_OK=$f"
  else
    echo "PY_COMPILE_FAILED=$f"
    sanitize < /tmp/hermes_ops_pycompile.out
    FAIL=1
  fi
}

{
  echo "# Hermes Ops Healthcheck"
  echo "Generated: $(date -Is)"
  echo ""

  echo "## Gateway Service"
  ACTIVE="$(systemctl is-active hermes-gateway.service 2>/dev/null || true)"
  echo "GATEWAY_ACTIVE=$ACTIVE"
  if [ "$ACTIVE" != "active" ]; then FAIL=1; fi
  systemctl status hermes-gateway.service --no-pager 2>&1 | sanitize || true
  echo ""

  echo "## Git Backup"
  if [ -d /root/hermano-backup/.git ]; then
    cd /root/hermano-backup
    echo "BACKUP_ROOT_EXISTS=YES"
    echo "GIT_BRANCH=$(git branch --show-current 2>/dev/null || true)"
    echo "GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || true)"
    echo "GIT_REMOTE=$(git remote get-url origin 2>/dev/null || true)"
  else
    echo "BACKUP_ROOT_EXISTS=NO"
    FAIL=1
  fi
  echo ""

  echo "## Critical Files"
  for f in \
    /root/.hermes/model_routing/routing_policy.yaml \
    /usr/local/lib/hermes-agent/tools/cronjob_tools.py \
    /usr/local/lib/hermes-agent/cron/scheduler.py \
    /usr/local/lib/hermes-agent/cron/jobs.py \
    /root/.hermes/scripts/hermes_rich_output_execute.py \
    /root/.hermes/scripts/hermes_rich_batch_execute.py \
    /root/.hermes/scripts/telegram_artifact_prerouter.py \
    /root/.hermes/scripts/hermes_media_verify.py \
    /root/.hermes/scripts/hermes_visual_asset_router.py \
    /root/.hermes/scripts/hermes_lesson_phrase_normalizer.py
  do
    check_file "$f"
  done
  echo ""

  echo "## Python Syntax"
  for f in \
    /usr/local/lib/hermes-agent/tools/cronjob_tools.py \
    /usr/local/lib/hermes-agent/cron/scheduler.py \
    /usr/local/lib/hermes-agent/cron/jobs.py \
    /root/.hermes/scripts/hermes_rich_output_execute.py \
    /root/.hermes/scripts/hermes_rich_batch_execute.py \
    /root/.hermes/scripts/telegram_artifact_prerouter.py \
    /root/.hermes/scripts/hermes_media_verify.py \
    /root/.hermes/scripts/hermes_visual_asset_router.py \
    /root/.hermes/scripts/hermes_lesson_phrase_normalizer.py
  do
    if [ -f "$f" ]; then check_py "$f"; fi
  done
  echo ""

  echo "## Reminder Regression"
  if [ -x /root/.hermes/scripts/hermes_reminder_create_test.py ]; then
    /root/.hermes/scripts/hermes_reminder_create_test.py 2>&1 | sanitize || FAIL=1
  else
    echo "REMINDER_CREATE_TEST=SKIPPED_MISSING"
    FAIL=1
  fi
  if [ -x /root/.hermes/scripts/hermes_reminder_delivery_test.py ]; then
    /root/.hermes/scripts/hermes_reminder_delivery_test.py 2>&1 | sanitize || FAIL=1
  else
    echo "REMINDER_DELIVERY_TEST=SKIPPED_MISSING"
    FAIL=1
  fi
  echo "REAL_TELEGRAM_SPAM_TEST=SKIPPED_BY_DESIGN"
  echo ""

  echo "## Disk And Memory"
  df -h / 2>&1 | sanitize || true
  free -h 2>&1 | sanitize || true
  echo ""

  echo "## Gateway Logs"
  journalctl -u hermes-gateway.service -n 80 --no-pager 2>&1 | sanitize || true
  echo ""

  echo "## Cron Status"
  if command -v hermes >/dev/null 2>&1; then
    echo "HERMES_COMMAND=FOUND"
  else
    echo "HERMES_COMMAND=NOT_FOUND"
  fi
  python3 - <<'PY' 2>&1 | sed -E 's/telegram:-?[0-9]+(:[0-9]+)?/telegram:<chat_id_masked>/g'
import json, sys
sys.path.insert(0, '/usr/local/lib/hermes-agent')
try:
    from cron.jobs import list_jobs
    jobs = list_jobs(include_disabled=True)
    print('CRON_JOB_COUNT=' + str(len(jobs)))
    for j in jobs[-12:]:
        deliver = str(j.get('deliver') or '')
        if deliver.startswith('telegram:'):
            deliver = 'telegram:<chat_id_masked>'
        print(json.dumps({
            'id': j.get('id'),
            'name': j.get('name'),
            'state': j.get('state'),
            'enabled': j.get('enabled'),
            'next_run_at': j.get('next_run_at'),
            'last_status': j.get('last_status'),
            'deliver': deliver,
        }, ensure_ascii=False))
except Exception as exc:
    print('CRON_LIST_FAILED=' + type(exc).__name__ + ':' + str(exc))
PY
  echo ""

  if [ "$FAIL" -eq 0 ]; then
    echo "OPS_HEALTHCHECK=PASSED"
  else
    echo "NOT VERIFIED"
  fi
} | tee "$TMP" >/dev/null

mv "$TMP" "$REPORT"
if grep -q '^OPS_HEALTHCHECK=PASSED$' "$REPORT"; then
  echo "OPS_HEALTHCHECK=PASSED"
  exit 0
fi

echo "NOT VERIFIED"
grep -E 'FAILED|MISSING|NOT VERIFIED|GATEWAY_ACTIVE=' "$REPORT" | tail -40
exit 1
