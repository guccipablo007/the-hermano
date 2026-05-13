# Model Router Skill

## Purpose

Use this skill when a user request would benefit from Hermes delegating work to a specialist model/worker route.

This skill supports the decentralized Hermes architecture:

User / Telegram
? Hermes Supervisor
? Task classification
? Specialist worker route
? Verification gate
? Final response

## Core Rule

Understand the user's natural language first.

Do not use hardcoded phrase routing.

Routing must be based on:
- task intent
- complexity
- tool needs
- privacy risk
- verification needs

## Available Routes

Routing policy file:

`/root/.hermes/model_routing/routing_policy.yaml`

Manual model-call helper:

`/root/.hermes/scripts/hermes_model_call.py`

### basic

Model:
- newcoin / qwen3-32b

Use for:
- simple explanations
- simple summaries
- rewriting
- brainstorming
- lightweight non-sensitive research
- simple plans

Do not use for:
- Gmail
- YouTube analytics/account data
- private credentials
- exact source-verified research
- complex builds

Example:

```bash
/root/.hermes/scripts/hermes_model_call.py --route basic --prompt "Explain this in simple terms..."
```

### coder

Model:
- newcoin / doubao-seed-2-0-code-preview-260215

Use for:
- Python scripts
- HTML/CSS/JS
- dashboards
- local automation
- file builders
- webapps
- helper tools
- skill creation

Verification required:
- use `/root/.hermes/scripts/hermes_verify.py script` for scripts
- use `/root/.hermes/scripts/hermes_verify.py file` for files
- run syntax checks and tests when possible

Example:

```bash
/root/.hermes/scripts/hermes_model_call.py --route coder --prompt "Generate a Python script..."
```

### complex_reasoning

Model:
- newcoin / kimi-k2

Use for:
- system architecture
- complex business strategy
- multi-agent planning
- difficult debugging
- project roadmaps
- decisions with many tradeoffs

Escalate to source_verified_research when source evidence is required.

Example:

```bash
/root/.hermes/scripts/hermes_model_call.py --route complex_reasoning --prompt "Design an architecture for..."
```

### vision

Model:
- newcoin / doubao-seed-1-6-vision-250815

Use for:
- screenshots
- UI images
- receipt photos
- thumbnails
- worksheet images
- visual inspection

Rules:
- describe visible facts
- separate observation from assumption
- do not infer private sensitive data beyond what is visible

Note:
Image routing may require additional helper support before full Telegram image routing is activated.

### source_verified_research

Model:
- newcoin / qwen3-32b

Use for:
- exact-source research
- quote-based reports
- documentation verification
- external links
- source conflict analysis
- claims where correctness matters

Required tools:
- `/root/.hermes/scripts/source_quote_extractor.py`
- `/root/.hermes/scripts/hermes_verify.py source_quote`

Required workflow:
1. Save raw sources under `/root/.hermes/research_sources/<project_name>/`.
2. Extract exact quotes with line numbers.
3. Run quote audit.
4. Separate verified facts, assumptions, not proven items, and risks.
5. Never claim a quote exists unless source_quote verification passes.

Example:

```bash
/root/.hermes/scripts/hermes_model_call.py --route source_verified_research --prompt "Create a source-verified report..."
```

### private_data

Model:
- openrouter / deepseek/deepseek-chat

Status:
- reserved only
- not active yet

Use only for future safe modules:
- Gmail
- YouTube Data API
- YouTube Analytics API
- OAuth/account data
- private analytics reports

Current behavior:
If a task requires private_data route before the safe module exists, answer:

`PRIVATE_DATA_ROUTE_NOT_ACTIVE_YET`

Never send Gmail content, YouTube analytics/account data, OAuth tokens, API keys, passwords, or private credentials to NewCoin.

## Verification Gate

Use the verification gate skill and helper before claiming success.

Helper:

`/root/.hermes/scripts/hermes_verify.py`

If verification fails, answer:

`NOT VERIFIED`

### File claims

Before saying a file was created or edited:

```bash
/root/.hermes/scripts/hermes_verify.py file --path /path/to/file
```

### Script claims

Before saying a script works:

```bash
/root/.hermes/scripts/hermes_verify.py script --path /path/to/script.py --test-cmd "python3 /path/to/script.py --help"
```

### Research quote claims

Before saying a quote exists:

```bash
/root/.hermes/scripts/hermes_verify.py source_quote --file /path/to/source --quote "exact quote"
```

### Service claims

Before saying a service is running:

```bash
/root/.hermes/scripts/hermes_verify.py service --name service-name
```

### Config claims

Before saying config is valid:

```bash
/root/.hermes/scripts/hermes_verify.py config --path /path/to/config.yaml
```

## Examples of Correct Routing

User: "Explain what Paperclip is in simple language."
Route: basic

User: "Build a Python script that extracts quotes from files."
Route: coder, then verification gate

