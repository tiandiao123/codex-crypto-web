"""RSS 新闻聚合任务。"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import aiohttp
import feedparser

from redis_client import RedisClient

LOGGER = logging.getLogger(__name__)


class NewsRSSCrawler:
    """抓取并聚合加密货币 RSS 新闻。"""

    FEED_URLS = (
        "https://cointelegraph.com/rss",
        "https://coindesk.com/arc/outboundfeeds/rss/",
    )

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis_client = redis_client

    @staticmethod
    def _to_utc_iso(published: str | None) -> str:
        """将发布时间字符串转换为 UTC ISO8601。"""
        if not published:
            return datetime.now(timezone.utc).isoformat()

        try:
            dt = parsedate_to_datetime(published)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:  # noqa: BLE001
            return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_id(url: str, published_at: str) -> str:
        """构建稳定新闻 ID，便于去重。"""
        source = f"{url}|{published_at}"
        return hashlib.sha1(source.encode("utf-8"), usedforsecurity=False).hexdigest()

    async def _fetch_feed(self, session: aiohttp.ClientSession, url: str) -> feedparser.FeedParserDict:
        """使用 aiohttp 拉取 RSS 内容再交给 feedparser 解析。"""
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            response.raise_for_status()
            text = await response.text()
            return feedparser.parse(text)

    async def run_once(self) -> int:
        """执行一次新闻抓取并写入 Redis。"""
        existing_ids = await self.redis_client.get_recent_news_ids(limit=50)
        to_insert: list[dict[str, str]] = []

        async with aiohttp.ClientSession() as session:
            for feed_url in self.FEED_URLS:
                try:
                    parsed = await self._fetch_feed(session, feed_url)
                    source = urlparse(feed_url).netloc

                    for entry in parsed.entries:
                        title = (entry.get("title") or "").strip()
                        article_url = entry.get("link") or ""
                        published_at = self._to_utc_iso(entry.get("published"))
                        item_id = self._build_id(article_url, published_at)

                        if not title or not article_url or item_id in existing_ids:
                            continue

                        existing_ids.add(item_id)
                        to_insert.append(
                            {
                                "id": item_id,
                                "title": title,
                                "source": source,
                                "url": article_url,
                                "publishedAt": published_at,
                            }
                        )
                except Exception as exc:  # noqa: BLE001
                    LOGGER.exception("抓取 RSS 失败 (%s): %s", feed_url, exc)

        inserted = await self.redis_client.push_news(to_insert, max_items=50)
        LOGGER.info("新闻聚合完成，新增 %s 条", inserted)
        return inserted
