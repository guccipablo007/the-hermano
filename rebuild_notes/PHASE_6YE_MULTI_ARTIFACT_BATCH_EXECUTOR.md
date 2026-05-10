
# Phase 6Y-E: Multi-Artifact Batch Executor

Problem:
Telegram artifact pre-router intercepted a DOCX+PPT+PDF request, but the single-output executor selected only PPTX and failed.

Fix:

* Added /root/.hermes/scripts/hermes_rich_batch_execute.py
* Added /root/.hermes/scripts/hermes_pptx_picture_builder.py because pptx_picture_file was referenced but not registered.
* Patched /root/.hermes/scripts/hermes_router_execute.py to register pptx_picture_file.
* Patched telegram_artifact_prerouter.py to use batch executor when multiple output formats are requested.
* Batch executor detects DOCX/PPTX/PDF/HTML/XLSX/MD formats.
* Batch executor preserves negative format instructions.
* Batch executor reuses rich routes:

  * rich_docx_picture_file
  * pptx_picture_file
  * rich_pdf_picture_file

* Batch executor creates, verifies, media-verifies, and delivers every requested artifact.

No private route activated.
No default model changed.