User: "Design my Hermes + Paperclip business architecture."
Route: complex_reasoning

User: "Analyze this screenshot."
Route: vision

User: "Verify what the Paperclip docs actually say and include exact quotes."
Route: source_verified_research, then quote audit

User: "Check my Gmail and summarize important emails."
Route: private_data, but refuse for now with PRIVATE_DATA_ROUTE_NOT_ACTIVE_YET until safe Gmail module exists

User: "Check my YouTube analytics."
Route: private_data, but refuse for now with PRIVATE_DATA_ROUTE_NOT_ACTIVE_YET until safe YouTube module exists

## Anti-Patterns

Do not:
- hardcode phrase routes
- guess the route from one keyword only
- claim success without verification
- invent source quotes
- send private data to NewCoin
- activate private routes before safe Gmail/YouTube modules exist
- treat simulated JSON as tool output

## Final Response Rule

When using a specialist route, final response should include:
- route used
- model used
- what was done
- verification result
- exact file paths if files were created
- honest errors or limitations

## Router Executor Preference

For Telegram-safe execution tasks, prefer the deterministic router executor:

`/root/.hermes/scripts/hermes_router_execute.py`

Use it instead of manually chaining `hermes_model_call.py` and `hermes_verify.py` when the task is a supported execution mode.

Supported mode now:
- `coder_file`

Example:

```bash
/root/.hermes/scripts/hermes_router_execute.py coder_file \
  --output /root/.hermes/scripts/hello_router.py \
  --description "Create a Python script that prints HELLO_ROUTER." \
  --test-cmd "python3 /root/.hermes/scripts/hello_router.py" \
  --expect-output "HELLO_ROUTER"
```

If the router executor fails, report `NOT VERIFIED`.

## HTML File Mode

The deterministic router executor supports:

- `html_file`

Use this when Your Majesty asks for:
- landing pages
- simple webpages
- HTML/CSS prototypes
- webapp front pages
- visual page demos

Example:

```bash
/root/.hermes/scripts/hermes_router_execute.py html_file \
  --output /root/.hermes/newcoin_outputs/example_landing_page.html \
  --description "Create a clean single-file HTML/CSS landing page." \
  --expect-text "Example Landing Page"
```

Required behavior:
- Always provide `--output`
- Always provide `--description`
- Use `--expect-text` when there is a clear title or phrase that must appear
- Report the output path and verification result
- If the executor fails, report `NOT VERIFIED`

## Telegram Native Delivery

When Your Majesty asks for a file output, deliver it back through Telegram whenever possible.

Use:

`/root/.hermes/scripts/hermes_telegram_deliver.py`

For HTML outputs:
- send the `.html` file as a Telegram document
- also send a preview link
- prefer `hermes_router_execute.py html_file --deliver-telegram`

For documents:
- send PDF, DOCX, PPTX, XLSX, TXT, MD, JSON, CSV, ZIP as Telegram document attachments

Do not require a web dashboard or login portal for normal personal-device usage.

## Automatic Telegram Delivery Rule

For normal personal-device usage, Telegram is the main output center.

When an output file is generated and verified, deliver it to Telegram automatically whenever possible.

### HTML Outputs

Use:

```bash
/root/.hermes/scripts/hermes_router_execute.py html_file \
  --output /root/.hermes/newcoin_outputs/example.html \
  --description "Create a single-file HTML/CSS page." \
  --expect-text "Example"
```

HTML delivery is automatic by default:

* sends the `.html` file to Telegram
* sends a preview link

Use `--no-deliver-telegram` only when delivery should be skipped.

### Existing Files / Documents

Use:

```bash
/root/.hermes/scripts/hermes_router_execute.py deliver_file \
  --file /root/.hermes/file_outputs/example.pdf \
  --caption "Your Majesty, here is your file." \
  --preview-link no
```

Supported delivery targets include:

* HTML
* PDF
* DOCX
* PPTX
* XLSX
* MD
* TXT
* JSON
* CSV
* PY
* ZIP
* PNG/JPG/WEBP

### Rule

Do not require a login portal or dashboard for normal output access.

Do not expose arbitrary server folders.

If delivery fails, report `NOT VERIFIED`.


## Document File Modes

Hermes supports deterministic document creation through `/root/.hermes/scripts/hermes_router_execute.py`.

Available document modes: `pdf_file`, `docx_file`, `md_file`.

Use these when Your Majesty asks for PDF reports, DOCX documents, Markdown reports, lesson notes, printable worksheets without complex images, or simple business documents.

Document delivery is automatic by default. If document creation or delivery fails, report `NOT VERIFIED`.

Important: If Your Majesty asks specifically for PDF, create PDF. If Your Majesty asks specifically for DOCX, create DOCX. Do not substitute one format for another unless asked.

## Hard Document Output Override

