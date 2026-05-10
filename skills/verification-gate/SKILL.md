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
