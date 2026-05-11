# Hermes Ops Healthcheck (deep)
Generated: 2026-05-11T12:08:00+00:00
MODE=deep

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
Mem:           1.8Gi       1.4Gi       127Mi       688Mi       1.2Gi       467Mi
Swap:             0B          0B          0B

## Recent Gateway Fatal/Error Scan
GATEWAY_RECENT_CRITICAL_LOGS=NONE

## Deep Python Syntax
PY_COMPILE_OK=/root/.hermes/scripts/hermes_rich_output_execute.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_rich_batch_execute.py
PY_COMPILE_OK=/root/.hermes/scripts/telegram_artifact_prerouter.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_media_verify.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_visual_asset_router.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_lesson_phrase_normalizer.py

## Reminder Regression
REMINDER_CREATE_TEST=PASSED
JOB_ID=b464b689c49b
EXPECTED=2026-05-11T20:10:00.702555+08:00
ACTUAL=2026-05-11T20:10:00.703743+08:00
DELTA_SECONDS=0.001188
TIMEZONE=Asia/Shanghai
JOB_ID=ad7732a0a1a2
WAITING_FOR_DUE=70_SECONDS
SCHEDULER_TICK_RAN=1
JOB_STATE=completed
JOB_LAST_STATUS=ok
JOB_LAST_ERROR=None
JOB_LAST_DELIVERY_ERROR=None
DELIVERY_PATH_VERIFIED=LOCAL_EXECUTION_COMPLETED
REMINDER_DELIVERY_TEST=PASSED
REAL_TELEGRAM_SPAM_TEST=SKIPPED_BY_DESIGN

## Git Backup Details
GIT_BRANCH=main
GIT_COMMIT=00e19aa2ab63722ca96af68fb30f14d390084299
GIT_REMOTE=git@github.com-hermes:guccipablo007/the-hermano.git

## Gateway Status
● hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration
     Loaded: loaded (/etc/systemd/system/hermes-gateway.service; enabled; preset: enabled)
    Drop-In: /etc/systemd/system/hermes-gateway.service.d
             └─30-ops-healthcheck.conf
     Active: active (running) since Mon 2026-05-11 11:49:16 UTC; 19min ago
 Invocation: f93e6c9267ad41679504f63676dbbcda
    Process: 92808 ExecStartPost=/bin/bash -lc systemd-run --unit=hermes-ops-startup-healthcheck --property=Type=oneshot --on-active=20s /usr/local/bin/hermes_ops_startup_healthcheck >/dev/null 2>&1 || true (code=exited, status=0/SUCCESS)
   Main PID: 92807 (python)
      Tasks: 5 (limit: 1141)
     Memory: 172.6M (peak: 179.3M)
        CPU: 4.983s
     CGroup: /system.slice/hermes-gateway.service
             └─92807 /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace

May 11 11:49:16 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:49:16 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.

