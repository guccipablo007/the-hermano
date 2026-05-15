# News Retriever

Use `/root/.hermes/scripts/hermes_verified_news.py` for any request about latest news, headlines, or briefings.

Rules:
- Always retrieve real articles from the web or approved fixtures.
- Collect `source`, `title`, `published_at`, and `url` for every article you mention.
- Summarize only articles returned by the verifier.
- If a title, source, or URL cannot be verified, say `NOT VERIFIED`.
- Never invent article titles, dates, placeholder links, or “Read Full Report” text.
- Keep links exactly as returned by the verifier.

Examples:
- `python3 /root/.hermes/scripts/hermes_verified_news.py from-query "top international politics news, top 5 AI news, top 5 Premier League news" --format friendly`
- `python3 /root/.hermes/scripts/hermes_verified_news.py verify-headlines "headline one" "headline two" --format friendly`
