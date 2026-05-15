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
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Iterable


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
DEBUG_RE = re.compile(r"\b(raw|debug|json)\b", re.I)
URL_CACHE: dict[str, str] = {}

CATEGORY_CONFIG: dict[str, dict[str, object]] = {
    "international-politics": {
        "label": "International Politics",
        "query": "international politics Reuters OR AP OR BBC OR Al Jazeera OR Financial Times OR Guardian OR UN OR EU",
        "trusted_sources": {
            "reuters": 100,
            "associated press": 98,
            "ap": 98,
            "bbc": 94,
            "al jazeera": 92,
            "financial times": 92,
            "the guardian": 90,
            "guardian": 90,
            "un": 96,
            "un news": 96,
            "european union": 90,
            "eu": 90,
            "cfr": 88,
        },
    },
    "ai": {
        "label": "AI News",
        "query": "AI OpenAI OR Anthropic OR DeepMind OR NVIDIA OR Microsoft OR Reuters OR TechCrunch OR The Verge OR MIT Technology Review",
        "trusted_sources": {
            "openai": 100,
            "google deepmind": 99,
            "deepmind": 99,
            "anthropic": 99,
            "meta ai": 96,
            "microsoft": 96,
            "nvidia": 98,
            "arxiv": 92,
            "nature": 92,
            "science": 92,
            "mit technology review": 90,
            "the verge": 88,
            "techcrunch": 86,
            "reuters": 95,
        },
    },
    "premier-league": {
        "label": "Premier League",
        "query": "Premier League BBC Sport OR Sky Sports OR ESPN OR Guardian OR Athletic OR PremierLeague.com",
        "trusted_sources": {
            "premierleague.com": 100,
            "premier league": 100,
            "bbc sport": 96,
            "bbc": 94,
            "sky sports": 94,
            "espn": 92,
            "the guardian": 90,
            "guardian": 90,
            "the athletic": 92,
            "arsenal.com": 90,
            "chelseafc.com": 90,
            "mancity.com": 90,
            "manutd.com": 90,
            "liverpoolfc.com": 90,
            "tottenhamhotspur.com": 90,
        },
    },
    "general": {
        "label": "Verified News",
        "query": "latest news",
        "trusted_sources": {
            "reuters": 100,
            "associated press": 98,
            "bbc": 94,
        },
    },
}


@dataclass
class Article:
    category: str
    title: str
    source: str
    published_at: str
    url: str
    summary: str
    source_score: int = 0

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