When Your Majesty asks for a generated PDF, DOCX, Markdown document, HTML page, landing page, front page, worksheet, lesson document, or report file, use the deterministic router executor.

Do not use productivity/pandoc/pdfunite/pdflatex/manual `/tmp` workflows for generated documents.

Correct routes:

* PDF ? `pdf_file`
* DOCX/Word ? `docx_file`
* Markdown ? `md_file`
* HTML/webpage/front page ? `html_file`
* existing output file ? `deliver_file`

The output must be verified and delivered to Telegram.

If verification or delivery fails, say `NOT VERIFIED`.

Do not substitute file formats.
If PDF is requested, create PDF.
If DOCX is requested, create DOCX.
If HTML is requested, create HTML.

Do not add images unless explicitly requested.


## Illustrated Flashcards Mode

When Your Majesty asks for flashcards with pictures, use `/root/.hermes/scripts/hermes_router_execute.py flashcards_pdf`.

Rules:
* Create real pictures using local deterministic drawing.
* Do not use emoji-only placeholders as the default.
* Do not claim image generation if no image files are created.
* Deliver the verified PDF to Telegram.
* If picture creation, PDF creation, verification, or delivery fails, report `NOT VERIFIED`.

## Hard Flashcard Output Override

When Your Majesty asks for flashcards with pictures, kids flashcards, classroom flashcards, printable flashcards, or flashcards as PDF, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py flashcards_pdf
```

Do not use baoyu-comic for ordinary classroom flashcards.
Do not use ComfyUI unless explicitly requested.
Do not use emoji-only placeholders unless explicitly allowed.
Do not create text-only flashcards when pictures are requested.

The output must:

* create real PNG pictures
* embed them into the PDF
* verify the PDF
* deliver the PDF to Telegram

If any step fails, report `NOT VERIFIED`.

## PPTX File Mode

When Your Majesty asks for PowerPoint, PPT, PPTX, slide deck, or slides, create a real `.pptx` file.

Use:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file \
  --output /root/.hermes/file_outputs/example.pptx \
  --title "Example Presentation" \
  --description "Create a short slide presentation." \
  --expect-text "Example Presentation"
```

Rules:

* Do not substitute PDF, DOCX, HTML, or Markdown.
* Verify the `.pptx`.
* Deliver it directly to Telegram.
* If verification or delivery fails, report `NOT VERIFIED`.

## Hard PPTX Output Override

When Your Majesty asks for PowerPoint, PPT, PPTX, slides, slide deck, or presentation file, use:

```bash
/root/.hermes/scripts/hermes_router_execute.py pptx_file
```

Do not use the old powerpoint skill for normal final output creation.
Do not substitute PDF, DOCX, HTML, or Markdown.
Do not claim success unless the real `.pptx` is verified and delivered to Telegram.

If any step fails, report `NOT VERIFIED`.

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

## Artifact Execution Priority Rule

When the user asks to create an artifact file, the priority is execution, not discussion.

Use:

```bash
/root/.hermes/scripts/hermes_rich_output_execute.py \
  --request "<exact current user request>"
```

Do not choose baoyu-comic for DOCX/PDF/PPTX lesson documents unless the user explicitly asks for a comic-generation workflow.

Do not produce a prose-only plan.

Do not ask the user whether to proceed after they already requested the file.

A successful answer must be backed by tool output showing:

* output path
* verification passed
* media verification passed when required
* Telegram delivery passed

Otherwise say `NOT VERIFIED`.

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

## NewCoin Popular Model Routing Note

NewCoin is the primary provider. Use verified popular NewCoin model IDs from `/models`, not guessed names.

Current verified routing:
- Default/general/simple: `gemini-2.5-flash`
- Reasoning/agentic: `kimi-k2.6`
- Coding/debugging: `deepseek-v3.2`
- OpenRouter: fallback only

Do not use Doubao as the primary coding route unless explicitly re-verified and requested.
Do not use GPT/OpenAI models on NewCoin as defaults because they may be expensive.

Future planning only: `/nc` may later force NewCoin for a request, with optional hints such as `/nc code`, `/nc reason`, or `/nc cheap`. This is not implemented yet.

## Task-Aware NewCoin Model Router

Hermes has a model-selection router at `/root/.hermes/scripts/hermes_model_router.py`.
This is model routing only, not multi-agent delegation.

Routing order:
1. Use verified tools/scripts first when available.
2. Use NewCoin `qwen3-32b` for default/simple tasks.
3. Use NewCoin `kimi-k2.6` for reasoning, root-cause analysis, planning, and agent behavior design.
4. Use NewCoin `deepseek-v3.2` for coding, debugging, logs, stack traces, file paths, config edits, gateway/router/script work, and app/Firebase/database issues.
5. Use OpenRouter only as fallback if the selected NewCoin route fails.

Future planning only: `/nc code`, `/nc reason`, `/nc cheap`, and `/nc status` may be implemented later. They are not active yet.
