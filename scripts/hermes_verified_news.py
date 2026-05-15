#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Iterable, List


def resolve_base() -> Path:
    env_base = os.environ.get("HERMES_BASE", "").strip()
    if env_base:
        return Path(env_base)
    live = Path("/root/.hermes")
    if live.exists():
        return live
    return Path(__file__).resolve().parents[1]


BASE = resolve_base()
FIXTURE_DIR = os.environ.get("HERMES_NEWS_FIXTURE_DIR", "").strip()
PLACEHOLDER_RE = re.compile(r"read full report|placeholder|example\.com|lorem ipsum", re.I)
SOURCE_ALLOW_MISSING = {"ai", "premier-league", "international-politics"}


@dataclass
class Article:
    category: str
    title: str
    source: str
    published_at: str
    url: str
    summary: str

    def verified(self) -> bool:
        return bool(
            self.title.strip()
            and self.source.strip()
            and self.published_at.strip()
            and self.url.startswith(("http://", "https://"))
            and not PLACEHOLDER_RE.search(self.title)
            and not PLACEHOLDER_RE.search(self.url)
        )


def rss_url(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", unescape(clean)).strip()


def load_feed(category: str, query: str) -> bytes:
    if FIXTURE_DIR:
        path = Path(FIXTURE_DIR) / f"{category}.xml"
        if path.exists():
            return path.read_bytes()
    req = urllib.request.Request(
        rss_url(query),
        headers={"User-Agent": "HermesVerifiedNews/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_feed(category: str, payload: bytes, limit: int) -> List[Article]:
    root = ET.fromstring(payload)
    items = root.findall(".//item")
    articles: List[Article] = []
    for item in items[:limit]:
        title_text = strip_html(item.findtext("title", default=""))
        source_text = strip_html(item.findtext("source", default=""))
        link_text = strip_html(item.findtext("link", default=""))
        pub_text = strip_html(item.findtext("pubDate", default=""))
        desc_text = strip_html(item.findtext("description", default=""))
        if not source_text and " - " in title_text:
            title_text, source_text = [part.strip() for part in title_text.rsplit(" - ", 1)]
        try:
            published_at = parsedate_to_datetime(pub_text).isoformat()
        except Exception:
            published_at = pub_text
        summary = desc_text.split(". ")[0].strip() if desc_text else title_text
        articles.append(
            Article(
                category=category,
                title=title_text,
                source=source_text,
                published_at=published_at,
                url=link_text,
                summary=summary,
            )
        )
    return [article for article in articles if article.verified()]


def categories_from_message(message: str) -> List[tuple[str, str, int]]:
    text = message or ""
    low = text.lower()
    found: List[tuple[str, str, int]] = []
    patterns = [
        ("international-politics", "international politics", r"(top\s+(\d+)\s+)?international politics news"),
        ("ai", "artificial intelligence", r"(top\s+(\d+)\s+)?ai news"),
        ("premier-league", "premier league", r"(top\s+(\d+)\s+)?premier league news"),
    ]
    for slug, query, pattern in patterns:
        match = re.search(pattern, low, re.I)
        if match:
            limit = int(match.group(2) or 5)
            found.append((slug, query, limit))
    if not found:
        limit_match = re.search(r"\btop\s+(\d+)\b", low)
        limit = int(limit_match.group(1)) if limit_match else 5
        found.append(("general", text.strip() or "latest news", limit))
    return found


def collect_briefing(message: str) -> dict:
    verified_articles: List[Article] = []
    errors: List[str] = []
    for category, query, limit in categories_from_message(message):
        try:
            payload = load_feed(category, query)
            verified_articles.extend(parse_feed(category, payload, limit))
        except Exception as exc:
            errors.append(f"{category}:{type(exc).__name__}")
    return {
        "verification_status": "VERIFIED" if verified_articles else "NOT VERIFIED",
        "verified_articles": [
            {
                "category": article.category,
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at,
                "url": article.url,
                "summary": article.summary,
            }
            for article in verified_articles
        ],
        "errors": errors,
        "summary": "Verified news briefing created from real web sources." if verified_articles else "No verified articles could be retrieved from credible sources.",
    }


def verify_headlines(headlines: Iterable[str], message: str = "") -> dict:
    pool = collect_briefing(message or "top 5 international politics news, top 5 AI news, top 5 Premier League news")
    known = {normalize(article["title"]): article for article in pool["verified_articles"]}
    matched = []
    not_verified = []
    for title in headlines:
        key = normalize(title)
        if key in known:
            matched.append(known[key])
        else:
            not_verified.append(title)
    return {
        "verification_status": "VERIFIED" if matched and not not_verified else ("NOT VERIFIED" if not_verified else "NOT VERIFIED"),
        "matched": matched,
        "not_verified": not_verified,
        "summary": "Headline verification completed.",
    }


def print_friendly_briefing(data: dict) -> None:
    print(f"VERIFICATION_STATUS={data['verification_status']}")
    print(f"VERIFIED_ARTICLES={len(data['verified_articles'])}")
    print(f"SUMMARY={data['summary']}")
    if data["errors"]:
        print("ERRORS=" + "; ".join(data["errors"]))
    for idx, article in enumerate(data["verified_articles"], 1):
        print(f"{idx}. {article['title']}")
        print(f"   source={article['source']}")
        print(f"   published_at={article['published_at']}")
        print(f"   url={article['url']}")
        print(f"   summary={article['summary']}")
    if not data["verified_articles"]:
        print("NOT VERIFIED")


def print_friendly_verification(data: dict) -> None:
    print(f"VERIFICATION_STATUS={data['verification_status']}")
    for article in data["matched"]:
        print(f"VERIFIED_TITLE={article['title']}")
        print(f"URL={article['url']}")
    for title in data["not_verified"]:
        print(f"NOT VERIFIED: {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verified news retrieval for Hermes.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_query = sub.add_parser("from-query")
    p_query.add_argument("message")
    p_query.add_argument("--format", choices=["friendly", "json"], default="friendly")

    p_verify = sub.add_parser("verify-headlines")
    p_verify.add_argument("headlines", nargs="+")
    p_verify.add_argument("--message", default="")
    p_verify.add_argument("--format", choices=["friendly", "json"], default="friendly")

    args = parser.parse_args()
    if args.cmd == "from-query":
        data = collect_briefing(args.message)
        if args.format == "json":
            print(json.dumps(data, ensure_ascii=False))
        else:
            print_friendly_briefing(data)
        return 0 if data["verified_articles"] else 1

    data = verify_headlines(args.headlines, args.message)
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False))
    else:
        print_friendly_verification(data)
    return 0 if not data["not_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