def parse_timestamp(pub_text: str) -> tuple[str, float]:
    try:
        dt = parsedate_to_datetime(pub_text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat(), dt.timestamp()
    except Exception:
        return pub_text, 0.0


def load_feed(category: str, query: str) -> bytes:
    if FIXTURE_DIR:
        path = Path(FIXTURE_DIR) / f"{category}.xml"
        if path.exists():
            return path.read_bytes()
    req = urllib.request.Request(
        rss_url(query),
        headers={"User-Agent": "HermesVerifiedNews/2.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def resolve_direct_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return url
    if "news.google.com" not in url:
        return url
    if url in URL_CACHE:
        return URL_CACHE[url]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HermesVerifiedNews/2.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            final_url = resp.geturl() or url
    except Exception:
        final_url = url
    URL_CACHE[url] = final_url
    return final_url


def source_score(category: str, source: str, url: str, title: str) -> int:
    config = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG["general"])
    trusted = config.get("trusted_sources", {})
    low_source = (source or "").lower().strip()
    score = 25
    for key, weight in trusted.items():
        if key in low_source:
            score = max(score, int(weight))
    domain = urllib.parse.urlparse(url).netloc.lower()
    if "gov" in domain or domain.endswith(".gov"):
        score = max(score, 90)
    if "un.org" in domain:
        score = max(score, 96)
    if "europa.eu" in domain:
        score = max(score, 90)
    if "news.google.com" in domain:
        score -= 10
    low_title = title.lower()
    if category == "ai" and re.search(r"\b(stock|shares|price target|earnings)\b", low_title):
        score -= 18
    if category == "premier-league" and re.search(r"\bblog\b|\bfan\b", low_source):
        score -= 20
    return score


def parse_feed(category: str, payload: bytes, limit: int) -> list[Article]:
    root = ET.fromstring(payload)
    items = root.findall(".//item")
    scan_limit = max(limit * 3, 12)
    articles: list[Article] = []
    for item in items[:scan_limit]:
        title_text = strip_html(item.findtext("title", default=""))
        source_text = strip_html(item.findtext("source", default=""))
        link_text = strip_html(item.findtext("link", default=""))
        pub_text = strip_html(item.findtext("pubDate", default=""))
        desc_text = strip_html(item.findtext("description", default=""))
        if not source_text and " - " in title_text:
            title_text, source_text = [part.strip() for part in title_text.rsplit(" - ", 1)]
        published_at, _ = parse_timestamp(pub_text)
        summary = desc_text.split(". ")[0].strip() if desc_text else title_text
        article = Article(
            category=category,
            title=title_text,
            source=source_text,
            published_at=published_at,
            url=link_text,
            summary=summary,
        )
        article.source_score = source_score(category, article.source, article.url, article.title)
        if article.verified():
            articles.append(article)
    articles.sort(key=lambda article: (article.source_score, article.published_at), reverse=True)
    deduped: list[Article] = []
    seen: set[str] = set()
    for article in articles:
        key = normalize(article.title)
        if not key or key in seen:
            continue
        seen.add(key)
        article.url = resolve_direct_url(article.url)
        article.source_score = source_score(category, article.source, article.url, article.title)
        if article.verified():
            deduped.append(article)
        if len(deduped) >= limit * 2:
            break
    strong = [article for article in deduped if article.source_score >= 60]
    return (strong[:limit] if len(strong) >= limit else deduped[:limit])


def categories_from_message(message: str) -> list[tuple[str, str, int]]:
    text = message or ""
    low = text.lower()
    found: list[tuple[str, str, int]] = []
    patterns = [
        ("international-politics", CATEGORY_CONFIG["international-politics"]["query"], r"(top\s+(\d+)\s+)?international politics news"),
        ("ai", CATEGORY_CONFIG["ai"]["query"], r"(top\s+(\d+)\s+)?ai news"),
        ("premier-league", CATEGORY_CONFIG["premier-league"]["query"], r"(top\s+(\d+)\s+)?premier league news"),
    ]
    for slug, query, pattern in patterns:
        match = re.search(pattern, low, re.I)
        if match:
            limit = int(match.group(2) or 5)
            found.append((slug, str(query), limit))
    if not found:
        limit_match = re.search(r"\btop\s+(\d+)\b", low)
        limit = int(limit_match.group(1)) if limit_match else 5
        found.append(("general", text.strip() or "latest news", limit))
    return found


def collect_briefing(message: str) -> dict[str, object]:
    verified_articles: list[dict[str, object]] = []
    grouped: list[dict[str, object]] = []
    errors: list[str] = []
    for category, query, limit in categories_from_message(message):
        try:
            articles = parse_feed(category, load_feed(category, query), limit)
        except Exception as exc:
            errors.append(f"{category}:{type(exc).__name__}")
            articles = []
        label = str(CATEGORY_CONFIG.get(category, CATEGORY_CONFIG["general"])["label"])
        group_rows = [
            {
                "category": article.category,
                "category_label": label,
                "title": article.title,
                "source": article.source,
                "published_at": article.published_at,
                "url": article.url,
                "summary": article.summary,
                "source_score": article.source_score,
            }
            for article in articles
        ]
        if group_rows:
            grouped.append({"category": category, "label": label, "articles": group_rows})
            verified_articles.extend(group_rows)
    return {
        "verification_status": "VERIFIED" if verified_articles else "NOT VERIFIED",
        "verified_articles": verified_articles,
        "grouped_articles": grouped,
        "errors": errors,
        "summary": "Verified news briefing created from real web sources." if verified_articles else "No verified articles could be retrieved from credible sources.",
    }


def verify_headlines(headlines: Iterable[str], message: str = "") -> dict[str, object]:
    pool = collect_briefing(message or "top 5 international politics news, top 5 AI news, top 5 Premier League news")
    known = {normalize(str(article["title"])): article for article in pool["verified_articles"]}
    matched = []
    not_verified = []
    for title in headlines:
        key = normalize(title)
        if key in known:
            matched.append(known[key])
        else:
            not_verified.append(title)
    return {
        "verification_status": "VERIFIED" if matched and not not_verified else "NOT VERIFIED",
        "matched": matched,
        "not_verified": not_verified,
        "summary": "Headline verification completed.",
    }


def print_friendly_briefing(data: dict[str, object]) -> None:
    verified_articles = list(data["verified_articles"])
    print(f"VERIFICATION_STATUS={data['verification_status']}")
    print(f"VERIFIED_ARTICLES={len(verified_articles)}")
    print(f"SUMMARY={data['summary']}")
    if data["errors"]:
        print("ERRORS=" + "; ".join(data["errors"]))
    for idx, article in enumerate(verified_articles, 1):
        print(f"{idx}. {article['title']}")
        print(f"   category={article['category_label']}")
        print(f"   source={article['source']}")
        print(f"   published_at={article['published_at']}")
        print(f"   url={article['url']}")
        print(f"   summary={article['summary']}")
    if not verified_articles:
        print("NOT VERIFIED")


def print_telegram_briefing(data: dict[str, object]) -> None:
    if data["verification_status"] != "VERIFIED":
        print("NOT VERIFIED")
        print("No credible sourced articles could be verified for that news request.")
        return
    blocks: list[str] = []
    for group in data["grouped_articles"]:
        blocks.append(str(group["label"]))
        for idx, article in enumerate(group["articles"], 1):
            blocks.append(f"{idx}. {article['title']}")
            blocks.append(f"Source: {article['source']}")
            blocks.append(f"Published: {article['published_at']}")
            blocks.append(f"Summary: {article['summary']}")
            blocks.append(f"Link: {article['url']}")
            blocks.append("")
    print("\n".join(blocks).strip())


def print_friendly_verification(data: dict[str, object]) -> None:
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
    p_query.add_argument("--format", choices=["friendly", "json", "telegram", "debug"], default="friendly")

    p_verify = sub.add_parser("verify-headlines")
    p_verify.add_argument("headlines", nargs="+")
    p_verify.add_argument("--message", default="")
    p_verify.add_argument("--format", choices=["friendly", "json"], default="friendly")

    args = parser.parse_args()
    if args.cmd == "from-query":
        data = collect_briefing(args.message)
        if args.format == "json":
            print(json.dumps(data, ensure_ascii=False))
        elif args.format == "telegram":
            print_telegram_briefing(data)
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
