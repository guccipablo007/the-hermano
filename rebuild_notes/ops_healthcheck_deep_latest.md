# Hermes Ops Healthcheck (deep)
Generated: 2026-05-15T14:19:34+00:00
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
Mem:           1.8Gi       1.4Gi       106Mi       689Mi       1.1Gi       419Mi
Swap:             0B          0B          0B

## Recent Gateway Fatal/Error Scan
May 14 15:58:09 ubuntu python[151426]:     self.gen.throw(typ, value, traceback)
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
May 14 15:58:09 ubuntu python[151426]:     self.gen.throw(typ, value, traceback)
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
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
JOB_ID=0c3585aacf23
EXPECTED=2026-05-15T22:21:35.651718+08:00
ACTUAL=2026-05-15T22:21:35.653059+08:00
DELTA_SECONDS=0.001341
TIMEZONE=Asia/Shanghai
JOB_ID=b2bd96725614
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
GIT_COMMIT=e3f4fa2695b67aa6e66a31ffb4538c2b71e3af66
GIT_REMOTE=git@github.com-hermes:guccipablo007/the-hermano.git

## Gateway Status
● hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration
     Loaded: loaded (/etc/systemd/system/hermes-gateway.service; enabled; preset: enabled)
    Drop-In: /etc/systemd/system/hermes-gateway.service.d
             └─30-ops-healthcheck.conf
     Active: active (running) since Wed 2026-05-13 16:19:04 UTC; 1 day 22h ago
 Invocation: f6e7b367cc5f43fd9aa00b115241aa74
    Process: 151427 ExecStartPost=/bin/bash -lc systemd-run --unit=hermes-ops-startup-healthcheck --property=Type=oneshot --on-active=20s /usr/local/bin/hermes_ops_startup_healthcheck >/dev/null 2>&1 || true (code=exited, status=0/SUCCESS)
   Main PID: 151426 (python)
      Tasks: 5 (limit: 1141)
     Memory: 183.8M (peak: 204.1M)
        CPU: 3min 15.717s
     CGroup: /system.slice/hermes-gateway.service
             └─151426 /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace

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

## Gateway Logs
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
May 14 15:58:09 ubuntu python[151426]: WARNING gateway.platforms.telegram_network: [Telegram] Primary api.telegram.org connection failed (All connection attempts failed); trying fallback IPs 149.154.166.110
May 14 15:58:09 ubuntu python[151426]: WARNING gateway.platforms.telegram_network: [Telegram] Fallback IP 149.154.166.110 failed: All connection attempts failed
May 14 15:58:09 ubuntu python[151426]: ERROR telegram.ext: Network Retry Loop (Bootstrap delete Webhook): Failed run number 0 of 0. Aborting.
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 101, in map_httpcore_exceptions
May 14 15:58:09 ubuntu python[151426]:     yield
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 394, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     resp = await self._pool.handle_async_request(req)
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 256, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     raise exc from None
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 236, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     response = await connection.handle_async_request(
May 14 15:58:09 ubuntu python[151426]:                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 101, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     raise exc
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 78, in handle_async_request
May 14 15:58:09 ubuntu python[151426]:     stream = await self._connect(request)
May 14 15:58:09 ubuntu python[151426]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 124, in _connect
May 14 15:58:09 ubuntu python[151426]:     stream = await self._network_backend.connect_tcp(**kwargs)
May 14 15:58:09 ubuntu python[151426]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_backends/auto.py", line 31, in connect_tcp
May 14 15:58:09 ubuntu python[151426]:     return await self._backend.connect_tcp(
May 14 15:58:09 ubuntu python[151426]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 113, in connect_tcp
May 14 15:58:09 ubuntu python[151426]:     with map_exceptions(exc_map):
May 14 15:58:09 ubuntu python[151426]:   File "/root/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/lib/python3.11/contextlib.py", line 158, in __exit__
May 14 15:58:09 ubuntu python[151426]:     self.gen.throw(typ, value, traceback)
May 14 15:58:09 ubuntu python[151426]:   File "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions
May 14 15:58:09 ubuntu python[151426]:     raise to_exc(exc) from exc
May 14 15:58:09 ubuntu python[151426]: httpcore.ConnectError: All connection attempts failed
May 14 15:58:09 ubuntu python[151426]: The above exception was the direct cause of the following exception:
May 14 15:58:09 ubuntu python[151426]: Traceback (most recent call last):
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

## Cron Status
HERMES_COMMAND=FOUND
CRON_JOB_COUNT=163
{"id": "8070d8e8c808", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "20a68ce7a3b4", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "e6f667d435dc", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "aa0d475353eb", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "1f1c035e302d", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "86fa30745373", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "eef096cc1ca6", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "09f9a61d015b", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "36bfe8ba1299", "name": "phase7ca_reminder_create_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "8e1a3f1cd4d4", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}
{"id": "0c3585aacf23", "name": "phase7ca_reminder_create_test", "state": "scheduled", "enabled": true, "next_run_at": "2026-05-15T22:21:35.653059+08:00", "last_status": null, "deliver": "local"}
{"id": "b2bd96725614", "name": "phase7ca2_reminder_delivery_test", "state": "completed", "enabled": false, "next_run_at": null, "last_status": "ok", "deliver": "local"}

## Shellcheck
SHELLCHECK=SKIPPED_NOT_INSTALLED

OPS_HEALTHCHECK_DEEP=PASSED
