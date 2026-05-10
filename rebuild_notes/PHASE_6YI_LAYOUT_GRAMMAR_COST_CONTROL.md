# Phase 6Y-I: Layout, Grammar, and AI Cost Control

Problem:
AI images worked, but artifact styling/alignment was poor, some images contained unwanted text, grammar needed correction, and token/credit usage was too high.

Fix:
- Added hermes_lesson_phrase_normalizer.py
- Patched batch executor to use AI only when explicitly requested
- Patched AI image prompts to forbid text/labels inside generated images
- Patched PPTX picture layout to consistent 16:9 template
- Patched PDF layout to cleaner two-card pages
- Tested only PPT and PDF as requested
- Verified local cartoon scene remains default
- Verified no AI generation is triggered unless explicit 3D/AI wording is present

No private route activated.
No default model changed.
