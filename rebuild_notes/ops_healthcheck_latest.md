# Hermes Ops Healthcheck (quick)
Generated: 2026-05-11T12:33:49+00:00
MODE=quick

## Gateway Active
GATEWAY_ACTIVE=active

## Git Backup Presence
BACKUP_ROOT_EXISTS=YES

## Critical Files
FILE_OK=/root/.hermes/model_routing/routing_policy.yaml
FILE_OK=/usr/local/lib/hermes-agent/tools/cronjob_tools.py
FILE_OK=/usr/local/lib/hermes-agent/cron/scheduler.py
FILE_OK=/usr/local/lib/hermes-agent/cron/jobs.py
FILE_OK=/root/.hermes/scripts/hermes_rich_output_execute.py
FILE_OK=/root/.hermes/scripts/telegram_artifact_prerouter.py
FILE_OK=/root/.hermes/scripts/hermes_media_verify.py

## Critical Python Syntax
PY_COMPILE_OK=/usr/local/lib/hermes-agent/tools/cronjob_tools.py
PY_COMPILE_OK=/usr/local/lib/hermes-agent/cron/scheduler.py
PY_COMPILE_OK=/usr/local/lib/hermes-agent/cron/jobs.py

## Disk And Memory
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        77G  7.4G   70G  10% /
               total        used        free      shared  buff/cache   available
Mem:           1.8Gi       1.3Gi       106Mi       688Mi       1.2Gi       492Mi
Swap:             0B          0B          0B

## Recent Gateway Fatal/Error Scan
May 11 12:33:22 ubuntu python[92807]:   root       96006  0.0  0.1   7944  3756 ?        Ss   12:33   0:00 bash -c  set -e echo "=== Restart gateway ===" systemctl restart hermes-gateway.service sleep 4 ACTIVE=$(systemctl is-active hermes-gateway.service) echo "GATEWAY_ACTIVE=$ACTIVE" echo "=== Post-restart quick healthcheck ===" set +e hermes_ops_healthcheck --quick >/tmp/phase7f_post_restart_quick.txt 2>&1 QRC=$? set -e echo "POST_RESTART_QUICK_RC=$QRC" grep -E "OPS_HEALTHCHECK_QUICK=PASSED|NOT VERIFIED" /tmp/phase7f_post_restart_quick.txt | tail -5 || true echo "=== Startup healthcheck status ===" if [ -f /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md ]; then   tail -20 /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md fi echo "=== Journal recent error scan ===" journalctl -u hermes-gateway.service -n 80 --no-pager | grep -Ei "btw|traceback|syntaxerror|failed|error" | tail -40 || true echo "=== Latest commit ===" cd /root/hermano-backup && git rev-parse HEAD
GATEWAY_RECENT_CRITICAL_LOGS=NONE

OPS_HEALTHCHECK_QUICK=PASSED
