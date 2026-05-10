# Illustrated Flashcards Skill

## Purpose

Use this skill whenever Your Majesty asks for flashcards with pictures, illustrated flashcards, classroom flashcards, printable flashcards, kids flashcards, or flashcards as PDF.

## Required Tool Path

Use the deterministic router executor:

```bash
/root/.hermes/scripts/hermes_router_execute.py flashcards_pdf
```

## Hard Rule

If the request contains:

* flashcard
* flashcards
* cards for kids
* classroom cards
* printable cards
* accompanying pictures
* pictures
* illustrations

Then use `flashcards_pdf`.

Do not use:

* baoyu-comic
* comfyui
* emoji-only placeholders
* text-only PDF

unless Your Majesty explicitly asks for that alternative.

## Example

```bash
/root/.hermes/scripts/hermes_router_execute.py flashcards_pdf \
  --output /root/.hermes/file_outputs/mothers_day_flashcards_illustrated.pdf \
  --title "Mother's Day Flashcards" \
  --theme mothers_day \
  --age "3-4"
```

## Output Requirements

The result must include:

* real generated PNG pictures
* pictures embedded in the PDF
* simple words
* simple questions
* verified PDF
* Telegram delivery

## Failure Rule

If picture generation, PDF creation, verification, or Telegram delivery fails, report:

`NOT VERIFIED`
