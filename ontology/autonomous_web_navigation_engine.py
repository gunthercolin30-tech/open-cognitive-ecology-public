"""
AUTONOMOUS_WEB_NAVIGATION_ENGINE

Version 100%:
- navigation multi-pages
- extraction automatique de liens
- stratégie adaptative
- respect des politiques d'accès
- journalisation SQLite
"""

from __future__ import annotations

import re
import sqlite3
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

try:
    from ontology.internet_controlled_gateway import InternetControlledGateway
except Exception:
    InternetControlledGateway = None


class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


class AutonomousWebNavigationEngine:
    USER_AGENT = "OpenCognitiveEcology/3.0"

    def __init__(self, max_pages=5):
        self.max_pages = max(1, int(max_pages))
        self.visited = set()

        root = Path.home() / "open-cognitive-ecology"
        db_dir = root / "web_navigation"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_dir / "navigation_history.sqlite"
        self._initialize_db()

        if InternetControlledGateway is not None:
            self.gateway = InternetControlledGateway(max_queries=100)
        else:
            self.gateway = None

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS navigation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    content_length INTEGER NOT NULL,
                    success INTEGER NOT NULL,
                    visited_utc TEXT NOT NULL
                )
                """
            )

    def _log_visit(self, url, content_length, success):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO navigation_history
                (url, content_length, success, visited_utc)
                VALUES (?, ?, ?, ?)
                """,
                (
                    url,
                    int(content_length),
                    1 if success else 0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def _authorize(self, url):
        if self.gateway is None:
            return True

        domain = urllib.parse.urlparse(url).netloc
        event = self.gateway.register_query(domain, url)
        return bool(event.get("authorized", False))

    def fetch(self, url):
        if not self._authorize(url):
            raise PermissionError(f"Access denied: {url}")

        if sync_playwright is not None:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    content = page.content()
                    browser.close()
                    self._log_visit(url, len(content), True)
                    return content
            except Exception:
                pass

        request = urllib.request.Request(
            url,
            headers={"User-Agent": self.USER_AGENT},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8", errors="ignore")

        self._log_visit(url, len(content), True)
        return content

    def extract_text(self, html):
        text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_links(self, html, base_url):
        parser = _LinkExtractor()
        parser.feed(html)

        links = []
        for href in parser.links:
            absolute = urllib.parse.urljoin(base_url, href)
            parsed = urllib.parse.urlparse(absolute)
            if parsed.scheme in ("http", "https"):
                links.append(absolute)

        # Déduplication en conservant l'ordre
        seen = set()
        unique = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique.append(link)
        return unique

    def _score_link(self, link):
        parsed = urllib.parse.urlparse(link)
        score = 1.0
        if parsed.netloc.endswith("wikipedia.org"):
            score += 1.0
        if "wiki" in parsed.path.lower():
            score += 0.5
        if len(link) < 120:
            score += 0.2
        return score

    def select_next_links(self, links):
        ranked = sorted(links, key=self._score_link, reverse=True)
        return ranked[: self.max_pages]

    def fetch_text(self, url):
        return self.extract_text(self.fetch(url))

    def crawl(self, start_url):
        self.visited = set()
        queue = [start_url]
        pages = []

        while queue and len(pages) < self.max_pages:
            url = queue.pop(0)

            if url in self.visited:
                continue
            self.visited.add(url)

            try:
                html = self.fetch(url)
            except Exception:
                continue

            text = self.extract_text(html)
            links = self.extract_links(html, url)

            pages.append({
                "url": url,
                "text_length": len(text),
                "link_count": len(links),
            })

            for link in self.select_next_links(links):
                if link not in self.visited and link not in queue:
                    queue.append(link)

        return pages

    def step(self, inputs=None):
        inputs = inputs or {}
        url = inputs.get("url", "https://www.wikipedia.org")
        pages = self.crawl(url)

        total_text_length = sum(page["text_length"] for page in pages)

        return {
            "primitive": "AUTONOMOUS_WEB_NAVIGATION_ENGINE",
            "start_url": url,
            "pages_visited": len(pages),
            "total_text_length": total_text_length,
            "success": len(pages) > 0,
            "database_path": str(self.db_path),
            "pages": pages,
        }
