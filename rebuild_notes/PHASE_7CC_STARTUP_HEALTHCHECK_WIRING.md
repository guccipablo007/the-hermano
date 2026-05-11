# Phase 7C-C: Startup Healthcheck Wiring

Changed:
- Added /root/.hermes/scripts/hermes_ops_startup_healthcheck.sh
- Added /usr/local/bin/hermes_ops_startup_healthcheck
- Added /etc/systemd/system/hermes-gateway.service.d/30-ops-healthcheck.conf

The drop-in uses ExecStartPost and does not replace the main ExecStart. The startup wrapper always exits 0, so gateway startup is not blocked if the healthcheck fails.

Telegram startup failure alert is not wired yet; status is TELEGRAM_STARTUP_ALERT=NOT_VERIFIED. Failures are logged to /root/.hermes/rebuild_notes/startup_healthcheck_systemd.log and summarized in /root/.hermes/rebuild_notes/startup_healthcheck_last_status.md.

No default model changed. No Gmail/YouTube/private_data changes.

Update:
- Changed ExecStartPost to schedule a transient delayed systemd job with systemd-run.
- Reason: a synchronous ExecStartPost keeps hermes-gateway.service in activating state, causing the healthcheck to see GATEWAY_ACTIVE=activating.
