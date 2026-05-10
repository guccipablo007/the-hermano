# Rich Output Router Skill

## Purpose

Use this skill before creating any user-facing file output.

Hermes must stop thinking that documents are text-only. Modern outputs can contain pictures, charts, diagrams, icons, screenshots, tables, worksheets, and generated illustrations.

## Core Principle

Plan first. Build second.

Order:
1. Understand the user goal.
2. Detect exact file format.
3. Detect content type.
4. Decide visual policy.
5. Decide needed assets.
6. Choose the correct builder.
7. Build the file.
8. Verify the file.
9. Verify embedded media if visuals are required or promised.
10. Deliver to Telegram.
11. Claim success only after verification.

## Visual Policy

### none
Use only when the user asks for plain text, letter, memo, or explicitly says no pictures.

### auto
Use visuals when helpful: charts for data, diagrams for workflows, icons for dashboards, visual layout for HTML, tables for structured reports.

### required
Visuals must be generated/embedded for kids lessons, flashcards, young-child worksheets, PPTX lessons, anything saying with pictures/images/illustrations/icons, and matching words and pictures.

## Default Visual Policy

- Kids lesson PDF/DOCX/PPTX: required
- Flashcards: required
- Worksheets for young children: required
- PowerPoint lessons: required
- HTML landing pages: auto
- Business reports: auto
- Excel dashboards/trackers: auto
- Plain letter/memo: none

## Exact Format Rule

If Your Majesty asks for PDF, DOCX/Word, PPTX/PowerPoint/slides, XLSX/Excel/spreadsheet, or HTML/webpage/frontpage, create that exact format. Do not substitute formats unless Your Majesty explicitly agrees.

## Route Planning Tool

```bash
/root/.hermes/scripts/hermes_rich_output_plan.py --request "<exact user request>"
```

## Media Verification Tool

```bash
/root/.hermes/scripts/hermes_media_verify.py --file /path/to/file.pptx --type pptx --min-media 1
```

Supported types: pptx, docx, xlsx, pdf, html.

## Builder Mapping

Existing implemented routes:

- HTML -> `html_file`
- plain PDF -> `pdf_file`
- plain DOCX -> `docx_file`
- Markdown -> `md_file`
- plain PPTX -> `pptx_file`
- illustrated PPTX -> `pptx_picture_file`
- illustrated flashcards -> `flashcards_pdf`
- existing file delivery -> `deliver_file`

Planned/future rich routes:

- `rich_pdf_picture_file`
- `rich_docx_picture_file`
- `rich_xlsx_file`

If the rich route is not implemented and visuals are required, do not fall back silently to text-only. Report `NOT VERIFIED` and state the missing builder.

## Honesty Rule

Never claim with pictures, images, illustrations, charts, graphs, or diagrams unless the final artifact actually contains those visuals and media verification passed.

## Rich PDF/DOCX Lesson Builders

Implemented rich routes:
- `rich_pdf_picture_file`
- `rich_docx_picture_file`

Use these when Your Majesty asks for PDF or DOCX lessons with pictures, kids lesson documents where pictures are implied, or worksheets where pictures are required and PDF/DOCX is requested.

If visuals are required, do not use plain `pdf_file` or plain `docx_file`.

## Unified Natural Request Executor

For natural user-facing output requests, prefer the unified executor:

```bash
/root/.hermes/scripts/hermes_rich_output_execute.py \
  --request "<exact user request>"
```

Do not `skill_view` router mode names.

These are router modes, not skills:

* `rich_pdf_picture_file`
* `rich_docx_picture_file`
* `pptx_picture_file`
* `flashcards_pdf`
* `pdf_file`
* `docx_file`
* `pptx_file`
* `md_file`
* `html_file`

If a user asks for a rich document, run the unified executor first. It handles planning, route selection, execution, media verification, and delivery.

## Immediate Execution Rule

