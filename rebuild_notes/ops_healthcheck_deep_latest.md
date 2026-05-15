# Hermes Ops Healthcheck (deep)
Generated: 2026-05-15T16:06:50+00:00
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
/dev/vda1        77G  7.5G   69G  10% /
               total        used        free      shared  buff/cache   available
Mem:           1.8Gi       1.4Gi       120Mi       689Mi       1.2Gi       439Mi
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
JOB_ID=f4f1a7f00817
EXPECTED=2026-05-16T00:08:51.307589+08:00
ACTUAL=2026-05-16T00:08:51.308842+08:00
DELTA_SECONDS=0.001253
TIMEZONE=Asia/Shanghai
JOB_ID=1d56020484a1
WAITING_FOR_DUE=70_SECONDS
SCHEDULER_TICK_RAN=0
JOB_STATE=completed
JOB_LAST_STATUS=ok
JOB_LAST_ERROR=None
JOB_LAST_DELIVERY_ERROR=None
DELIVERY_PATH_VERIFIED=LOCAL_EXECUTION_COMPLETED
REMINDER_DELIVERY_TEST=PASSED
REAL_TELEGRAM_SPAM_TEST=SKIPPED_BY_DESIGN

## Git Backup Details
GIT_BRANCH=main
GIT_COMMIT=899df2a18a6f7b8219ccd4ead759218c1cc9dbb8
GIT_REMOTE=git@github.com-hermes:guccipablo007/the-hermano.git

## Gateway Status
● hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration
     Loaded: loaded (/etc/systemd/system/hermes-gateway.service; enabled; preset: enabled)
    Drop-In: /etc/systemd/system/hermes-gateway.service.d
             └─30-ops-healthcheck.conf
     Active: active (running) since Fri 2026-05-15 16:06:48 UTC; 1min 13s ago
 Invocation: c18517aaed9c4f839c5a2e56af6f2805
    Process: 206701 ExecStartPost=/bin/bash -lc systemd-run --unit=hermes-ops-startup-healthcheck --property=Type=oneshot --on-active=20s /usr/local/bin/hermes_ops_startup_healthcheck >/dev/null 2>&1 || true (code=exited, status=0/SUCCESS)
   Main PID: 206700 (python)
      Tasks: 5 (limit: 1141)
     Memory: 166.2M (peak: 178.3M)
        CPU: 1.862s
     CGroup: /system.slice/hermes-gateway.service
             └─206700 /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace

May 15 16:06:48 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 16:06:48 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.

