# PPTX Output Router Skill

## Purpose

Use this skill whenever Your Majesty asks Hermes to create a PowerPoint, PPT, PPTX, slide deck, slides, or presentation file.

## Required Tool Path

Use the deterministic router executor:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file
```

## Hard Rule

If the request asks for:

* PowerPoint
* PPT
* PPTX
* slides
* slide deck
* presentation file

Then create a real `.pptx` with `pptx_file`.

Do not substitute:

* PDF
* DOCX
* HTML
* Markdown

Do not use the old `powerpoint` skill for normal final output creation unless Your Majesty explicitly asks to edit an existing PPTX.

## Example

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file \
  --output /root/.hermes/file_outputs/my_home_lesson.pptx \
  --title "My Home" \
  --description "Create a 5-slide PowerPoint lesson for 4-year-old kids about My Home." \
  --expect-text "My Home"
```

## Output Requirements

The result must:

* be a real `.pptx`
* be saved under `/root/.hermes/file_outputs`
* be verified
* be delivered to Telegram

If any step fails, report:

`NOT VERIFIED`

## Unified Rich Output Planning Rule

Before generating any file output, use rich-output planning.

Command:

```bash
/root/.hermes/scripts/hermes_rich_output_plan.py \
  --request "<exact user request>"
```

If the plan says visuals are required, choose a visual-capable builder.

Do not use a text-only builder when the request needs pictures, charts, diagrams, icons, graphs, or illustrations.

If the correct visual builder is not yet implemented, report `NOT VERIFIED` instead of producing a half-complete artifact.

When visuals are required or promised, run:

```bash
/root/.hermes/scripts/hermes_media_verify.py \
  --file <artifact> \
  --type <pptx|docx|xlsx|pdf|html> \
  --min-media 1
```

Claim success only after file verification, media verification, and Telegram delivery pass.
