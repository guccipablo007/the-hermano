
# Phase 6Y-G: AI Image Provider Adapter

Problem:
Local cartoon scenes are still flat vector-style graphics, not beautiful 3D images.

Fix:

* Added NewCoin image provider probe.
* Added AI image generator adapter.
* Added visual asset router.
* Added cache directory for AI image assets.
* Added provider route name: newcoin_image.
* Verified NewCoin /images/generations works with gpt-image-1.
* Added honesty rules: do not call local graphics 3D/real images.

Important:
If NewCoin image generation becomes unavailable, Hermes must report AI image provider unavailable instead of pretending.

No private route activated.
No default model changed.
