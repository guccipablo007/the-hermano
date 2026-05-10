# Phase 6Q: Deterministic Document Routing Enforcement

Problem:
Natural Telegram PDF request drifted into productivity/pandoc/pdfunite/tmp workflow.

Fix:

* Created document-output-router skill.
* Patched productivity skill to delegate document generation when present.
* Updated model-router skill.
* Updated AGENTS.md.
* Updated SOUL.md.
* Added hard rule: PDF/DOCX/MD/HTML outputs must use hermes_router_execute.py modes.
* Blocked pandoc/pdfunite/pdflatex/tmp pipelines by default.

No private_data route activated.
No Hermes default model changed.
