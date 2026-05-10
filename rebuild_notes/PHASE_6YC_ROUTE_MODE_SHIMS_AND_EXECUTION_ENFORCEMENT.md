
# Phase 6Y-C: Route-Mode Shims and Execution Enforcement

Problem:
Natural Telegram artifact requests still stopped at planning and attempted skill_view on router mode names.

Fix:

* Added route-mode shim skills.
* Added hermes_rich_output_execute wrapper.
* Strengthened rich-output-router, document-output-router, model-router, AGENTS.md, and SOUL.md.
* Added no prose-only artifact plan rule.
* Regression-tested exact DOCX-with-pictures Telegram request.
* Regression-tested exact PDF-with-pictures request.

Rule:
For natural artifact requests, execute:
`/root/.hermes/scripts/hermes_rich_output_execute.py --request "<exact current user request>"`

Do not merely plan.

No private route activated.
No default model changed.