## Gateway Logs
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/request/_httpxrequest.py", line 279, in do_request
May 14 15:58:09 ubuntu python[151426]:     res = await self._client.request(
May 14 15:58:09 ubuntu python[151426]:           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_client.py", line 1540, in request
May 14 15:58:09 ubuntu python[151426]:     return await self.send(request, auth=auth, follow_redirects=follow_redirects)
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_client.py", line 1629, in send
May 14 15:58:09 ubuntu python[151426]:     response = await self._send_handling_auth(
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_client.py", line 1657, in _send_handling_auth
May 14 15:58:09 ubuntu python[151426]:     response = await self._send_handling_redirects(
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_client.py", line 1694, in _send_handling_redirects
May 14 15:58:09 ubuntu python[151426]:     response = await self._send_single_request(request)
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_client.py", line 1730, in _send_single_request
May 14 15:58:09 ubuntu python[151426]:     response = await transport.handle_async_request(request)
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/gateway/platforms/telegram_network.py", line 114, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     raise last_error
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/gateway/platforms/telegram_network.py", line 88, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     response = await transport.handle_async_request(candidate)
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 393, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     with map_httpcore_exceptions():
May 14 15:58:09 ubuntu python[151426]:   File "/root/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/lib/python3.11/contextlib.py", line 158, in __exit__
May 14 15:58:09 ubuntu python[151426]:     self.gen.throw(typ, value, traceback)
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 118, in map_httpcore_exceptions
May 14 15:58:09 ubuntu python[151426]:     raise mapped_exc(message) from exc
May 14 15:58:09 ubuntu python[151426]: httpx.ConnectError: All connection attempts failed
May 14 15:58:09 ubuntu python[151426]: The above exception was the direct cause of the following exception:
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_utils/networkloop.py", line 161, in network_retry_loop
May 14 15:58:09 ubuntu python[151426]:     await do_action()
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_utils/networkloop.py", line 136, in do_action
May 14 15:58:09 ubuntu python[151426]:     await action_cb()
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_updater.py", line 686, in bootstrap_del_webhook
May 14 15:58:09 ubuntu python[151426]:     await self.bot.delete_webhook(drop_pending_updates=drop_pending_updates)
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 1490, in delete_webhook
May 14 15:58:09 ubuntu python[151426]:     return await super().delete_webhook(
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/_bot.py", line 5037, in delete_webhook
May 14 15:58:09 ubuntu python[151426]:     return await self._post(
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/_bot.py", line 704, in _post
May 14 15:58:09 ubuntu python[151426]:     return await self._do_post(
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 370, in _do_post
May 14 15:58:09 ubuntu python[151426]:     return await super()._do_post(
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/_bot.py", line 733, in _do_post
May 14 15:58:09 ubuntu python[151426]:     result = await request.post(
May 14 15:58:09 ubuntu python[151426]:              ^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 198, in post
May 14 15:58:09 ubuntu python[151426]:     result = await self._request_wrapper(
May 14 15:58:09 ubuntu python[151426]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 305, in _request_wrapper
May 14 15:58:09 ubuntu python[151426]:     code, payload = await self.do_request(
May 14 15:58:09 ubuntu python[151426]:                     ^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/telegram/request/_httpxrequest.py", line 303, in do_request
May 14 15:58:09 ubuntu python[151426]:     raise NetworkError(f"httpx.{err.__class__.__name__}: {err}") from err
May 14 15:58:09 ubuntu python[151426]: telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed
May 14 15:58:09 ubuntu python[151426]: WARNING gateway.platforms.telegram: [Telegram] Telegram polling reconnect failed: httpx.ConnectError: All connection attempts failed
May 14 15:58:09 ubuntu python[151426]: WARNING gateway.platforms.telegram: [Telegram] Telegram network error (attempt 2/10), reconnecting in 10s. Error: httpx.ConnectError: All connection attempts failed
May 14 15:58:19 ubuntu python[151426]: WARNING gateway.platforms.telegram_network: [Telegram] Primary api.telegram.org connection failed (All connection attempts failed); trying fallback IPs 149.154.166.110
May 14 15:58:19 ubuntu python[151426]: WARNING gateway.platforms.telegram_network: [Telegram] Primary api.telegram.org path unreachable; using sticky fallback IP 149.154.166.110
May 15 08:22:25 ubuntu python[151426]: WARNING gateway.platforms.telegram: [Telegram] Telegram network error, scheduling reconnect: httpx.ReadError:
May 15 08:22:25 ubuntu python[151426]: WARNING gateway.platforms.telegram: [Telegram] Telegram network error (attempt 1/10), reconnecting in 5s. Error: httpx.ReadError:
May 15 13:36:39 ubuntu python[151426]: WARNING gateway.platforms.base: [Telegram] Failed to send media (.pdf): File file not found: /tmp/hermes_outputs/first_electric_car_lesson.pdf
May 15 13:37:20 ubuntu python[151426]: WARNING gateway.platforms.base: [Telegram] Failed to send media (.pdf): File file not found: /tmp/hermes_outputs/first_electric_car_lesson.pdf
May 15 14:21:49 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 14:21:49 ubuntu python[151426]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 15 14:21:49 ubuntu python[151426]:   root       24733  0.0  1.6 170824 30420 ?        Ss   May08   1:17 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 15 14:21:49 ubuntu python[151426]:   root      194579  0.0  0.2   7944  3860 ?        Ss   14:21   0:00 bash -c set -e systemctl restart hermes-gateway.service sleep 5 echo GATEWAY_ACTIVE=$(systemctl is-active hermes-gateway.service) sleep 35 if [ -f /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md ]; then   echo '=== STARTUP_STATUS ==='   grep -E 'STARTUP_OPS_HEALTHCHECK_QUICK=|STARTUP_OPS_HEALTHCHECK=|TELEGRAM_STARTUP_ALERT=|timestamp:' /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md || true fi /usr/local/bin/hermes_ops_healthcheck --quick | sed -n '1,40p'
May 15 14:21:49 ubuntu python[151426]:   root      194580  0.0  0.4  20204  7880 ?        S    14:21   0:00 systemctl restart hermes-gateway.service
May 15 14:21:53 ubuntu python[151426]: ┌─────────────────────────────────────────────────────────┐
May 15 14:21:53 ubuntu python[151426]: │           ⚕ Hermes Gateway Starting...                 │
May 15 14:21:53 ubuntu python[151426]: ├─────────────────────────────────────────────────────────┤
May 15 14:21:53 ubuntu python[151426]: │  Messaging platforms + cron scheduler                    │
May 15 14:21:53 ubuntu python[151426]: │  Press Ctrl+C to stop                                   │
May 15 14:21:53 ubuntu python[151426]: └─────────────────────────────────────────────────────────┘
May 15 14:21:53 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 15 14:21:53 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 15 14:21:53 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 15 14:21:53 ubuntu systemd[1]: hermes-gateway.service: Consumed 3min 16.301s CPU time over 1d 22h 2min 49.421s wall clock time, 204.1M memory peak.
May 15 14:21:53 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 14:21:53 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 15 14:59:17 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 14:59:17 ubuntu python[194588]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 15 14:59:17 ubuntu python[194588]:   root       24733  0.0  1.6 170824 30420 ?        Ss   May08   1:17 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 15 14:59:17 ubuntu python[194588]:   root      199251  0.0  0.2   7944  3864 ?        Ss   14:59   0:00 bash -lc  set -e systemctl restart hermes-gateway.service systemctl is-active hermes-gateway.service journalctl -u hermes-gateway.service -n 120 --no-pager | rg 'STARTUP_OPS_HEALTHCHECK_QUICK=PASSED' || true /usr/local/bin/hermes_ops_healthcheck --quick cd /root/.hermes && hermes_prechange_backup
May 15 14:59:17 ubuntu python[194588]:   root      199266  0.0  0.4  20204  7944 ?        S    14:59   0:00 systemctl restart hermes-gateway.service
May 15 14:59:18 ubuntu python[194588]: ┌─────────────────────────────────────────────────────────┐
May 15 14:59:18 ubuntu python[194588]: │           ⚕ Hermes Gateway Starting...                 │
May 15 14:59:18 ubuntu python[194588]: ├─────────────────────────────────────────────────────────┤
May 15 14:59:18 ubuntu python[194588]: │  Messaging platforms + cron scheduler                    │
May 15 14:59:18 ubuntu python[194588]: │  Press Ctrl+C to stop                                   │
May 15 14:59:18 ubuntu python[194588]: └─────────────────────────────────────────────────────────┘
May 15 14:59:18 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 15 14:59:18 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 15 14:59:18 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 15 14:59:18 ubuntu systemd[1]: hermes-gateway.service: Consumed 8.725s CPU time over 37min 24.896s wall clock time, 286.2M memory peak.
May 15 14:59:18 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 14:59:18 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 15 16:06:47 ubuntu systemd[1]: Stopping hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 16:06:47 ubuntu python[199272]: WARNING gateway.run: Shutdown diagnostic — other hermes processes running:
May 15 16:06:47 ubuntu python[199272]:   root       24733  0.0  1.6 170824 30420 ?        Ss   May08   1:18 /usr/bin/python3 /root/.hermes/scripts/hermes_preview_server.py
May 15 16:06:47 ubuntu python[199272]:   root      206694  0.0  0.4  20204  7996 ?        Ss   16:06   0:00 systemctl restart hermes-gateway.service
May 15 16:06:47 ubuntu python[199272]: ┌─────────────────────────────────────────────────────────┐
May 15 16:06:47 ubuntu python[199272]: │           ⚕ Hermes Gateway Starting...                 │
May 15 16:06:47 ubuntu python[199272]: ├─────────────────────────────────────────────────────────┤
May 15 16:06:47 ubuntu python[199272]: │  Messaging platforms + cron scheduler                    │
May 15 16:06:47 ubuntu python[199272]: │  Press Ctrl+C to stop                                   │
May 15 16:06:47 ubuntu python[199272]: └─────────────────────────────────────────────────────────┘
May 15 16:06:48 ubuntu systemd[1]: hermes-gateway.service: Main process exited, code=exited, status=1/FAILURE
May 15 16:06:48 ubuntu systemd[1]: hermes-gateway.service: Failed with result 'exit-code'.
May 15 16:06:48 ubuntu systemd[1]: Stopped hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.
May 15 16:06:48 ubuntu systemd[1]: hermes-gateway.service: Consumed 10.868s CPU time over 1h 7min 29.733s wall clock time, 239.6M memory peak.
May 15 16:06:48 ubuntu systemd[1]: Starting hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration...
May 15 16:06:48 ubuntu systemd[1]: Started hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration.

## Cron Status
HERMES_COMMAND=FOUND
CRON_JOB_COUNT=173
{"id": "0c3585aacf23", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "b2bd96725614", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "1aa1e0386ed0", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "fecd3a74f700", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "6020f70af3cc", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "37f34e0ed28f", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "3a70dbd1e8d6", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "d3fcede57ff8", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "c15802463b8e", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "009c2556e896", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "f4f1a7f00817", "name": "phase7ca_reminder_create_test", "state": "scheduled", "enabled": true, "next_run_at": "2026-05-16T00:08:51.308842+08:00", "last_status": null, "deliver": "local"}
{"id": "1d56020484a1", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}

## Shellcheck
SHELLCHECK=SKIPPED_NOT_INSTALLED

OPS_HEALTHCHECK_DEEP=PASSED
