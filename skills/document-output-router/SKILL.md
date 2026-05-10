# Document Output Router Skill

## Purpose

Use this skill whenever Your Majesty asks Hermes to create, verify, and send a document or webpage file.

This skill prevents Hermes from improvising unreliable document workflows.

## Hard Rule

For generated output files, use the deterministic router executor:

`/root/.hermes/scripts/hermes_router_execute.py`

Do not use pandoc, pdfunite, pdflatex, texlive, or manual `/tmp` document workflows unless Your Majesty explicitly asks for that conversion workflow.

## Format Routing

### PDF

If Your Majesty asks for PDF, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py pdf_file \
  --output /root/.hermes/file_outputs/<safe_name>.pdf \
  --title "<title>" \
  --description "<description>" \
  --expect-text "<expected text>"
```

Rules:

* Create a real `.pdf`
* Do not substitute DOCX or HTML
* Verify and deliver to Telegram

### DOCX

If Your Majesty asks for DOCX or Word document, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py docx_file \
  --output /root/.hermes/file_outputs/<safe_name>.docx \
  --title "<title>" \
  --description "<description>" \
  --expect-text "<expected text>"
```

### Markdown

If Your Majesty asks for Markdown or a simple report file, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py md_file \
  --output /root/.hermes/file_outputs/<safe_name>.md \
  --title "<title>" \
  --description "<description>" \
  --expect-text "<expected text>"
```

### HTML / Front Page / Webpage

If Your Majesty asks for HTML, webpage, landing page, or front page, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py html_file \
  --output /root/.hermes/newcoin_outputs/<safe_name>.html \
  --description "<description>" \
  --expect-text "<expected text>"
```

HTML automatically sends:

* the `.html` file
* a preview link

### Existing File Delivery

If a verified file already exists, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py deliver_file \
  --file /root/.hermes/file_outputs/<file> \
  --caption "Your Majesty, here is your file." \
  --preview-link no
