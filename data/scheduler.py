"""APScheduler 调度器封装。"""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from crawlers.news_rss import NewsRSSCrawler
from crawlers.price_history import PriceHistoryRecorder

LOGGER = logging.getLogger(__name__)


class TaskScheduler:
    """管理历史快照和 RSS 抓取的定时任务。"""

    def __init__(self, history_recorder: PriceHistoryRecorder, news_crawler: NewsRSSCrawler) -> None:
        self.history_recorder = history_recorder
        self.news_crawler = news_crawler
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    async def _safe_history_job(self) -> None:
        """包装历史任务异常，防止调度器崩溃。"""
        try:
            await self.history_recorder.run_once()
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("历史快照任务异常: %s", exc)

    async def _safe_news_job(self) -> None:
        """包装新闻任务异常，防止调度器崩溃。"""
        try:
            await self.news_crawler.run_once()
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("新闻抓取任务异常: %s", exc)

    def start(self) -> None:
        """启动定时任务。"""
        self.scheduler.add_job(
            self._safe_history_job,
            trigger=IntervalTrigger(minutes=1),
            id="price_history_job",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._safe_news_job,
            trigger=IntervalTrigger(minutes=15),
            id="news_rss_job",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
        self.scheduler.start()
        LOGGER.info("调度器启动完成")

    def stop(self) -> None:
        """停止调度器。"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            LOGGER.info("调度器已停止")
