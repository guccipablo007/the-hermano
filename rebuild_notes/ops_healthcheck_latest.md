# Hermes Ops Healthcheck (quick)
Generated: 2026-05-15T15:30:13+00:00
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
/dev/vda1        77G  7.5G   69G  10% /
               total        used        free      shared  buff/cache   available
Mem:           1.8Gi       1.4Gi       102Mi       689Mi       1.1Gi       385Mi
Swap:             0B          0B          0B

## Recent Gateway Fatal/Error Scan
May 14 15:58:09 ubuntu python[151426]:     self.gen.throw(typ, value, traceback)
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
GATEWAY_RECENT_CRITICAL_LOGS=NONE

OPS_HEALTHCHECK_QUICK=PASSED