## Gateway Logs
May 11 09:35:30 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 09:35:30 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 09:35:30 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 09:35:30 ubuntu systemd[1]: hermes-gateway.service: Consumed 1min 39.798s CPU time over 23h 47min 35.985s wall clock time, 239M memory peak.
May 11 09:35:30 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 09:55:30 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 09:55:30 ubuntu python[82920]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 09:55:30 ubuntu python[82920]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 09:55:30 ubuntu python[82920]:   root       84038  0.0  0.4  20204  8004 ?        S    09:55   0:00 systemctl restart hermes-gateway.service
May 11 09:55:31 ubuntu python[82920]: ┌─────────────────────────────────────────────────────────┐
May 11 09:55:31 ubuntu python[82920]: │           ⚕ Hermes Gateway Starting...                 │
May 11 09:55:31 ubuntu python[82920]: ├─────────────────────────────────────────────────────────┤
May 11 09:55:31 ubuntu python[82920]: │  Messaging platforms + cron scheduler                    │
May 11 09:55:31 ubuntu python[82920]: │  Press Ctrl+C to stop                                   │
May 11 09:55:31 ubuntu python[82920]: └─────────────────────────────────────────────────────────┘
May 11 09:55:32 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 09:55:32 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 09:55:32 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 09:55:32 ubuntu systemd[1]: hermes-gateway.service: Consumed 5.831s CPU time over 20min 1.881s wall clock time, 206.6M memory peak.
May 11 09:55:32 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 10:33:35 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 10:33:35 ubuntu python[84042]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 10:33:35 ubuntu python[84042]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 10:33:35 ubuntu python[84042]:   root       88778  0.0  0.2   7944  3856 ?        Ss   10:32   0:00 bash -c  set -e python3 -m py_compile /usr/local/lib/hermes-agent/tools/cronjob_tools.py python3 -m py_compile /usr/local/lib/hermes-agent/cron/scheduler.py python3 -m py_compile /usr/local/lib/hermes-agent/cron/jobs.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_create_test.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_delivery_test.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_telegram_delivery_test.py echo SYNTAX_CHECKS=PASSED /root/.hermes/scripts/hermes_reminder_create_test.py | tee /tmp/phase7ca3_create_test_final.txt /root/.hermes/scripts/hermes_reminder_delivery_test.py | tee /tmp/phase7ca3_local_delivery_test_final.txt systemctl restart hermes-gateway.service sleep 4 GW=$(systemctl is-active hermes-gateway.service) echo GATEWAY_STATUS=$GW python3 - <<'PY' import yaml from pathlib import Path data = yaml.safe_load(Path('/root/.hermes/config.yaml').read_text()) or {} model = data.get('model', {}) print('primary_provider:', model.get('provider') if isinstance(model, dict) else None) print('primary_model:', model.get('model') if isinstance(model, dict) else model) print('default_model:', model.get('default') if isinstance(model, dict) else None) PY
May 11 10:33:35 ubuntu python[84042]:   root       88798  0.0  0.4  20204  7916 ?        S    10:33   0:00 systemctl restart hermes-gateway.service
May 11 10:33:39 ubuntu python[84042]: ┌─────────────────────────────────────────────────────────┐
May 11 10:33:39 ubuntu python[84042]: │           ⚕ Hermes Gateway Starting...                 │
May 11 10:33:39 ubuntu python[84042]: ├─────────────────────────────────────────────────────────┤
May 11 10:33:39 ubuntu python[84042]: │  Messaging platforms + cron scheduler                    │
May 11 10:33:39 ubuntu python[84042]: │  Press Ctrl+C to stop                                   │
May 11 10:33:39 ubuntu python[84042]: └─────────────────────────────────────────────────────────┘
May 11 10:33:39 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 10:33:39 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 10:33:39 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 10:33:39 ubuntu systemd[1]: hermes-gateway.service: Consumed 6.620s CPU time over 38min 7.475s wall clock time, 179.7M memory peak.
May 11 10:33:39 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 10:49:45 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 10:49:45 ubuntu python[88802]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 10:49:45 ubuntu python[88802]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 10:49:45 ubuntu python[88802]:   root       89609  0.0  0.1   7944  3788 ?        Ss   10:48   0:00 bash -c  set -e python3 -m py_compile /usr/local/lib/hermes-agent/tools/cronjob_tools.py python3 -m py_compile /usr/local/lib/hermes-agent/cron/scheduler.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_create_test.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_delivery_test.py python3 -m py_compile /root/.hermes/scripts/hermes_reminder_telegram_delivery_test.py python3 -m py_compile /root/.hermes/scripts/hermes_live_reminder_same_path_test.py echo SYNTAX_CHECKS=PASSED /root/.hermes/scripts/hermes_reminder_create_test.py | tee /tmp/phase7ca4_create_test.txt /root/.hermes/scripts/hermes_reminder_delivery_test.py | tee /tmp/phase7ca4_local_delivery_test.txt /root/.hermes/scripts/hermes_reminder_telegram_delivery_test.py | tee /tmp/phase7ca4_direct_telegram_test.txt systemctl restart hermes-gateway.service sleep 5 echo GATEWAY_STATUS=$(systemctl is-active hermes-gateway.service)
May 11 10:49:45 ubuntu python[88802]:   root       89633  0.0  0.4  20204  7984 ?        S    10:49   0:00 systemctl restart hermes-gateway.service
May 11 10:49:46 ubuntu python[88802]: ┌─────────────────────────────────────────────────────────┐
May 11 10:49:46 ubuntu python[88802]: │           ⚕ Hermes Gateway Starting...                 │
May 11 10:49:46 ubuntu python[88802]: ├─────────────────────────────────────────────────────────┤
May 11 10:49:46 ubuntu python[88802]: │  Messaging platforms + cron scheduler                    │
May 11 10:49:46 ubuntu python[88802]: │  Press Ctrl+C to stop                                   │
May 11 10:49:46 ubuntu python[88802]: └─────────────────────────────────────────────────────────┘
May 11 10:49:46 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 10:49:46 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 10:49:46 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 10:49:46 ubuntu systemd[1]: hermes-gateway.service: Consumed 5.279s CPU time over 16min 6.927s wall clock time, 223M memory peak.
May 11 10:49:46 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:03:00 ubuntu crontab[89995]: (root) LIST (root)
May 11 11:16:30 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:16:30 ubuntu python[89637]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 11:16:30 ubuntu python[89637]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 11:16:30 ubuntu python[89637]:   root       90673  0.0  0.1   7944  3748 ?        Ss   11:16   0:00 bash -c  set -e systemctl restart hermes-gateway.service sleep 5 echo GATEWAY_STATUS=$(systemctl is-active hermes-gateway.service) hermes_ops_healthcheck | tee /tmp/phase7cb_health_after.txt /root/.hermes/scripts/hermes_reminder_create_test.py | tee /tmp/phase7cb_reminder_create.txt /root/.hermes/scripts/hermes_reminder_delivery_test.py | tee /tmp/phase7cb_reminder_delivery.txt cd /root/hermano-backup && echo LATEST_GIT_COMMIT=$(git rev-parse HEAD) python3 - <<'PY' import yaml from pathlib import Path data=yaml.safe_load(Path('/root/.hermes/config.yaml').read_text()) or {} model=data.get('model', {}) print('DEFAULT_PROVIDER=' + str(model.get('provider') if isinstance(model, dict) else None)) print('DEFAULT_MODEL=' + str(model.get('default') if isinstance(model, dict) else model)) PY
May 11 11:16:30 ubuntu python[89637]:   root       90674  0.0  0.4  20204  7916 ?        S    11:16   0:00 systemctl restart hermes-gateway.service
May 11 11:16:35 ubuntu python[89637]: ┌─────────────────────────────────────────────────────────┐
May 11 11:16:35 ubuntu python[89637]: │           ⚕ Hermes Gateway Starting...                 │
May 11 11:16:35 ubuntu python[89637]: ├─────────────────────────────────────────────────────────┤
May 11 11:16:35 ubuntu python[89637]: │  Messaging platforms + cron scheduler                    │
May 11 11:16:35 ubuntu python[89637]: │  Press Ctrl+C to stop                                   │
May 11 11:16:35 ubuntu python[89637]: └─────────────────────────────────────────────────────────┘
May 11 11:16:35 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 11:16:35 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 11:16:35 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:16:35 ubuntu systemd[1]: hermes-gateway.service: Consumed 6.442s CPU time over 26min 48.885s wall clock time, 193.9M memory peak.
May 11 11:16:35 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:29:09 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:29:09 ubuntu python[90678]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 11:29:09 ubuntu python[90678]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 11:29:09 ubuntu python[90678]:   root       91458  0.0  0.1   7944  3772 ?        Ss   11:29   0:00 bash -c  set -e BEFORE_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) systemctl restart hermes-gateway.service sleep 95 GW=$(systemctl is-active hermes-gateway.service) echo GATEWAY_STATUS=$GW AFTER_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) echo STARTUP_STATUS_MTIME_BEFORE=$BEFORE_TS echo STARTUP_STATUS_MTIME_AFTER=$AFTER_TS if [ "$AFTER_TS" -gt "$BEFORE_TS" ]; then echo EXECSTARTPOST_RAN=YES; else echo EXECSTARTPOST_RAN=NO; fi grep -E 'STARTUP_OPS_HEALTHCHECK=|TELEGRAM_STARTUP_ALERT=|timestamp:' /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md || true tail -80 /root/.hermes/rebuild_notes/startup_healthcheck_systemd.log | sed -E 's/(bot[0-9]+:)[A-Za-z0-9_-]+/\1<REDACTED>/g; s/(Bearer )[A-Za-z0-9._-]+/\1<REDACTED>/g; s/telegram:-?[0-9]+(:[0-9]+)?/telegram:<chat_id_masked>/g' | grep -E 'STARTUP_OPS_HEALTHCHECK=|OPS_HEALTHCHECK=|TELEGRAM_STARTUP_ALERT=' || true journalctl -u hermes-gateway.service -n 120 --no-pager | sed -E 's/(bot[0-9]+:)[A-Za-z0-9_-]+/\1<REDACTED>/g; s/(Bearer )[A-Za-z0-9._-]+/\1<REDACTED>/g' | tail -30 hermes_ops_healthcheck | tee /tmp/phase7cc_health_after_restart.txt /root/.hermes/scripts/hermes_reminder_create_test.py | tee /tmp/phase7cc_reminder_create.txt /root/.hermes/scripts/hermes_reminder_delivery_test.py | tee /tmp/phase7cc_reminder_delivery.txt cd /root/hermano-backup && echo LATEST_GIT_COMMIT=$(git rev-parse HEAD) python3 - <<'PY' import yaml from pathlib import Path data=yaml.safe_load(Path('/root/.hermes/config.yaml').read_text()) or {} model=data.get('model', {}) print('DEFAULT_PROVIDER=' + str(model.get('provider') if isinstance(model, dict) else None)) print('DEFAULT_MODEL=' + str(model.get('default') if isinstance(model, dict) else model)) PY
May 11 11:29:09 ubuntu python[90678]:   root       91461  0.0  0.4  20204  7976 ?        S    11:29   0:00 systemctl restart hermes-gateway.service
May 11 11:29:10 ubuntu python[90678]: ┌─────────────────────────────────────────────────────────┐
May 11 11:29:10 ubuntu python[90678]: │           ⚕ Hermes Gateway Starting...                 │
May 11 11:29:10 ubuntu python[90678]: ├─────────────────────────────────────────────────────────┤
May 11 11:29:10 ubuntu python[90678]: │  Messaging platforms + cron scheduler                    │
May 11 11:29:10 ubuntu python[90678]: │  Press Ctrl+C to stop                                   │
May 11 11:29:10 ubuntu python[90678]: └─────────────────────────────────────────────────────────┘
May 11 11:29:10 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 11:29:10 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 11:29:10 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:29:10 ubuntu systemd[1]: hermes-gateway.service: Consumed 3.020s CPU time over 12min 34.976s wall clock time, 162.6M memory peak.
May 11 11:29:10 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:30:27 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:35:14 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:35:14 ubuntu python[91465]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 11:35:14 ubuntu python[91465]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 11:35:14 ubuntu python[91465]:   root       91946  0.0  0.2   7944  3868 ?        Ss   11:35   0:00 bash -c  set -e BEFORE_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) systemctl restart hermes-gateway.service sleep 55 GW=$(systemctl is-active hermes-gateway.service) echo GATEWAY_STATUS=$GW AFTER_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) echo STARTUP_STATUS_MTIME_BEFORE=$BEFORE_TS echo STARTUP_STATUS_MTIME_AFTER=$AFTER_TS if [ "$AFTER_TS" -gt "$BEFORE_TS" ]; then echo EXECSTARTPOST_RAN=YES; else echo EXECSTARTPOST_RAN=NO; fi grep -E 'STARTUP_OPS_HEALTHCHECK=|TELEGRAM_STARTUP_ALERT=|timestamp:' /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md || true systemctl status hermes-ops-startup-healthcheck --no-pager 2>/dev/null | tail -30 || true hermes_ops_healthcheck | tee /tmp/phase7cc_health_after_restart2.txt /root/.hermes/scripts/hermes_reminder_create_test.py | tee /tmp/phase7cc_reminder_create2.txt /root/.hermes/scripts/hermes_reminder_delivery_test.py | tee /tmp/phase7cc_reminder_delivery2.txt cd /root/hermano-backup && echo LATEST_GIT_COMMIT=$(git rev-parse HEAD)
May 11 11:35:14 ubuntu python[91465]:   root       91949  0.0  0.4  20204  8012 ?        S    11:35   0:00 systemctl restart hermes-gateway.service
May 11 11:35:15 ubuntu python[91465]: ┌─────────────────────────────────────────────────────────┐
May 11 11:35:15 ubuntu python[91465]: │           ⚕ Hermes Gateway Starting...                 │
May 11 11:35:15 ubuntu python[91465]: ├─────────────────────────────────────────────────────────┤
May 11 11:35:15 ubuntu python[91465]: │  Messaging platforms + cron scheduler                    │
May 11 11:35:15 ubuntu python[91465]: │  Press Ctrl+C to stop                                   │
May 11 11:35:15 ubuntu python[91465]: └─────────────────────────────────────────────────────────┘
May 11 11:35:16 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 11:35:16 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 11:35:16 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:35:16 ubuntu systemd[1]: hermes-gateway.service: Consumed 4.054s CPU time over 6min 5.425s wall clock time, 145.9M memory peak.
May 11 11:35:16 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:35:16 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:49:15 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:49:15 ubuntu python[91953]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 11:49:15 ubuntu python[91953]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:33 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 11:49:15 ubuntu python[91953]:   root       92800  0.0  0.1   7944  3784 ?        Ss   11:49   0:00 bash -c  set -e BEFORE_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) systemctl restart hermes-gateway.service sleep 45 GW=$(systemctl is-active hermes-gateway.service) echo GATEWAY_STATUS=$GW AFTER_TS=$(stat -c %Y /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md 2>/dev/null || echo 0) echo STARTUP_STATUS_MTIME_BEFORE=$BEFORE_TS echo STARTUP_STATUS_MTIME_AFTER=$AFTER_TS if [ "$AFTER_TS" -gt "$BEFORE_TS" ]; then echo EXECSTARTPOST_RAN=YES; else echo EXECSTARTPOST_RAN=NO; fi grep -E 'STARTUP_OPS_HEALTHCHECK_QUICK=|STARTUP_OPS_HEALTHCHECK=|TELEGRAM_STARTUP_ALERT=|timestamp:' /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md || true tail -60 /root/.hermes/rebuild_notes/startup_healthcheck_systemd.log | sed -E 's/(bot[0-9]+:)[A-Za-z0-9_-]+/\1<REDACTED>/g; s/(Bearer )[A-Za-z0-9._-]+/\1<REDACTED>/g; s/telegram:-?[0-9]+(:[0-9]+)?/telegram:<chat_id_masked>/g' | grep -E 'STARTUP_OPS_HEALTHCHECK_QUICK=|OPS_HEALTHCHECK_QUICK=|TELEGRAM_STARTUP_ALERT=' || true systemctl is-active hermes-gateway.service cd /root/hermano-backup && echo LATEST_GIT_COMMIT=$(git rev-parse HEAD)
May 11 11:49:15 ubuntu python[91953]:   root       92803  0.0  0.4  20204  7964 ?        S    11:49   0:00 systemctl restart hermes-gateway.service
May 11 11:49:16 ubuntu python[91953]: ┌─────────────────────────────────────────────────────────┐
May 11 11:49:16 ubuntu python[91953]: │           ⚕ Hermes Gateway Starting...                 │
May 11 11:49:16 ubuntu python[91953]: ├─────────────────────────────────────────────────────────┤
May 11 11:49:16 ubuntu python[91953]: │  Messaging platforms + cron scheduler                    │
May 11 11:49:16 ubuntu python[91953]: │  Press Ctrl+C to stop                                   │
May 11 11:49:16 ubuntu python[91953]: └─────────────────────────────────────────────────────────┘
May 11 11:49:16 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 11 11:49:16 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 11 11:49:16 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 11:49:16 ubuntu systemd[1]: hermes-gateway.service: Consumed 5.109s CPU time over 14min 820ms wall clock time, 161.8M memory peak.
May 11 11:49:16 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 11:49:16 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.

## Cron Status
HERMES_COMMAND=FOUND
CRON_JOB_COUNT=55
{"id": "b2727000ba71", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "0485c1d2320f", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "5fb2dd447e82", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "f9a0e04ad687", "name": "Reminder: Test reminder delivery", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "telegram:<chat_id_masked>"}
{"id": "5214518c0c03", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "3bf0c988a11f", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "ac3e268bfa57", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "767237b4f688", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "ff8795e9f7bb", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "3071ec85c97c", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "b464b689c49b", "name": "phase7ca_reminder_create_test", "state": "scheduled", "enabled": true, "next_run_at": "2026-05-11T20:10:00.703743+08:00", "last_status": null, "deliver": "local"}
{"id": "ad7732a0a1a2", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}

## Shellcheck
SHELLCHECK=SKIPPED_NOT_INSTALLED

OPS_HEALTHCHECK_DEEP=PASSED