For natural artifact requests, do not stop after planning.

A plan is not completion.

After planning, immediately execute:

```bash
/root/.hermes/scripts/hermes_rich_output_execute.py \
  --request "<exact current user request>"
```

Router modes are commands, not creative skills. If a router-mode shim skill loads, use it only as a redirect to the unified executor.

Examples of router modes:

* rich_docx_picture_file
* rich_pdf_picture_file
* pptx_picture_file
* flashcards_pdf
* pptx_file
* docx_file
* pdf_file
* html_file

Never say a route is not implemented unless `/root/.hermes/scripts/hermes_rich_output_execute.py` itself reports `ROUTE_NOT_IMPLEMENTED`.

Forbidden behavior:

* planning only
* asking for confirmation after planning
* drifting to baoyu-comic
* falling back to emojis
* text-only output when pictures are required

If execution fails, say `NOT VERIFIED`.

## Multi-Artifact Batch Rule

If Your Majesty asks for more than one output format in the same request, do not run the single-output executor.

Use:

```bash
/root/.hermes/scripts/hermes_rich_batch_execute.py \
  --request "<exact current user request>"
```

Examples:

* DOCX + PPTX + PDF
* Word + PowerPoint + PDF
* PDF and DOCX
* PPTX and PDF

The batch executor must create, verify, media-verify, and deliver each requested file.

## Visual Quality Tier Rule

Do not confuse embedded media with acceptable pictures.

Visual tiers:
- `basic_icon`: simple symbols only
- `local_cartoon_scene`: meaningful local cartoon scene drawings
- `ai_cartoon_image`: provider-generated cartoon images
- `ai_3d_image`: provider-generated 3D-style images

For kids lessons with pictures, the minimum tier is `local_cartoon_scene`.

If Your Majesty asks for cartoon-style or 3D-style pictures, do not use `basic_icon`.

Use:
`/root/.hermes/scripts/hermes_visual_asset_generator.py`

Then verify:
`/root/.hermes/scripts/hermes_visual_quality_verify.py`

Do not claim ?real pictures,? ?cartoon pictures,? or ?3D images? unless the selected visual tier supports that claim.

## AI Image Quality Rule

Local Pillow drawings are `local_cartoon_scene`, not 3D images.

If Your Majesty asks for:
- beautiful 3D style
- 3D cartoon
- real images
- high-quality AI images
- Pixar-like style

Hermes must use `ai_3d_image` or `ai_cartoon_image` through:

```bash
/root/.hermes/scripts/hermes_visual_asset_router.py \
  --label "<activity>" \
  --topic "<topic>" \
  --output "<path>.png" \
  --quality-tier ai_3d_image
```

If the AI image provider is unavailable, say:

`NOT VERIFIED: AI image provider unavailable`

Do not silently fall back to flat vector images unless Your Majesty explicitly accepts fallback.

## Activated NewCoin AI Image Generation

NewCoin image generation is available.

When Your Majesty asks for beautiful 3D style, real images, high-quality images, or non-vector pictures, use:

`visual_quality_tier=ai_3d_image`

Use cached AI images whenever possible. Generate each activity image once, then reuse it across DOCX, PPTX, and PDF.

For ordinary kids lessons, local cartoon scenes remain acceptable unless Your Majesty asks for high-quality/3D/real/cartoon AI images.

## Default Visual Tier and Cost-Control Rule

Do not use AI image generation by default.

Default:
- kids lesson with pictures -> `local_cartoon_scene`

Use NewCoin AI images only when Your Majesty explicitly asks for:
- 3D style
- beautiful 3D
- AI images
- real images
- high-quality images
- not vector graphics
- not placeholder images

If the request only says "pictures," use local cartoon scenes.

Never generate AI images during tests unless the test specifically targets AI image generation.

For AI images, prompts must require:
- no text inside the image
- no words
- no letters
- no labels
- no signs
- no captions
- no watermarks
