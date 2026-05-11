#!/usr/bin/env bash
set +e

STATUS_FILE="/root/.hermes/rebuild_notes/startup_healthcheck_last_status.md"
LOG_FILE="/root/.hermes/rebuild_notes/startup_healthcheck_systemd.log"
TMP_OUT="/tmp/hermes_startup_healthcheck.$$"
mkdir -p /root/.hermes/rebuild_notes

sanitize() {
  sed -E \
    -e 's/(bot[0-9]+:)[A-Za-z0-9_-]+/\1<REDACTED>/g' \
    -e 's/(Bearer )[A-Za-z0-9._-]+/\1<REDACTED>/g' \
    -e 's/telegram:-?[0-9]+(:[0-9]+)?/telegram:<chat_id_masked>/g' \
    -e 's/(api[_-]?key[=: ]+)[^[:space:]]+/\1<REDACTED>/Ig' \
    -e 's/(token[=: ]+)[^[:space:]]+/\1<REDACTED>/Ig'
}

{
  echo "=== Hermes startup quick healthcheck wrapper ==="
  echo "START_TIME=$(date -Is)"
  echo "MODE=quick"
  echo "SLEEP_SECONDS=5"
} >> "$LOG_FILE"

sleep 5
/usr/local/bin/hermes_ops_healthcheck --quick > "$TMP_OUT" 2>&1
HC_RC=$?
SANITIZED="$(sanitize < "$TMP_OUT")"
printf '%s\n' "$SANITIZED" >> "$LOG_FILE"
TS="$(date -Is)"
if [ "$HC_RC" -eq 0 ] && printf '%s\n' "$SANITIZED" | grep -q '^OPS_HEALTHCHECK_QUICK=PASSED$'; then
  {
    echo "# Hermes Startup Healthcheck Status"
    echo "timestamp: $TS"
    echo "STARTUP_OPS_HEALTHCHECK_QUICK=PASSED"
    echo "TELEGRAM_STARTUP_ALERT=SKIPPED_NOT_NEEDED"
  } > "$STATUS_FILE"
  echo "STARTUP_OPS_HEALTHCHECK_QUICK=PASSED timestamp=$TS" >> "$LOG_FILE"
else
  SUMMARY="$(printf '%s\n' "$SANITIZED" | grep -E 'NOT VERIFIED|FAILED|MISSING|GATEWAY_ACTIVE=' | head -8 | tr '\n' '; ' | cut -c1-500)"
  [ -n "$SUMMARY" ] || SUMMARY="quick healthcheck failed; run hermes_ops_healthcheck --deep for details"
  {
    echo "# Hermes Startup Healthcheck Status"
    echo "timestamp: $TS"
    echo "STARTUP_OPS_HEALTHCHECK_QUICK=NOT_VERIFIED"
    echo "summary: $SUMMARY"
    echo "TELEGRAM_STARTUP_ALERT=NOT_VERIFIED"
  } > "$STATUS_FILE"
  echo "STARTUP_OPS_HEALTHCHECK_QUICK=NOT_VERIFIED timestamp=$TS summary=$SUMMARY" >> "$LOG_FILE"
  echo "TELEGRAM_STARTUP_ALERT=NOT_VERIFIED" >> "$LOG_FILE"
fi
rm -f "$TMP_OUT"
exit 0
