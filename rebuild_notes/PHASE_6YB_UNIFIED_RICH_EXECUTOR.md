
# Phase 6Y-B: Unified Rich Output Executor

Problem:
Telegram natural DOCX-with-pictures request detected rich_docx_picture_file but planner incorrectly reported it not implemented. Hermes then drifted into baoyu-comic and failed.

Fix:

* Patched hermes_rich_output_plan.py to mark rich_pdf_picture_file and rich_docx_picture_file implemented.
* Created hermes_rich_output_execute.py.
* Updated skills and AGENTS/SOUL to treat router modes as commands, not skills.
* Unified executor now performs plan -> route -> execute -> verify -> media verify -> deliver.

No private route activated.
No default model changed.
