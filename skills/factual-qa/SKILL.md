# Factual Q&A

Use `/root/.hermes/scripts/hermes_verified_fact.py` for factual questions that are:

- historically disputed
- source-sensitive
- current or recent
- technical benchmark claims
- medical, legal, or financial
- prone to “first ever” ambiguity

Rules:
- Prefer one short clean answer.
- If a fact depends on definitions, answer with the distinction instead of pretending there is one absolute answer.
- Never invent citations, URLs, or “verified” claims.
- If a trusted source cannot be confirmed, say `NOT VERIFIED`.
- Do not leak internal self-correction or repeated debate text.

Examples:
- `python3 /root/.hermes/scripts/hermes_verified_fact.py answer "Who made the first ever electric airplane?" --format friendly`
- `python3 /root/.hermes/scripts/hermes_verified_fact.py answer "Who made the first ever electric air plane?" --format raw`
