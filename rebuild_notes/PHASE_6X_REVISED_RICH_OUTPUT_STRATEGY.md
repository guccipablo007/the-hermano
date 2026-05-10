
# Phase 6X Revised: Unified Rich Output Strategy

Problem:
Previous output workflows were too text-first and required special patches for pictures.

Fix:

* Added hermes_rich_output_plan.py
* Added hermes_media_verify.py
* Added rich-output-router skill
* Updated AGENTS.md, SOUL.md, and output-related skills
* Established visual_policy: none / auto / required
* Added rule that success requires media verification when visuals are requested or implied

Existing implemented visual routes:

* flashcards_pdf
* pptx_picture_file
* html_file

Planned rich routes:

* rich_pdf_picture_file
* rich_docx_picture_file
* rich_xlsx_file

No private route activated.
No default model changed.
