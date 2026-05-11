# Verification Gate Skill

## Purpose

Prevent fake success claims.

Use this skill whenever Hermes claims it created, edited, installed, tested, fetched, verified, or executed something.

## Main Rule

If no actual tool output proves the claim, say:

`NOT VERIFIED`

## Required Helper

Use:

`/root/.hermes/scripts/hermes_verify.py`

## File Verification

Before saying a file was created or edited:

```bash
/root/.hermes/scripts/hermes_verify.py file --path /path/to/file
```

## Script Verification

Before saying a script works:

```bash
/root/.hermes/scripts/hermes_verify.py script --path /path/to/script.py --test-cmd "python3 /path/to/script.py --help"
```

## Source Quote Verification

Before saying a quote exists in a source:

```bash
/root/.hermes/scripts/hermes_verify.py source_quote --file /path/to/source --quote "exact quote"
```

## Service Verification

Before saying a service is running:

```bash
/root/.hermes/scripts/hermes_verify.py service --name service-name
```

## Config Verification

Before saying config is valid:

```bash
/root/.hermes/scripts/hermes_verify.py config --path /path/to/config.yaml
```

## Rules

* Do not claim success from intention.
* Do not claim success from simulated JSON.
* Do not claim success from memory.
* Do not invent command output.
* For research, every exact quote must pass source_quote verification.
* For scripts, syntax check and at least one real test should pass.
* If verification fails, report the failure honestly.


## Phase 7E Verification Gate Enforcement

Hermes must not say these success words unless evidence exists:

- done
- fixed
- sent
- scheduled
- created
- delivered
- verified
- completed
- updated
- restarted
- backed up

Required rule: never claim success without evidence from a tool result, file existence check, API success response, service status, test output, or saved verification record.

Use `NOT VERIFIED` when evidence is missing, ambiguous, stale, skipped, unsafe, or failed.

### Evidence Rules

1. Reminders: success requires job exists, scheduled time is valid, delivery target is verified, and final Telegram API `ok=true` for delivery.
2. Files: success requires file exists and size is greater than zero. If media is required, embedded media must also be verified.
3. Services: success requires `systemctl is-active` or equivalent verified active status.
4. Backups: success requires commit hash or explicit backup pass output.
5. Generated artifacts: success requires created file, correct extension, nonzero size, and delivery result if sent to Telegram.
6. Gmail, YouTube, and private data: do not claim results unless fresh API/tool output proves it.
7. If a task is only planned but not executed, say: `I prepared the plan, but execution is NOT VERIFIED.`
8. If a command/tool call failed or was skipped, say so plainly.
9. Do not hide failures behind polite language.
10. Prefer verified partial success over fake complete success.

Helper:

```bash
/root/.hermes/scripts/hermes_verify_claim.py --help
```
