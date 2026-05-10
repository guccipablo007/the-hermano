# Hermes Backup Mirror

This repository is a safe backup mirror for the Hermes VPS setup.

It intentionally excludes secrets, tokens, OAuth credentials, generated output files, provider keys, logs, and caches.

## Main folders

- `scripts/` - Hermes helper scripts
- `plugins/` - Hermes plugins
- `skills/` - Hermes skills
- `rebuild_notes/` - phase notes and changelog
- `model_routing/` - safe routing policy files only
- `sanitized_config/` - redacted config snapshot
- `systemd/` - service unit snapshot
- `wrappers/` - helper CLI wrappers
- `runtime_patches/` - patched runtime Python files, when detected

## Restore principle

Do not blindly copy everything over a live Hermes install.

Recommended restore order:
1. inspect diffs
2. restore scripts/skills/plugins first
3. verify syntax
4. restore runtime patches carefully
5. restart Hermes only after verification
