# Phase 6Y-H: Activate NewCoin AI Images

Problem:
NewCoin image generation was detected, but builders still used local cartoon scenes by default.

Fix:
- Replaced conservative AI image adapter with active NewCoin image generation call.
- Added OpenAI-compatible response parsing for b64_json/url/image.
- Added caching by label/topic/style/model/size/quality.
- Patched visual asset router with model/size/quality.
- Patched batch executor to choose ai_3d_image when user asks for 3D/beautiful/real/non-vector images.
- Patched rich PDF/DOCX and PPTX builders to honor HERMES_VISUAL_QUALITY_TIER.
- Added max 25 AI images per request guard.
- Tested 3-image AI generation first.
- Tested cache hit.
- Tested full 3D multi-artifact generation.

No private route activated.
No default model changed.
