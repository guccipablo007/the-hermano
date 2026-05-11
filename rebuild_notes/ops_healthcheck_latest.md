# Hermes Ops Healthcheck
Generated: 2026-05-11T11:16:40+00:00

## Gateway Service
GATEWAY_ACTIVE=active
● hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration
     Loaded: loaded (/etc/systemd/system/hermes-gateway.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-11 11:16:35 UTC; 5s ago
 Invocation: 40a5cce19de64436bf422468438f4eaf
   Main PID: 90678 (python)
      Tasks: 4 (limit: 1141)
     Memory: 148.5M (peak: 162.6M)
        CPU: 1.648s
     CGroup: /system.slice/hermes-gateway.service
             └─90678 /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace

May 11 11:16:35 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.

## Git Backup
BACKUP_ROOT_EXISTS=YES
GIT_BRANCH=main
GIT_COMMIT=68bd47924f6f39474e8debb2c566d31f5866f0ee
GIT_REMOTE=git@github.com-hermes:guccipablo007/the-hermano.git

## Critical Files
FILE_OK=/root/.hermes/model_routing/routing_policy.yaml
FILE_OK=/usr/local/lib/hermes-agent/tools/cronjob_tools.py
FILE_OK=/usr/local/lib/hermes-agent/cron/scheduler.py
FILE_OK=/usr/local/lib/hermes-agent/cron/jobs.py
FILE_OK=/root/.hermes/scripts/hermes_rich_output_execute.py
FILE_OK=/root/.hermes/scripts/hermes_rich_batch_execute.py
FILE_OK=/root/.hermes/scripts/telegram_artifact_prerouter.py
FILE_OK=/root/.hermes/scripts/hermes_media_verify.py
FILE_OK=/root/.hermes/scripts/hermes_visual_asset_router.py
FILE_OK=/root/.hermes/scripts/hermes_lesson_phrase_normalizer.py

## Python Syntax
PY_COMPILE_OK=/usr/local/lib/hermes-agent/tools/cronjob_tools.py
PY_COMPILE_OK=/usr/local/lib/hermes-agent/cron/scheduler.py
PY_COMPILE_OK=/usr/local/lib/hermes-agent/cron/jobs.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_rich_output_execute.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_rich_batch_execute.py
PY_COMPILE_OK=/root/.hermes/scripts/telegram_artifact_prerouter.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_media_verify.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_visual_asset_router.py
PY_COMPILE_OK=/root/.hermes/scripts/hermes_lesson_phrase_normalizer.py

## Reminder Regression
REMINDER_CREATE_TEST=PASSED
JOB_ID=65afe74a125f
EXPECTED=2026-05-11T19:18:41.285803+08:00
ACTUAL=2026-05-11T19:18:41.287126+08:00
DELTA_SECONDS=0.001323
TIMEZONE=Asia/Shanghai
JOB_ID=5f2d776a3e44
WAITING_FOR_DUE=70_SECONDS
SCHEDULER_TICK_RAN=1
JOB_STATE=completed
JOB_LAST_STATUS=ok
JOB_LAST_ERROR=None
JOB_LAST_DELIVERY_ERROR=None
DELIVERY_PATH_VERIFIED=LOCAL_EXECUTION_COMPLETED
REMINDER_DELIVERY_TEST=PASSED
REAL_TELEGRAM_SPAM_TEST=SKIPPED_BY_DESIGN

## Disk And Memory
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        77G  7.4G   70G  10% /
               total        used        free      shared  buff/cache   available
Mem:           1.8Gi       1.3Gi       118Mi       687Mi       1.2Gi       525Mi
Swap:             0B          0B          0B

## Gateway Logs
May 10 09:47:54 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 11 09:35:29 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 11 09:35:29 ubuntu python[71338]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 11 09:35:29 ubuntu python[71338]:   root       24733  0.0  1.4 146236 27940 ?        Ss   May08   0:32 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 11 09:35:29 ubuntu python[71338]:   root       82916  0.0  0.4  20204  8012 ?        S    09:35   0:00 systemctl restart hermes-gateway.service
May 11 09:35:29 ubuntu python[71338]: ┌─────────────────────────────────────────────────────────┐
May 11 09:35:29 ubuntu python[71338]: │           ⚕ Hermes Gateway Starting...                 │
May 11 09:35:29 ubuntu python[71338]: ├─────────────────────────────────────────────────────────┤
May 11 09:35:29 ubuntu python[71338]: │  Messaging platforms + cron scheduler                    │
May 11 09:35:29 ubuntu python[71338]: │  Press Ctrl+C to stop                                   │
May 11 09:35:29 ubuntu python[71338]: └─────────────────────────────────────────────────────────┘
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

## Cron Status
HERMES_COMMAND=FOUND
CRON_JOB_COUNT=30
{"id": "ac0a82f273a3", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "07593c2eab61", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "80d60399325d", "name": "Reminder: Confirm final reminder fix", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "telegram:<chat_id_masked>"}
{"id": "744381c8d028", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "e3a8154ddc87", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "b8357b8c0435", "name": "Telegram real delivery verification", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "telegram:<chat_id_masked>"}
{"id": "0f02f1f9d533", "name": "Reminder: Live same-path scheduler test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "telegram:<chat_id_masked>"}
{"id": "1e9accf858c9", "name": "Reminder: Prove Hermes reminders are finally fixed", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "telegram:<chat_id_masked>"}
{"id": "371a9668f47e", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "41a5a1a382b8", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "65afe74a125f", "name": "phase7ca_reminder_create_test", "state": "scheduled", "enabled": true, "next_run_at": "2026-05-11T19:18:41.287126+08:00", "last_status": null, "deliver": "local"}
{"id": "5f2d776a3e44", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}

OPS_HEALTHCHECK=PASSED
