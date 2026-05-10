# PowerPoint Skill - Deterministic Delegator Only

## Purpose

This skill exists only to route PowerPoint/PPT/PPTX/slide deck requests to the verified deterministic PPTX workflow.

It must not create slides itself for normal user-facing output.

## Hard Rule

When Your Majesty asks for:
- PowerPoint
- PPT
- PPTX
- slides
- slide deck
- lesson presentation
- presentation file

Use this command pattern only:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file \
  --output /root/.hermes/file_outputs/<safe_name>.pptx \
  --title "<presentation title>" \
  --description "<clear presentation description>" \
  --expect-text "<expected title text>"
```

## Forbidden for New PPTX Creation

Do not use:

* `scripts/add_slide.py`
* `hermes_router_execute pptx_file` shorthand
* PDF substitute
* DOCX substitute
* HTML substitute
* Markdown substitute
* prose-only plan
* fake "file created" claim

## Required Success Evidence

Before claiming success, terminal/tool output must show:

* real `.pptx` output path
* `VERIFICATION=PASSED`
* Telegram delivery passed or file visibly delivered

If those are not present, respond:

`NOT VERIFIED`

## Example

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file \
  --output /root/.hermes/file_outputs/my_home_lesson.pptx \
  --title "My Home" \
  --description "Create a 5-slide PowerPoint lesson about My Home for 4-year-old kids. Include title slide, what is a home, rooms, things we do at home, and review slide." \
  --expect-text "My Home"
```

## Existing PPTX Editing

Only use old internal PowerPoint editing scripts if Your Majesty explicitly asks to inspect or edit an existing PPTX file and provides a file path.
