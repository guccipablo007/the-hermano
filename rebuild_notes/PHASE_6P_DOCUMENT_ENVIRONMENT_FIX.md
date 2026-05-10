# Phase 6P: Document Builder Environment Fix

Problem:
Telegram Hermes reported missing docx module during PDF generation.

Fix:
- Document builder now uses lazy imports.
- PDF mode no longer imports docx.
- DOCX mode imports docx only when needed.
- Router executor calls document builder with /usr/bin/python3.

No Hermes default model changed.
No private route activated.
