# pdf_file Router Mode Shim

## Purpose

This is not a creative content skill.

This is a compatibility shim for the router mode:

`pdf_file`

If this skill is loaded, Hermes must treat it as a signal to execute the unified rich-output executor.

## Hard Rule

Do not stop at planning.

Do not ask for confirmation.

Do not say the route is not implemented unless the unified executor reports:

`ROUTE_NOT_IMPLEMENTED`

Do not use baoyu-comic, ComfyUI, emojis, or text-only fallback unless Your Majesty explicitly asks.

## Required Action

For the current user request, immediately run:

```bash
/root/.hermes/scripts/hermes_rich_output_execute.py \
  --request "<exact current user request>"
```

Alternative wrapper:

```bash
hermes_rich_output_execute --request "<exact current user request>"
```

## Success Rule

Success requires:
- actual terminal execution
- output file path
- file verification passed
- media verification passed when visuals are required
- Telegram delivery passed

If any requirement fails, say:

`NOT VERIFIED`

## Forbidden Response

Never respond only with:
- a plan
- "I will proceed"
- "Let me know"
- "Would you like me to continue?"
- a proposed command without executing it

The command must be executed.