```

## Output Folders

Use only:

* `/root/.hermes/file_outputs`
* `/root/.hermes/newcoin_outputs`
* `/root/.hermes/telegram_outputs`

Do not use `/tmp` for final outputs.

## Verification

The deterministic router handles verification and Telegram delivery.

Success requires:

* real file exists
* correct file type
* verification passed
* Telegram delivery passed

If any step fails, say:

`NOT VERIFIED`

## Image Rule

Do not add cartoonish illustrations or generated images unless Your Majesty explicitly asks for images and an image-generation workflow is available.

For kids lessons without an image request, create a clean text-based PDF/DOCX first.

## Forbidden Default Tools for Document Creation

Do not use by default:

* pandoc
* pdfunite
* pdflatex
* texlive installation
* manual `/tmp/*.md` to PDF pipelines

These are only allowed if Your Majesty explicitly asks for a pandoc/LaTeX conversion workflow.


## Illustrated Flashcards

If Your Majesty asks for flashcards with pictures or accompanying pictures, use `flashcards_pdf`.

Do not create text-only flashcards when pictures are requested. Do not use emoji-only placeholders as the default. Do not rely on ComfyUI unless explicitly available and requested. Use local deterministic picture generation first.

## Hard Flashcard Routing Rule

If a document request is specifically for flashcards with pictures, use `flashcards_pdf`, not generic `pdf_file`.

Correct:

```bash
/root/.hermes/scripts/hermes_router_execute.py flashcards_pdf
```

Wrong:

* generic text PDF
* emoji-only PDF
* baoyu-comic
* ComfyUI fallback

## PPTX / PowerPoint

If Your Majesty asks for PowerPoint, PPT, PPTX, slide deck, or slides, create a real `.pptx`.

Use:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file \
  --output /root/.hermes/file_outputs/<safe_name>.pptx \
  --title "<title>" \
  --description "<description>" \
  --expect-text "<expected text>"
```

Do not substitute PDF/DOCX/HTML.

## Hard PPTX Routing Rule

If a document request asks for PowerPoint, PPT, PPTX, slides, slide deck, or presentation file, use `pptx_file`.

Correct:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file
```

Wrong:

* old powerpoint skill
* PDF substitute
* DOCX substitute
* HTML substitute
* Markdown substitute

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

## Rich PDF/DOCX Picture Output Rule

For PDF or DOCX lessons, worksheets, or kids documents where pictures are requested or implied, use the rich visual-capable builders:

* `rich_pdf_picture_file`
* `rich_docx_picture_file`

Do not use plain `pdf_file` or plain `docx_file` when pictures are required.

Success requires file verification, media verification, and Telegram delivery. If media verification fails, report `NOT VERIFIED`.

## Unified Rich Output Executor Rule

For natural requests to create documents, lessons, worksheets, flashcards, presentations, spreadsheets, or webpages, use:

`/root/.hermes/scripts/hermes_rich_output_execute.py --request "<exact user request>"`

Do not try to load router modes with `skill_view`.

Router modes are commands, not skills:

* `rich_pdf_picture_file`
* `rich_docx_picture_file`
* `pptx_picture_file`
* `flashcards_pdf`
* `pdf_file`
* `docx_file`
* `pptx_file`
* `md_file`
* `html_file`

The unified executor must be preferred because it performs planning, route selection, builder execution, file verification, media verification when required, and Telegram delivery.

If it fails, report `NOT VERIFIED`.

## Natural Request Execution Override

For natural user requests that ask Hermes to create a file, document, lesson, worksheet, flashcards, presentation, webpage, or spreadsheet, prefer the unified executor:

```bash
/root/.hermes/scripts/hermes_rich_output_execute.py \
  --request "<exact current user request>"
```

Do not merely display a plan.

Do not ask for confirmation.

Do not use `skill_view` on router mode names as if they are standalone creative skills.

If the request includes pictures, images, illustrations, charts, graphs, diagrams, or young-child lesson material, the unified executor must verify media before success is claimed.

If execution or verification fails, report `NOT VERIFIED`.

## Multi-Artifact Output Rule

When Your Majesty asks for multiple output formats in one request, use:

`/root/.hermes/scripts/hermes_rich_batch_execute.py --request "<exact current user request>"`

Do not choose only one format.

All requested formats must be attempted and individually verified.

If any requested artifact fails, report `NOT VERIFIED` and show which format failed.

## Visual Asset Quality Rule

For kids lessons, worksheets, flashcards, PDFs, DOCX, PPTX, and classroom materials with pictures, do not use basic placeholder icons.

Minimum acceptable tier:
`local_cartoon_scene`

Forbidden as final lesson pictures unless explicitly requested:
- yellow circles with text only
- emoji-only images
- text-only placeholders
- generic symbols that do not depict the activity

Success requires:
- embedded media verification
- visual quality verification
- Telegram delivery

## AI Image Provider Honesty Rule

Do not call local vector/cartoon drawings ?3D images? or ?real images.?

Local generated scenes are only:
`local_cartoon_scene`

For beautiful 3D/cartoon AI images, Hermes must use a verified AI image provider.

If no image-generation provider is verified, report:
`NOT VERIFIED: AI image provider unavailable`

Do not silently downgrade to flat vector graphics unless Your Majesty explicitly accepts the fallback.

## NewCoin AI Image Generation Rule

NewCoin image generation is available and should be used when Your Majesty asks for:
- beautiful 3D style pictures
- real images
- high-quality cartoon pictures
- non-vector images
- proper beautiful images

Use `ai_3d_image` and cache outputs.

Do not regenerate the same activity image for DOCX, PPTX, and PDF separately. Reuse cached assets.

## Lesson Layout and AI Cost Rule

For normal classroom lesson files with pictures, use local cartoon scenes by default.

Do not use NewCoin image generation unless Your Majesty explicitly asks for 3D/AI/real/high-quality/non-vector images.

When creating PPTX lessons:
- use consistent 16:9 layout
- image on the left
- title/sentence/prompt on the right
- no floating or misaligned objects

When creating PDF lessons:
- use consistent margins
- scale images evenly
- use clean two-card-per-page layout where possible
- keep grammar corrected through phrase normalization

Do not test DOCX unless the phase or user asks for DOCX testing.
