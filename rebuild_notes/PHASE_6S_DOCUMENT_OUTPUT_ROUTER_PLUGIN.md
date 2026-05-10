# Phase 6S: Document Output Router Plugin

Problem:
Hermes emitted pseudo function call text for `document-output-router` because it was only a skill, not a real tool.

Fix:
Created and enabled a Hermes plugin:
- /root/.hermes/plugins/document-output-router/

Registered tools:
- document-output-router
- document_output_router

Also patched:
- /root/.hermes/scripts/hermes_document_builder.py with --content-file support

Purpose:
Natural document requests can now call a real tool that creates verified PDF/DOCX/MD/HTML outputs and delivers them to Telegram.

No private route activated.
No NewCoin worker routing changed.
No Hermes default model changed.
