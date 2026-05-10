
# Phase 6T-C: PowerPoint Skill Neutralized

Problem:
Natural Telegram PPTX request still selected old powerpoint skill and made a fake/unfinished success claim.

Fix:

* Replaced old powerpoint skill with deterministic delegator only.
* Added /usr/local/bin/hermes_router_execute wrapper.
* Added PPTX no-fake-success rules to AGENTS.md and SOUL.md.
* Verified PPTX creation through full path and wrapper.

No private route activated.
No default model changed.
