# Phase 6Y-F: Visual Asset Quality

Problem:
Files had embedded images, but the images were placeholders, mostly circles with text.

Fix:
- Added hermes_visual_asset_generator.py
- Added hermes_visual_quality_verify.py
- Patched rich DOCX/PDF lesson builder to use local cartoon scene assets
- Patched PPTX picture builder to use local cartoon scene assets
- Added quality tiers:
  - basic_icon
  - local_cartoon_scene
  - ai_cartoon_image
  - ai_3d_image
- Kids lesson pictures now require at least local_cartoon_scene

No private route activated.
No default model changed.
